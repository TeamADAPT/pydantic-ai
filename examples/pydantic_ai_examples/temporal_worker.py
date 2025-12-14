"""Comprehensive Temporal Worker for all workflows."""

import asyncio
import sys
import os

# Add the examples directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'examples'))

import temporalio
from temporalio.worker import Worker

# Import workflows from different modules
from workflows import ResearchWorkflow as SimpleWorkflow, research_activity as simple_activity
from pydantic_ai_examples.deep_research_agent import (
    DeepResearchWorkflow,
    search_activity,
    analysis_activity as deep_analysis_activity,
)


async def main():
    """Start the comprehensive Temporal worker."""
    print("=" * 80)
    print("STARTING TEMPORAL WORKER")
    print("=" * 80)
    print()
    print("Registering workflows and activities:")
    print("  - Simple Research Workflow (for demo)")
    print("  - Deep Research Workflow (with Pydantic AI)")
    print()

    # Create worker with all workflows and activities
    worker = Worker(
        client=await temporalio.client.Client.connect("localhost:7233"),
        task_queue="research-tasks",
        workflows=[SimpleWorkflow, DeepResearchWorkflow],
        activities=[simple_activity, search_activity, deep_analysis_activity],
    )

    print("✓ Worker ready!")
    print("  Task Queue: research-tasks")
    print()
    print("Listening for workflows...")
    print()

    # Run worker
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())

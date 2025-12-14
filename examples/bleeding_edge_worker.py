"""Temporal Worker for Bleeding Edge Research"""

import asyncio
import temporalio
from temporalio.worker import Worker
from temporal_research_workflows_v2 import (
    BleedingEdgeResearchWorkflow,
    BleedingEdgeOrchestrator,
    bleeding_edge_research_activity,
    generate_markdown_report_activity,
)


async def main():
    """Start the Temporal worker for bleeding edge research"""
    print("=" * 80)
    print("🔥 BLEEDING EDGE TEMPORAL RESEARCH WORKER")
    print("=" * 80)
    print()
    print("Registering workflows:")
    print("  - BleedingEdgeResearchWorkflow")
    print("  - BleedingEdgeOrchestrator")
    print()
    print("Registering activities:")
    print("  - bleeding_edge_research_activity (June-Nov 2025)")
    print("  - generate_markdown_report_activity (Markdown)")
    print()
    print("📅 Date Filter: June-November 2025 ONLY")
    print("📄 Output: Markdown (.md)")
    print()

    # Create worker
    worker = Worker(
        client=await temporalio.client.Client.connect("localhost:7233"),
        task_queue="research-tasks",
        workflows=[BleedingEdgeResearchWorkflow, BleedingEdgeOrchestrator],
        activities=[bleeding_edge_research_activity, generate_markdown_report_activity],
    )

    print("✅ Worker ready!")
    print("  Task Queue: research-tasks")
    print()
    print("🔄 Listening for BLEEDING EDGE workflows...")
    print()

    # Run worker
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())

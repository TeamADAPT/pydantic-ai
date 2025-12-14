"""Temporal Worker for registering workflows and activities."""

import asyncio
import temporalio
from temporalio.worker import Worker
from workflows import ResearchWorkflow, research_activity


async def main():
    """Start the Temporal worker."""
    print("Starting Temporal worker...")
    print("Registering workflows and activities...")

    # Create worker
    worker = Worker(
        client=await temporalio.client.Client.connect("localhost:7233"),
        task_queue="research-tasks",
        workflows=[ResearchWorkflow],
        activities=[research_activity],
    )

    print("✓ Worker ready and listening on task queue: research-tasks")
    print()

    # Run worker
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())

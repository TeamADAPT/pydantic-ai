import asyncio
import temporalio
from temporalio.worker import Worker
from bleeding_edge_research_final import (
    BleedingEdgeResearchWorkflow,
    BleedingEdgeOrchestrator,
    bleeding_edge_research_activity,
    generate_markdown_report_activity,
)

async def main():
    print("🔥 Starting Bleeding Edge Temporal Worker...")
    worker = Worker(
        client=await temporalio.client.Client.connect("localhost:7233"),
        task_queue="research-tasks",
        workflows=[BleedingEdgeResearchWorkflow, BleedingEdgeOrchestrator],
        activities=[bleeding_edge_research_activity, generate_markdown_report_activity],
    )
    print("✅ Worker ready, listening for workflows...")
    await worker.run()

asyncio.run(main())

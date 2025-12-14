"""Workflows and activities for Temporal demo."""

import asyncio
import temporalio
from temporalio import workflow, activity
from datetime import timedelta


@activity.defn
async def research_activity(topic: str) -> str:
    """Simulate a research activity that takes time."""
    print(f"[Activity] Starting research on: {topic}")
    await asyncio.sleep(2)  # Simulate work
    result = f"Research completed for: {topic}"
    print(f"[Activity] {result}")
    return result


@workflow.defn
class ResearchWorkflow:
    """Temporal workflow that is crash-proof."""

    @workflow.run
    async def run(self, topic: str) -> str:
        """Run the research workflow."""
        print(f"[Workflow] Starting research workflow for: {topic}")

        # Execute activity
        result = await workflow.execute_activity(
            research_activity,
            topic,
            start_to_close_timeout=timedelta(seconds=10),
        )

        print(f"[Workflow] Workflow completed: {result}")
        return result

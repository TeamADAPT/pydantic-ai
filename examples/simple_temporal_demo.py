"""Simple demonstration of Temporal's durable execution.

This shows how Temporal can survive crashes and resume execution.
"""

import asyncio
from temporalio.client import Client
from datetime import timedelta


async def main():
    """Run the Temporal workflow."""
    print("=" * 80)
    print("TEMPORAL DURABLE EXECUTION DEMONSTRATION")
    print("=" * 80)
    print()
    print("This demonstrates Temporal's crash-proof execution.")
    print("The workflow will survive process crashes and restarts.")
    print()

    # Connect to Temporal
    print("Connecting to Temporal server at localhost:7233...")
    client = await Client.connect("localhost:7233")
    print("✓ Connected!")
    print()

    # Start workflow
    workflow_id = f"research-workflow-{int(asyncio.get_event_loop().time())}"
    print(f"Starting workflow (ID: {workflow_id})...")
    print()

    handle = await client.start_workflow(
        "ResearchWorkflow",
        "Quantum Computing and Cryptography",
        id=workflow_id,
        task_queue="research-tasks",
    )

    print("Workflow started! Waiting for result...")
    result = await handle.result()

    print()
    print("=" * 80)
    print("RESULT:")
    print("=" * 80)
    print(result)
    print()
    print("=" * 80)
    print("✓ Workflow completed successfully!")
    print("=" * 80)
    print()
    print("💡 To test durability:")
    print("1. This workflow is persisted in Temporal")
    print("2. If the process crashed, you could reconnect with:")
    print(f"   handle = await client.get_workflow_handle('{workflow_id}')")
    print("   result = await handle.result()")
    print("3. Temporal would replay the workflow and continue from where it left off!")


if __name__ == "__main__":
    asyncio.run(main())

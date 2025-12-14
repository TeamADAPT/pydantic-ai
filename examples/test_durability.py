"""Test Temporal's durability by recovering a workflow."""

import asyncio
from temporalio.client import Client


async def recover_workflow(workflow_id: str):
    """Recover and complete a workflow that was started earlier."""
    print("=" * 80)
    print("TEMPORAL DURABILITY TEST")
    print("=" * 80)
    print()
    print(f"Attempting to recover workflow: {workflow_id}")
    print()

    # Connect to Temporal
    client = await Client.connect("localhost:7233")

    # Get the workflow handle
    handle = client.get_workflow_handle(workflow_id)

    # Check status
    print(f"Workflow status: {handle.describe().status}")

    # Wait for result (Temporal will resume if not complete)
    print("Waiting for workflow to complete...")
    result = await handle.result()

    print()
    print("=" * 80)
    print("RECOVERED RESULT:")
    print("=" * 80)
    print(result)
    print()
    print("✓ Workflow successfully recovered and completed!")


async def list_workflows():
    """List recent workflows."""
    client = await Client.connect("localhost:7233")

    print("Recent workflows:")
    async for workflow in client.list_workflows(limit=5):
        print(f"  - ID: {workflow.id}")
        print(f"    Status: {workflow.status}")
        print(f"    Type: {workflow.type}")
        print(f"    Started: {workflow.start_time}")
        print()


async def main():
    """Main function."""
    # List workflows
    await list_workflows()

    # Recover the most recent workflow
    import sys
    if len(sys.argv) > 1:
        workflow_id = sys.argv[1]
    else:
        workflow_id = "research-workflow-17110"

    await recover_workflow(workflow_id)


if __name__ == "__main__":
    asyncio.run(main())

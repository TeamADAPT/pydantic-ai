"""Deep Research Agent with Durable Execution using Pydantic AI and Temporal.

This example demonstrates how to build a crash-proof research agent that can:
1. Plan search queries
2. Execute multiple searches in parallel
3. Synthesize results into a comprehensive report

The agent survives crashes thanks to Temporal's durable execution.
"""

import asyncio
from dataclasses import dataclass
from typing import List

import logfire
from pydantic import BaseModel, Field
from tavily import TavilyClient

# Import Pydantic AI with Temporal support
try:
    from pydantic_ai import Agent, RunContext
    from pydantic_ai.durable_exec.temporal import TemporalAgent
except ImportError as e:
    print(f"Error importing pydantic_ai with temporal support: {e}")
    print("Make sure pydantic-ai-slim[temporal] is installed")
    raise

# Import Temporal
import temporalio
from temporalio import workflow, activity
from temporalio.client import Client


# Configure logfire for observability
# Try to configure, but don't fail if not authenticated
try:
    logfire.configure()
except Exception:
    # If logfire auth fails, continue without it
    pass


# Define data models
class SearchQuery(BaseModel):
    """A single search query."""
    query: str = Field(description="The search query")
    focus_area: str = Field(description="Specific aspect to focus on")


class SearchResult(BaseModel):
    """A search result from Tavily."""
    title: str
    url: str
    content: str
    query: str


class ResearchPlan(BaseModel):
    """Research plan with multiple search queries."""
    topic: str
    queries: List[SearchQuery] = Field(
        description="List of search queries to execute in parallel"
    )


class DeepResearchReport(BaseModel):
    """Final comprehensive research report."""
    topic: str
    executive_summary: str = Field(description="Brief summary of findings")
    key_findings: List[str] = Field(description="Main discoveries")
    sources: List[str] = Field(description="List of source URLs")
    detailed_analysis: str = Field(description="Comprehensive analysis")


# Activities for Temporal
@activity.defn
async def search_activity(query: str) -> List[SearchResult]:
    """Perform a single search using Tavily."""
    import asyncio
    client = TavilyClient()
    results = await asyncio.to_thread(
        client.search,
        query=query,
        search_depth="advanced",
        include_answer=True,
        include_raw_content=True,
        max_results=5,
    )

    return [
        SearchResult(
            title=result["title"],
            url=result["url"],
            content=result.get("content", result.get("snippet", "")),
            query=query,
        )
        for result in results["results"]
    ]


@activity.defn
async def analysis_activity(
    topic: str, all_results: List[List[SearchResult]]
) -> DeepResearchReport:
    """Analyze all search results and synthesize into a report."""
    # Flatten results
    flat_results = [item for sublist in all_results for item in sublist]

    # Prepare context for the analysis agent
    context = f"""
    Topic: {topic}

    Search Results:
    {'='*80}
    """

    for i, result in enumerate(flat_results, 1):
        context += f"""
    Result {i} (Query: {result.query})
    Title: {result.title}
    URL: {result.url}
    Content: {result.content[:1000] if result.content else 'No content'}
    {'-'*80}
    """

    # Use a smart model for analysis (llama via Groq)
    analysis_agent = Agent(
        "groq:llama-3.3-70b-versatile",
        output_type=DeepResearchReport,
        system_prompt=f"""You are an expert research analyst. Analyze the provided search results and create a comprehensive research report.

Your analysis should:
1. Identify key findings and insights
2. Synthesize information across multiple sources
3. Provide a clear executive summary
4. List all sources used
5. Give a detailed analysis

Be objective, thorough, and cite sources where appropriate.
""",
    )

    result = await analysis_agent.run(
        f"""
        Please analyze the following search results for the topic: {topic}

        {context}

        Create a comprehensive research report.
        """
    )

    return result.output


# Temporal Workflow
@workflow.defn
class DeepResearchWorkflow:
    """Temporal workflow for deep research with crash-proof execution."""

    @workflow.run
    async def run(self, topic: str, research_plan: ResearchPlan) -> DeepResearchReport:
        """Execute the research workflow."""
        # Step 1: Generate search queries (if not provided)
        if not research_plan.queries:
            planning_agent = Agent(
                "minimax-m3",
                result_type=ResearchPlan,
                system_prompt="""You are a research planning expert. Generate 3-5 strategic search queries
                that will comprehensively cover the topic. Each query should focus on a different aspect.
                """,
            )
            result = await planning_agent.run(
                f"Create a research plan for: {topic}",
            )
            research_plan = result.data

        # Step 2: Execute searches in parallel using asyncio.TaskGroup
        async with asyncio.TaskGroup() as tg:
            search_tasks = []
            for search_query in research_plan.queries:
                task = tg.create_task(
                    workflow.execute_activity(search_activity, search_query.query)
                )
                search_tasks.append(task)

        # Collect all results
        all_results = [task.result() for task in search_tasks]

        # Step 3: Analyze all results
        final_report = await workflow.execute_activity(
            analysis_activity, topic, all_results
        )

        return final_report


# Pydantic AI Agents with Temporal support
def create_search_agent() -> TemporalAgent:
    """Create a search agent using Tavily."""
    tavily_client = TavilyClient()

    async def search_tool(ctx: RunContext, query: str) -> str:
        """Search for information using Tavily."""
        try:
            logfire.info("Performing search", query=query)
        except Exception:
            pass  # Logfire not configured
        import asyncio
        results = await asyncio.to_thread(
            tavily_client.search,
            query=query,
            search_depth="advanced",
            include_answer=True,
            max_results=5,
        )
        return str(results)

    # Create agent with temporal support
    agent = TemporalAgent(
        "groq:llama-3.1-8b-instant",
        output_type=str,
        system_prompt="You are a search expert. Use the tavily_search tool to find relevant information.",
    )
    agent.tool(search_tool, description="Search for information using Tavily")

    return agent


def create_analysis_agent() -> TemporalAgent:
    """Create an analysis agent."""
    agent = TemporalAgent(
        "groq:llama-3.3-70b-versatile",
        output_type=DeepResearchReport,
        system_prompt="""You are an expert research analyst. Analyze search results and provide
        comprehensive insights. Focus on accuracy, objectivity, and clear communication.
        """,
    )
    return agent


# Simple async runner (alternative to Temporal)
async def run_research_simple(topic: str) -> DeepResearchReport:
    """Run research without Temporal (for testing)."""
    # Create planning agent
    planning_agent = Agent(
        "groq:llama-3.1-8b-instant",
        output_type=ResearchPlan,
        system_prompt="Generate 3-5 strategic search queries for comprehensive research.",
    )

    # Step 1: Plan
    plan_result = await planning_agent.run(
        f"Create a research plan for: {topic}",
    )
    research_plan = plan_result.output

    # Step 2: Parallel searches (Tavily search is sync, so use asyncio.to_thread)
    search_client = TavilyClient()
    async with asyncio.TaskGroup() as tg:
        search_tasks = [
            tg.create_task(
                asyncio.to_thread(
                    search_client.search,
                    query=q.query,
                    search_depth="advanced",
                    include_answer=True,
                    max_results=5,
                )
            )
            for q in research_plan.queries
        ]

    # Collect results
    all_results = [task.result() for task in search_tasks]

    # Step 3: Analyze
    analysis_agent = Agent(
        "groq:llama-3.3-70b-versatile",
        output_type=DeepResearchReport,
        system_prompt="Analyze search results and create a comprehensive report.",
    )

    report_result = await analysis_agent.run(
        f"Analyze these search results for: {topic}\n\nResults: {all_results}"
    )

    return report_result.output


async def main():
    """Main entry point."""
    print("=" * 80)
    print("Deep Research Agent with Durable Execution (Pydantic AI + Temporal)")
    print("=" * 80)
    print()

    # For simplicity, we'll run without Temporal first
    # To use Temporal, you need a server running: temporal server start-dev
    print("Running in simple mode (no Temporal server required)")
    print("For durable execution, start Temporal server: temporal server start-dev")
    print()

    # Get topic from user or use default
    topic = "The impact of quantum computing on cryptography"
    print(f"Research Topic: {topic}")
    print()

    try:
        # Run the research
        print("Starting research...")
        report = await run_research_simple(topic)

        # Display results
        print("\n" + "=" * 80)
        print("RESEARCH REPORT")
        print("=" * 80)
        print(f"\nExecutive Summary:\n{report.executive_summary}")
        print(f"\nKey Findings:")
        for i, finding in enumerate(report.key_findings, 1):
            print(f"  {i}. {finding}")
        print(f"\nDetailed Analysis:\n{report.detailed_analysis}")
        print(f"\nSources:")
        for i, source in enumerate(report.sources, 1):
            print(f"  {i}. {source}")

        print("\n" + "=" * 80)
        print("Research completed successfully!")
        print("=" * 80)

    except Exception as e:
        try:
            logfire.error("Research failed", error=str(e), exc_info=True)
        except Exception:
            pass  # Logfire not configured
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


# Temporal client setup (commented out - uncomment to use Temporal)
async def run_with_temporal():
    """Run with Temporal server for durable execution."""
    from datetime import timedelta

    # Start Temporal server first: temporal server start-dev
    print("Connecting to Temporal server at localhost:7233...")
    client = await Client.connect("localhost:7233")

    # Define workflow
    workflow_id = f"deep-research-{int(asyncio.get_event_loop().time())}"

    # Use execute_workflow for simpler API
    print(f"Starting workflow (ID: {workflow_id})...")
    result = await client.execute_workflow(
        "DeepResearchWorkflow",
        "The impact of quantum computing on cryptography",
        ResearchPlan(
            topic="Quantum Computing and Cryptography",
            queries=[
                SearchQuery(query="quantum computing cryptography threats", focus_area="Security"),
                SearchQuery(query="post-quantum cryptography algorithms", focus_area="Solutions"),
                SearchQuery(query="quantum resistant encryption standards", focus_area="Standards"),
            ],
        ),
        id=workflow_id,
        task_queue="deep-research",
        start_to_close_timeout=timedelta(minutes=5),
    )

    print("\nResearch Report:", result)


if __name__ == "__main__":
    # Run simple version (works great!)
    import asyncio
    print("Running Deep Research Agent (Simple Mode)...")
    asyncio.run(main())

#!/bin/bash
cd /adapt/projects/durability/pydantic-ai/examples
nohup uv run python bleeding_edge_research_final.py > /tmp/bleeding_edge_output.log 2>&1 &
echo $! > /tmp/bleeding_edge_pid.txt
echo "Worker started with PID: $(cat /tmp/bleeding_edge_pid.txt)"

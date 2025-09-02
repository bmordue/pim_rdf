#!/usr/bin/env python3
"""Utility to run a SPARQL query against a Turtle data file (default: build/merged.ttl).

Usage examples:
  ./util/run_query.py queries/user/open_tasks_by_priority.sparql
  ./util/run_query.py -q queries/user/dashboard.sparql -d build/merged.ttl

Requirements: rdflib (pip3 install rdflib)
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

try:
    import rdflib
except Exception as e:
    print("Error: rdflib is required. Install with: pip3 install rdflib", file=sys.stderr)
    raise


def run_query(query_path: Path, data_path: Path) -> int:
    """Run a SPARQL query from query_path against data_path and print results.

    Returns exit code 0 on success, non-zero on failure.
    """
    if not query_path.exists():
        print(f"Query file not found: {query_path}", file=sys.stderr)
        return 2
    if not data_path.exists():
        print(f"Data file not found: {data_path}", file=sys.stderr)
        return 3

    g = rdflib.Graph()
    try:
        g.parse(str(data_path), format="turtle")
    except Exception as e:
        print(f"Failed to parse data file '{data_path}': {e}", file=sys.stderr)
        return 4

    try:
        query_text = query_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Failed to read query file '{query_path}': {e}", file=sys.stderr)
        return 5

    try:
        results = g.query(query_text)
    except Exception as e:
        print(f"SPARQL query execution failed: {e}", file=sys.stderr)
        return 6

    # Print headers if available
    if hasattr(results, "vars") and results.vars:
        header = [str(v) for v in results.vars]
        print("\t".join(header))
    count = 0
    for row in results:
        # row may be a rdflib.term or a tuple
        if isinstance(row, (list, tuple)):
            print("\t".join(str(item) if item is not None else "" for item in row))
        else:
            print(row)
        count += 1

    print(f"\n{count} result(s)")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Run a SPARQL query against a Turtle data file.")
    p.add_argument("query", nargs="?", help="Path to SPARQL query file (.sparql)", default="queries/user/open_tasks_by_priority.sparql")
    p.add_argument("-d", "--data", help="Path to Turtle data file", default="build/merged.ttl")
    args = p.parse_args(argv)

    query_path = Path(args.query)
    data_path = Path(args.data)

    return run_query(query_path, data_path)


if __name__ == "__main__":
    raise SystemExit(main())

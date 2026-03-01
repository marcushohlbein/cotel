import click
from pathlib import Path
from repo_intel.core.config import Config, get_config
from repo_intel.core.indexer import Indexer
from repo_intel.core.storage import Storage


@click.group()
def main():
    """repo-intel: Local-first structural intelligence for code repositories."""
    pass


@main.command()
@click.option("--project", default="default", help="Project name")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed progress")
def index(project, verbose):
    """Index the repository."""
    config = get_config()
    db_path = Path(config.project_root) / config.db_path

    if verbose:
        click.echo(f"Indexing project: {config.project_root}")

    indexer = Indexer(str(db_path), verbose=verbose)
    indexed = indexer.index_project(config.project_root, project, verbose=verbose)

    click.echo(f"\n✅ Indexed {indexed} files")


@main.command()
def stdio():
    """Start stdio protocol for tool integration."""
    click.echo("Stdio mode not yet implemented")


@main.command()
@click.argument("tool_name")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.option("--kind", "kind_filter", help="Filter symbols by kind")
@click.option("--name", "symbol_name", help="Symbol name for find-symbol")
@click.option("--no-auto-index", is_flag=True, help="Disable auto-indexing")
def tool(tool_name, output_json, kind_filter, symbol_name, no_auto_index):
    """Run a specific tool."""
    import json
    from repo_intel.core.config import get_config
    from repo_intel.core.storage import Storage
    from repo_intel.core.indexer import Indexer
    from repo_intel.tools.list_symbols import list_symbols
    from repo_intel.tools.find_symbol import find_symbol
    from repo_intel.tools.call_graph import get_callers, get_callees

    config = get_config()
    db_path = Path(config.project_root) / config.db_path
    storage = Storage(str(db_path))

    # Auto-index if stale (unless disabled)
    if not no_auto_index and storage.is_index_stale(config.project_root):
        click.echo("🔄 Index stale, auto-reindexing...", err=True)
        indexer = Indexer(str(db_path), verbose=False)
        indexer.index_project(config.project_root, "default", verbose=False)
        click.echo("✅ Reindex complete", err=True)

    tools = {
        "list-symbols": lambda: list_symbols(storage, kind_filter),
        "find-symbol": lambda: find_symbol(storage, symbol_name) if symbol_name else None,
        "get-callers": lambda: get_callers(storage, symbol_name) if symbol_name else None,
        "get-callees": lambda: get_callees(storage, symbol_name) if symbol_name else None,
    }

    if tool_name not in tools:
        click.echo(f"Unknown tool: {tool_name}")
        click.echo(f"Available tools: {', '.join(tools.keys())}")
        return

    result = tools[tool_name]()

    if result is None:
        click.echo("Error: This tool requires additional parameters")
        return

    if output_json:
        click.echo(json.dumps(result, indent=2))
    else:
        if isinstance(result, list):
            for item in result:
                click.echo(item)
        elif isinstance(result, dict):
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(result)


if __name__ == "__main__":
    main()

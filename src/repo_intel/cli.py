import click
from pathlib import Path
from repo_intel.core.config import Config, get_config
from repo_intel.core.indexer import Indexer
from repo_intel.core.storage import Storage
from repo_intel.core.constants import (
    TOOL_LIST_SYMBOLS,
    TOOL_FIND_SYMBOL,
    TOOL_GET_CALLERS,
    TOOL_GET_CALLEES,
)


@click.group()
def main():
    """repo-intel: Local-first structural intelligence for code repositories."""
    pass


@main.command()
@click.option("--project", default="default", help="Project name")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed progress")
@click.option("--chunk-size", default=200, help="Files per chunk (default: 200)")
def index(project, verbose, chunk_size):
    """Index the repository."""
    config = get_config()
    db_path = Path(config.project_root) / config.db_path

    indexer = Indexer(str(db_path), verbose=verbose)
    result = indexer.index_project(config.project_root, project, chunk_size=chunk_size)

    # Print summary
    click.echo("\n" + "=" * 60)
    click.echo("📊 INDEXING SUMMARY")
    click.echo("=" * 60)
    click.echo(f"Total files:      {result.total_files}")
    click.echo(
        f"✅ Indexed:       {result.indexed} ({result.indexed / result.total_files * 100:.1f}%)"
    )
    click.echo(
        f"⏭️  Skipped:       {result.skipped} ({result.skipped / result.total_files * 100:.1f}%)"
    )

    if result.failed > 0:
        click.secho(
            f"❌ Failed:         {result.failed} ({result.failed / result.total_files * 100:.1f}%)",
            fg="red",
        )
    else:
        click.echo(f"❌ Failed:         0")

    click.echo(f"\nTotal symbols:    {result.total_symbols}")
    click.echo(f"Duration:         {result.duration:.2f}s")
    click.echo(f"Success rate:     {result.success_rate:.1f}%")

    if result.languages:
        click.echo("\nLanguages:")
        for lang, count in sorted(result.languages.items(), key=lambda x: x[1], reverse=True):
            click.echo(f"  {lang}: {count}")

    if result.failed_files:
        click.secho(f"\n❌ Failed files ({len(result.failed_files)}):", fg="red")
        for failed_file in result.failed_files[:10]:  # Show first 10
            click.secho(f"  - {failed_file}", fg="red")
        if len(result.failed_files) > 10:
            click.secho(f"  ... and {len(result.failed_files) - 10} more", fg="red")

    click.echo("=" * 60)


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
        result = indexer.index_project(config.project_root, "default", chunk_size=100)
        click.echo(
            f"✅ Reindex complete: {result.indexed} files, {result.total_symbols} symbols", err=True
        )

    tools = {
        TOOL_LIST_SYMBOLS: lambda: list_symbols(storage, kind_filter),
        TOOL_FIND_SYMBOL: lambda: find_symbol(storage, symbol_name) if symbol_name else None,
        TOOL_GET_CALLERS: lambda: get_callers(storage, symbol_name) if symbol_name else None,
        TOOL_GET_CALLEES: lambda: get_callees(storage, symbol_name) if symbol_name else None,
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

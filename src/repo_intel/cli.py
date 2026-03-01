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
@click.argument("path", type=click.Path(exists=True), default=".")
def init(path):
    """Initialize repo-intel in a repository."""
    config_dir = Path(path) / ".repo-intel"
    config_dir.mkdir(exist_ok=True)

    config_path = config_dir / "config.json"
    if not config_path.exists():
        config = Config(project_root=str(Path(path).resolve()))
        import json

        with open(config_path, "w") as f:
            json.dump(config.to_dict(), f, indent=2)

    click.echo(f"Initialized repo-intel in {path}")


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
def watch():
    """Watch for changes and reindex."""
    click.echo("Watch mode not yet implemented")


@main.command()
def stdio():
    """Start stdio protocol for tool integration."""
    click.echo("Stdio mode not yet implemented")


@main.command()
@click.argument("tool_name")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.option("--kind", "kind_filter", help="Filter symbols by kind")
@click.option("--name", "symbol_name", help="Symbol name for find-symbol")
def tool(tool_name, output_json, kind_filter, symbol_name):
    """Run a specific tool."""
    import json
    from repo_intel.core.config import get_config
    from repo_intel.core.storage import Storage
    from repo_intel.tools.list_symbols import list_symbols
    from repo_intel.tools.find_symbol import find_symbol
    from repo_intel.tools.call_graph import get_callers, get_callees

    config = get_config()
    db_path = Path(config.project_root) / config.db_path
    storage = Storage(str(db_path))

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

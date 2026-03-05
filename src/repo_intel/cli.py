import click
from pathlib import Path
from repo_intel.core.config import Config, get_config
from repo_intel.core.indexer import Indexer
from repo_intel.core.storage import Storage
from repo_intel.core.repomap_generator import RepoMapGenerator
from repo_intel.core.constants import (
    TOOL_LIST_SYMBOLS,
    TOOL_FIND_SYMBOL,
    TOOL_GET_CALLERS,
    TOOL_GET_CALLEES,
)


@click.group(invoke_without_command=True)
@click.option("--max-tokens", default=1024, help="Maximum token budget")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON instead of TOON")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.pass_context
def cli(ctx, max_tokens, output_json, verbose):
    """
    Generate repository map for AI coding assistants.

    Default action: Generate repomap (auto-indexes if needed)

    Subcommands: list, find, callers, callees, index
    """
    ctx.ensure_object(dict)
    ctx.obj["max_tokens"] = max_tokens
    ctx.obj["output_json"] = output_json
    ctx.obj["verbose"] = verbose

    if ctx.invoked_subcommand is None:
        # Default: generate repomap
        return _generate_repomap(ctx)


def _generate_repomap(ctx):
    """Generate repomap"""
    config = get_config()
    repo_root = config.project_root
    db_path = Path(repo_root) / config.db_path

    # Auto-index if needed
    if not db_path.exists():
        if ctx.obj["verbose"]:
            click.echo("Indexing repository...")
        storage = Storage(str(db_path))
        indexer = Indexer(str(db_path), verbose=ctx.obj["verbose"])
        indexer.index_project(repo_root, "default")
    else:
        storage = Storage(str(db_path))

    # Generate repomap
    generator = RepoMapGenerator(storage, str(repo_root))

    output_format = "json" if ctx.obj["output_json"] else "toon"
    repomap = generator.generate(max_tokens=ctx.obj["max_tokens"], output_format=output_format)

    click.echo(repomap)


@cli.command("list")
@click.option("--type", "symbol_type", help="Filter by symbol type (function, class, method, etc.)")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.pass_context
def list_symbols(ctx, symbol_type, output_json):
    """List all symbols"""
    import json
    from repo_intel.core.config import get_config
    from repo_intel.core.storage import Storage
    from repo_intel.tools.list_symbols import list_symbols as do_list

    config = get_config()
    db_path = Path(config.project_root) / config.db_path
    storage = Storage(str(db_path))

    result = do_list(storage, symbol_type)

    if output_json:
        click.echo(json.dumps(result, indent=2))
    else:
        for item in result:
            click.echo(item)


@cli.command("find")
@click.option("--name", required=True, help="Symbol name to find")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.pass_context
def find_symbol(ctx, name, output_json):
    """Find a specific symbol"""
    import json
    from repo_intel.core.config import get_config
    from repo_intel.core.storage import Storage
    from repo_intel.tools.find_symbol import find_symbol as do_find

    config = get_config()
    db_path = Path(config.project_root) / config.db_path
    storage = Storage(str(db_path))

    result = do_find(storage, name)

    if output_json:
        click.echo(json.dumps(result, indent=2))
    else:
        click.echo(result)


@cli.command("callers")
@click.option("--name", required=True, help="Symbol name")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.pass_context
def get_callers(ctx, name, output_json):
    """Get callers of a symbol"""
    import json
    from repo_intel.core.config import get_config
    from repo_intel.core.storage import Storage
    from repo_intel.tools.call_graph import get_callers as do_get_callers

    config = get_config()
    db_path = Path(config.project_root) / config.db_path
    storage = Storage(str(db_path))

    result = do_get_callers(storage, name)

    if output_json:
        click.echo(json.dumps(result, indent=2))
    else:
        for item in result:
            click.echo(item)


@cli.command("callees")
@click.option("--name", required=True, help="Symbol name")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.pass_context
def get_callees(ctx, name, output_json):
    """Get callees of a symbol"""
    import json
    from repo_intel.core.config import get_config
    from repo_intel.core.storage import Storage
    from repo_intel.tools.call_graph import get_callees as do_get_callees

    config = get_config()
    db_path = Path(config.project_root) / config.db_path
    storage = Storage(str(db_path))

    result = do_get_callees(storage, name)

    if output_json:
        click.echo(json.dumps(result, indent=2))
    else:
        for item in result:
            click.echo(item)


@cli.command("index")
@click.option("--project", default="default", help="Project name")
@click.option("--verbose", "-v", is_flag=True, help="Show progress")
@click.option("--chunk-size", default=200, help="Files per chunk (default: 200)")
@click.pass_context
def index_repo(ctx, project, verbose, chunk_size):
    """Index repository (usually auto-handled)"""
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


# Backward compatibility: keep 'main' as an alias
main = cli


if __name__ == "__main__":
    cli()

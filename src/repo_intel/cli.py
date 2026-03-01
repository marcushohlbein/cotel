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
def index(project):
    """Index the repository."""
    config = get_config()
    db_path = Path(config.project_root) / config.db_path

    indexer = Indexer(str(db_path))
    indexed = indexer.index_project(config.project_root, project)

    click.echo(f"Indexed {indexed} files")


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
def tool(tool_name, output_json):
    """Run a specific tool."""
    click.echo(f"Tool '{tool_name}' not yet implemented")


if __name__ == "__main__":
    main()

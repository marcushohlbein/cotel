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


import click
from pathlib import Path
from repo_intel.core.config import Config, get_config
from repo_intel.core.indexer import Indexer
from repo_intel.core.storage import Storage
import time
from threading import Timer
from watchdog.observers import Observer
from watchdog.events import (
    FileSystemEventHandler,
    FileModifiedEvent,
    FileCreatedEvent,
    FileDeletedEvent,
)


class DebouncedHandler(FileSystemEventHandler):
    """File system event handler with debouncing."""

    def __init__(self, indexer, storage, project, debounce_seconds=0.5):
        super().__init__()
        self.indexer = indexer
        self.storage = storage
        self.project = project
        self.debounce_seconds = debounce_seconds
        self._timer = None
        self._pending_creates = set()
        self._pending_modifies = set()
        self._pending_deletes = set()

    def on_modified(self, event):
        if event.is_directory:
            return
        self._pending_modifies.add(event.src_path)
        self._schedule_process()

    def on_created(self, event):
        if event.is_directory:
            return
        self._pending_creates.add(event.src_path)
        self._schedule_process()

    def on_deleted(self, event):
        if event.is_directory:
            return
        self._pending_deletes.add(event.src_path)
        self._schedule_process()

    def _schedule_process(self):
        """Schedule file processing with debouncing."""
        if self._timer:
            self._timer.cancel()

        self._timer = Timer(self.debounce_seconds, self._process_pending)
        self._timer.start()

    def _process_pending(self):
        """Process all pending files."""
        creates = set(self._pending_creates)
        modifies = set(self._pending_modifies)
        deletes = list(self._pending_deletes)

        self._pending_creates.clear()
        self._pending_modifies.clear()
        self._pending_deletes.clear()

        for file_path in deletes:
            self._delete_file(file_path)

        for file_path in creates.union(modifies):
            self._index_file(file_path)

    def _delete_file(self, file_path):
        """Delete file and its symbols from index."""
        from repo_intel.utils.language_detector import detect_language

        if not detect_language(file_path):
            return

        file_entry = self.storage.get_file_by_path(file_path)
        if file_entry:
            self.storage.delete_symbols_by_file(file_entry.id)
            self.storage.delete_file(file_entry.id)
            click.secho(f"✗ Removed: {file_path}", fg="yellow")

    def _index_file(self, file_path):
        """Index a single file."""
        from repo_intel.utils.language_detector import detect_language

        if not detect_language(file_path):
            return

        if self.indexer.index_file(file_path, self.project):
            click.secho(f"✓ Reindexed: {file_path}", fg="green")


@main.command()
@click.option("--project", default="default", help="Project name")
@click.option("--debounce", default=0.5, help="Debounce seconds (default: 0.5)")
def watch(project, debounce):
    """Watch for file changes and reindex."""
    config = get_config()
    db_path = Path(config.project_root) / config.db_path

    storage = Storage(str(db_path))
    indexer = Indexer(str(db_path), verbose=True)
    event_handler = DebouncedHandler(indexer, storage, project, debounce_seconds=debounce)

    observer = Observer()
    observer.schedule(event_handler, config.project_root, recursive=True)
    observer.start()

    click.echo(f"👁️  Watching {config.project_root} (Ctrl+C to stop)")
    click.echo(f"    Project: {project}")
    click.echo(f"    Debounce: {debounce}s")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        click.echo("\n🛑 Stopping watch mode...")
        observer.stop()

    observer.join()
    click.echo("✅ Watch mode stopped")


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

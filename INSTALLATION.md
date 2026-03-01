# Installation Guide

## The Problem

When you run `pip install -e .`, you might see:

```
error: externally-managed-environment
```

This is because Python 3.11+ on macOS uses "externally managed environments" to prevent breaking system packages.

## Solution 1: Use Virtual Environment (Recommended ✅)

```bash
# The virtual environment already exists in this project
source venv/bin/activate

# Now install
pip install -e .

# Verify
repo-intel --help
```

## Solution 2: Create New Virtual Environment

If the venv doesn't exist or is broken:

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install
pip install -e .
```

## Solution 3: Override System Protection (Not Recommended ⚠️)

If you really want to install system-wide (not recommended):

```bash
pip install -e . --break-system-packages --user
```

## Verify Installation

```bash
# Make sure you're in the venv
source venv/bin/activate

# Check CLI works
repo-intel --help

# Run tests
pytest tests/ -v
```

## Permanent Fix: Always Use Venv

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
# Auto-activate venv when entering directories with venv/
export VENV_ACTIVATED=$(stat -f .venv/bin/activate 2>/dev/null || stat -f venv/bin/activate 2>/dev/null)
if [ "$VENV_ACTIVATED" != "" ]; then
    source venv/bin/activate
fi
```

## Quick Start for repo-intel

```bash
# 1. Enter the project
cd /path/to/repo-intel

# 2. Activate venv
source venv/bin/activate

# 3. Install (if needed)
pip install -e .

# 4. Verify
repo-intel --help

# 5. Test on a project
cd your-project
repo-intel init
repo-intel index --project myproject
repo-intel tool list-symbols --json
```

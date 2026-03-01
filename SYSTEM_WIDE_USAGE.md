# System-Wide Installation Guide

## ✅ Installation Complete!

repo-intel is now installed system-wide at:
```
/Users/marcus/Library/Python/3.14/bin/repo-intel
```

## One-Time Setup

Add to PATH (choose one):

### Option 1: Current Session Only
```bash
export PATH="$HOME/Library/Python/3.14/bin:$PATH"
```

### Option 2: Permanent (Recommended)
```bash
echo 'export PATH="$HOME/Library/Python/3.14/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

## Test It Works

```bash
# From ANY directory now:
cd /tmp/my-project
repo-intel init
repo-intel index --project myproject
repo-intel tool list-symbols --json
```

## Test Right Now

```bash
# Test Java parsing
mkdir -p quick-test && cat > quick-test/Test.java << 'JAVA'
public class Test {
    public void hello() { }
}
JAVA

export PATH="$HOME/Library/Python/3.14/bin:$PATH"
cd quick-test
repo-intel init
repo-intel index --project test
repo-intel tool list-symbols --json
```

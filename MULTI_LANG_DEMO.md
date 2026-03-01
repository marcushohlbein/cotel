# Multi-Language Testing Guide

## Test Each Language

### Java (Spring Boot)

```bash
cd your-java-project
repo-intel init
repo-intel index --project java-app

# List all classes
repo-intel tool list-symbols --kind class --json

# List all endpoints
repo-intel tool list-symbols --kind endpoint --json
```

### Rust

```bash
cd your-rust-project
repo-intel init
repo-intel index --project rust-app

# List public functions
repo-intel tool list-symbols --json | jq '.[] | select(.exported == 1)'

# List structs
repo-intel tool list-symbols --kind class --json
```

### Go

```bash
cd your-go-project
repo-intel init
repo-intel index --project go-app

# List exported functions (capitalized)
repo-intel tool list-symbols --json | jq '.[] | select(.exported == 1)'

# List structs
repo-intel tool list-symbols --kind class --json
```

### PHP (Laravel)

```bash
cd your-laravel-project
repo-intel init
repo-intel index --project laravel-app

# List all controller methods
repo-intel tool list-symbols --kind method --json

# List endpoints (detected from get/post/put/delete prefixes)
repo-intel tool list-symbols --kind endpoint --json
```

## Language-Specific Features

### Java
- ✅ Classes and methods
- ✅ Interfaces
- ✅ Annotations (Spring MVC: @GetMapping, @PostMapping)
- ✅ Inheritance (extends, implements)
- ✅ Import statements

### Rust
- ✅ Functions and methods
- ✅ Structs
- ✅ Traits
- ✅ Public/private (pub keyword)
- ✅ Use statements
- ✅ Impl blocks

### Go
- ✅ Functions
- ✅ Structs
- ✅ Interfaces
- ✅ Exported (capitalized)
- ✅ Import statements
- ✅ Methods (receiver functions)

### PHP
- ✅ Functions and methods
- ✅ Classes
- ✅ Interfaces
- ✅ Namespaces/use statements
- ✅ Laravel-style endpoints (get*, post*, etc.)

## Query Examples

### Find all HTTP endpoints across languages
```bash
repo-intel tool list-symbols --kind endpoint --json | jq '.[] | {name, path, http_method}'
```

### Find all classes
```bash
repo-intel tool list-symbols --kind class --json | jq '.[] | .name'
```

### Find all public functions
```bash
repo-intel tool list-symbols --json | jq '.[] | select(.exported == 1) | .name'
```

### Trace call graphs
```bash
# Find callers of a function
repo-intel tool get-callers --name myFunction --json

# Find what a function calls
repo-intel tool get-callees --name myFunction --json
```

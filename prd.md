1. Product Overview
Product Name

repo-intel

Vision

Provide a local-first, language-agnostic structural intelligence layer over a repository that enables LLM agents to reason about:

Symbols

Call graphs

Dependency graphs

Inheritance graphs

HTTP boundaries

Cross-project monorepos

Without:

Sending full repositories to models

Running a required background daemon

Using embeddings

Being tied to a specific AI vendor

2. Goals (v1)
Functional Goals

Multi-language symbol indexing.

Deterministic call graph generation.

Dependency and inheritance modeling.

HTTP boundary modeling (framework-agnostic).

Incremental reindexing.

Monorepo awareness.

CLI + stdio tool compatibility.

Zero cloud dependencies.

3. Non-Goals (v1)

No embeddings.

No LLM summarization.

No deep framework internals (Angular DI, Spring Security).

No runtime tracing.

No distributed indexing.

No plugin system (yet).

4. Supported Languages (v1)

Via Tree-sitter:

JavaScript

TypeScript

Java

Python

PHP

Rust

Go

Extraction is structural only.

5. System Architecture
5.1 Folder Structure (v1)
repo-intel/
│
├── package.json
├── tsconfig.json
├── README.md
│
├── bin/
│   └── cli.ts                  # Entry CLI (init, index, stdio, tool, watch)
│
├── src/
│
│   ├── core/
│   │   ├── indexer.ts          # Full indexing orchestration
│   │   ├── incremental.ts      # Incremental reindex logic
│   │   ├── project-detector.ts # Monorepo detection
│   │   ├── symbol-extractor.ts # Normalization layer
│   │   ├── graph-builder.ts    # Builds relations
│   │   ├── storage.ts          # SQLite abstraction
│   │   └── config.ts
│   │
│   ├── parsers/
│   │   ├── base.ts             # Parser interface
│   │   ├── js-ts.ts
│   │   ├── java.ts
│   │   ├── python.ts
│   │   ├── php.ts
│   │   ├── rust.ts
│   │   └── go.ts
│   │
│   ├── analysis/
│   │   ├── call-graph.ts
│   │   ├── dependency-graph.ts
│   │   ├── inheritance-graph.ts
│   │   └── http-boundary.ts
│   │
│   ├── tools/
│   │   ├── list-symbols.ts
│   │   ├── find-symbol.ts
│   │   ├── get-definition.ts
│   │   ├── get-callers.ts
│   │   ├── get-callees.ts
│   │   ├── get-dependencies.ts
│   │   ├── get-http-target.ts
│   │   └── search-text.ts
│   │
│   ├── server/
│   │   ├── stdio.ts
│   │   └── protocol.ts
│   │
│   └── utils/
│       ├── file-walker.ts
│       ├── hashing.ts
│       ├── language-detector.ts
│       └── logger.ts
│
└── .repo-intel/
    └── index.db
6. Core Capabilities
6.1 Unified Symbol Model
interface SymbolEntry {
  id: string
  name: string
  kind:
    | 'function'
    | 'class'
    | 'method'
    | 'interface'
    | 'endpoint'
    | 'http_call'

  language: string
  file: string
  project: string

  startLine: number
  endLine: number
  exported: boolean

  httpMethod?: string
  path?: string
}

Note:
project field supports monorepo isolation.

6.2 Incremental Reindexing Engine (Included in v1)
Objective

Avoid full repository reindex on every run.

Functional Requirements

The system SHALL:

Store file hash in database.

Compare current hash with stored hash.

Reindex only changed files.

Remove symbols of deleted files.

Recompute only affected graph edges.

Support repo-intel watch mode.

Design
Hash Strategy

SHA-256 per file.

Stored in files.hash.

Dependency Tracking

When file changes:

Delete its symbols.

Delete relations referencing them.

Recompute only that file’s graph edges.

Performance Target

Reindex single changed file in < 200ms.

No full repo reparse during normal dev cycles.

6.3 Monorepo Awareness (Included in v1)
Objective

Support repositories containing:

Frontend + backend

Multiple services

Multiple languages

Independent modules

Project Detection

The system SHALL detect subprojects by scanning for:

package.json

pnpm-workspace.yaml

pom.xml

go.mod

Cargo.toml

composer.json

requirements.txt

Each detected root becomes a logical project.

Isolation Behavior

Symbols tagged with project.

Queries may filter by project.

HTTP linking may cross projects.

Import linking limited within project unless explicit.

Example
/frontend (Angular)
/backend (Spring)
/shared-lib

Each becomes separate logical scope.

6.4 Call Graph

The system SHALL:

Detect call expressions.

Create calls relations.

Support multi-language traversal.

6.5 Dependency Graph

The system SHALL:

Detect imports/includes.

Store file-to-file dependencies.

Support get_dependencies.

6.6 Inheritance Graph

The system SHALL detect:

extends

implements

interface realization

6.7 HTTP Boundary Modeling (Framework-Agnostic)
Backend Endpoint Detection

Detect common patterns:

Annotation-based mappings (Java)

Decorator-based mappings (TS/Python)

Router method definitions (JS/Go/PHP)

Extract:

httpMethod

path

Create symbol:

kind: 'endpoint'
Outbound HTTP Call Detection

Detect:

fetch()

axios

HttpClient

requests

http.Post

similar patterns

Create symbol:

kind: 'http_call'
HTTP Linking

Match by:

Normalized method

Normalized path

Support path parameters (basic normalization)

Create relation:

relation_type = 'http_match'
7. SQLite Schema (v1)
files
CREATE TABLE files (
  id TEXT PRIMARY KEY,
  path TEXT,
  language TEXT,
  project TEXT,
  hash TEXT
);
symbols
CREATE TABLE symbols (
  id TEXT PRIMARY KEY,
  name TEXT,
  kind TEXT,
  language TEXT,
  file_id TEXT,
  project TEXT,
  start_line INTEGER,
  end_line INTEGER,
  exported INTEGER,
  http_method TEXT,
  path TEXT
);
relations
CREATE TABLE relations (
  id TEXT PRIMARY KEY,
  from_symbol_id TEXT,
  to_symbol_id TEXT,
  relation_type TEXT
);

Relation types:

calls

imports

extends

implements

http_match

8. CLI Requirements
Commands
repo-intel init
repo-intel index
repo-intel watch
repo-intel stdio
repo-intel tool <name> --json
Execution Model

Default:

No daemon.

SQLite persistent.

Stdio tool-compatible.

Optional:

Watch mode for dev usage.

9. Tool API Surface

Must expose:

list_symbols

find_symbol

get_definition

get_callers

get_callees

get_dependencies

get_parents

get_children

get_http_target

search_text

All responses structured JSON.

No narrative responses.

10. Performance Requirements

Full index of 500k LOC in < 30s.

Incremental update in < 200ms per file.

Symbol lookup < 100ms.

11. Installation Requirements

Node 20+

No Docker

No cloud

No background daemon

Install via:

npx repo-intel init
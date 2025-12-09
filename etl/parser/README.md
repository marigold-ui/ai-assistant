# ETL Parser

Parser for Marigold UI documentation (MDX + TSX) with code extraction and AST generation.

## Architecture

### Core Modules

- **fetcher.ts**: Downloads documentation from GitHub repository
- **ast-builder.ts**: Parses MDX files and builds hierarchical section tree
- **fetch_docs.ts**: CLI entry point for documentation fetching
- **generate_ast.ts**: CLI entry point for AST generation

## Usage

### Fetch Documentation

```bash
pnpm fetch
```

Downloads Marigold UI documentation from GitHub to `../../data/raw/`

### Parse and Generate AST

```bash
pnpm parse
```

Parses all MDX files from `../../data/raw/` and generates structured JSON output in `../../data/processed/`

### Run Full Pipeline

```bash
pnpm dev
```

Runs fetch followed by parse.

## Output Structure

Each generated JSON file contains:

```json
{
  "component": "button",
  "metadata": {
    "title": "Button",
    "caption": "Description",
    "badge": "updated"
  },
  "demos": [
    {
      "file": "button-loading.demo.tsx",
      "code": "..."
    }
  ],
  "sections": [
    {
      "title": "Anatomy",
      "level": 2,
      "content": "Description text",
      "images": [
        { "src": "/path/to/image", "alt": "description" }
      ],
      "demos": ["button-loading.demo.tsx"],
      "children": []
    }
  ]
}
```

## Configuration

Modify configuration in each script's CLI entry point:

- **fetch_docs.ts**: Repository URL, docs path, output directory
- **generate_ast.ts**: Raw and output directories

## Dependencies

- `unified`: AST processing framework
- `remark-parse`: Markdown parser
- `remark-mdx`: MDX support
- `remark-gfm`: GitHub-flavored markdown
- `glob`: File pattern matching

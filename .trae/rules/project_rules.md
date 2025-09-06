1. Every time a new library/package is added, search for the latest stable version and use it.  
2. For every new library/package or project created, use context7 MCP for documentation before installation or project setup.  
3. Always use modern Python (latest stable version, e.g., Python 3.12) and its latest features.  
4. Before creating `pyproject.toml` or `requirements.txt`, use context7 MCP for every package added.  
5. When a prompt is given, actually install/check packages, create files, and validate them.  
6. After each task, check files, run `mypy`, `ruff`/`flake8`, and `pytest`, then fix all errors in the same prompt.  
7. All tasks must be completed in the same prompt (no deferring).  
8. If any error is found, fix it immediately in the same prompt.  
9. Use uv for package management.
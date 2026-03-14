# Prompt Log

## AI Tools / Models Used
- ChatGPT (brainstorm, planning, requirements clarification, architecture prompts)
- Codex coding agent in local workspace (implementation, refactoring, debugging, verification)

## Project Scope
- Project name: `Course Catalog`
- Core stack: Python, SQLite (`sqlite3`), Flask, HTML/CSS
- Core requirements covered: CRUD, filter/sort Read queries, local DB, parameterized SQL, clean DB connection handling

## Development Process and Important Prompts

### Stage 1: Architecture and Setup

Important prompts used:
- "I want you to build a small local Python project called 'Course Catalog' using SQLite and a command-line interface (CLI)."
- "Project file structure: app.py, db.py, schema.sql, README.md, prompt_log.md, .gitignore."
- "Initialize the database/table automatically if it does not exist."


### Stage 2: Create (INSERT)

Important prompts used:
- "Next step: Implement Create. Write a function that accepts user input and inserts the record into the table."
- "Use parameterized queries with ? placeholders."
- "Make sure INSERT, UPDATE, and DELETE call commit()."


### Stage 3: Read (View All + Filter/Sort/Search)

Important prompts used:
- "Next, implement the read (SELECT) operations based on the earlier GPT requirements."
- "Read must include at least one query that filters or sorts based on user input."
- "Include submenu options: department, semester, mini course, sort credits, sort fce_hours, keyword search."

### Stage 4: Update and Delete

Important prompts used:
- "Next step is update and delete."


### Stage 5: Major Change to Flask Web App

Important prompts used:
- "Next we need a major change: build a simple web interface with HTML and Flask."
- "The web app should have four abstract functions: create, read, update, delete."
- "Read should be richer: visualize the query/filter logic we implemented."


### Stage 6: UX Iteration and Simplification

Important prompts used:
- "Show confirm/cancel in a small floating block near delete, without changing action-column width."
- "Add a reset-data function to delete all rows and start clean."


### Stage 7: Navigation and Multi-Entry Create

Important prompts used:
- "Create should support importing multiple rows; add an 'Add More Data' option at the bottom."


### Stage 8: Terminal Debug Mode + Documentation

Important prompts used:
- "In README.md, add a local debugging mode similar to CLI that runs directly in terminal instead of web."
- "Also list how to operate data via CLI in README with five examples: create, read (all and filter), update, delete."



## Representative Non-Trivial Prompt Snippets
- "Use parameterized queries with ? placeholders"
- "Initialize the database/table automatically if it does not exist"
- "Read functionality must include at least one query that filters or sorts based on user input"
- "Add reset data: delete all data and restart from clean state"
- "Create should support multiple data entries with add-more form rows"

## Verification and Quality Notes
- Validated syntax with `py -3 -m py_compile` during iterations.
- Performed route and behavior checks with Flask test client.
- Confirmed DB operations commit correctly and connections close in route handlers.
- Verified local run paths:
  - Web app: `py -3 app.py`
  - Terminal debug mode: `py -3 debug_cli.py`

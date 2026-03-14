# Overview

This app tracks university course information such as course number,
department, credits, semester availability, and workload.

I chose this topic because I frequently compare courses when planning
future semesters and wanted a simple tool to organize course data.

## Database Schema

Table: courses

| Column | Type | Description |
|------|------|-------------|
| id | INTEGER PRIMARY KEY AUTOINCREMENT | unique identifier |
| course_number | TEXT | course number (e.g., 36-402) |
| course_name | TEXT | course title |
| department | TEXT | department offering the course |
| credits | INTEGER | number of credits |
| semester_offered | TEXT | semester availability |
| mini_course | TEXT | whether the course is a mini (Y/N) |
| description | TEXT | course description |
| fce_hours | REAL | FCE workload estimate |

# Course Catalog (Flask + SQLite)

A local web app for managing course information with full CRUD:
- Create course
- Read courses (with filter/sort and query visualization)
- Update course
- Delete course

## Tech Stack

- Python
- Flask
- SQLite (`sqlite3`)

## Run Locally

1. Install Flask:

```bash
py -3 -m pip install flask
```

2. Start app:

```bash
py -3 app.py
```

3. Open in browser:

```text
http://127.0.0.1:5000
```

## Terminal Debug Mode (No Web UI)

If you want to debug data quickly in terminal (CLI style), use:

```bash
py -3 debug_cli.py
```

This debug CLI supports:
- create (add one course)
- read all
- read with filter/sort
- update by id
- delete by id
- find by id
- reset all data

Use this when you want to test CRUD data behavior without opening the browser.

## CLI Examples (5)

Run CLI:

```bash
py -3 debug_cli.py
```

Example 1: Create

```text
Choose: 1
Course number: 15-112
Course name: Fundamentals of Programming
Department: SCS
Credits: 10
Semester offered: Fall only
Mini course (Y/N): Y
Description (optional): Intro course
FCE hours (optional): 10.5
```

Example 2: Read All

```text
Choose: 2
```

Example 3: Read with Filter

```text
Choose: 3
Choose filter type: 1
Department: SCS
```

Example 4: Update

```text
Choose: 4
Course id: 1
Course number [15-112] (Enter=keep):
Course name [Fundamentals of Programming] (Enter=keep): FP in Python
...
```

Example 5: Delete

```text
Choose: 5
Course id: 1
Delete this course? (Y/N): Y
```

## Project Structure

- `app.py`: Flask routes and form handling
- `db.py`: database connection + CRUD/query functions
- `debug_cli.py`: terminal-only debug CLI (no web interface)
- `schema.sql`: `courses` table schema
- `templates/`: HTML pages
- `static/styles.css`: basic styling
- `data/courses.db`: local SQLite database (created automatically)

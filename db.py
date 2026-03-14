"""Database setup helpers for the Course Catalog CLI project."""

from pathlib import Path
import sqlite3


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "courses.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"


def connect_db() -> sqlite3.Connection:
    """Create and return a SQLite connection."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_db(connection: sqlite3.Connection) -> None:
    """Create tables from schema.sql if they do not exist."""
    with open(SCHEMA_PATH, "r", encoding="utf-8") as schema_file:
        schema_sql = schema_file.read()
    connection.executescript(schema_sql)
    connection.commit()


def add_course(
    connection: sqlite3.Connection,
    course_number: str,
    course_name: str,
    department: str,
    credits: int,
    semester_offered: str,
    mini_course: str,
    description: str | None,
    fce_hours: float | None,
) -> int:
    """Insert a new course record and return the created row id."""
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT INTO courses (
            course_number, course_name, department, credits,
            semester_offered, mini_course, description, fce_hours
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            course_number,
            course_name,
            department,
            credits,
            semester_offered,
            mini_course,
            description,
            fce_hours,
        ),
    )
    connection.commit()
    return cursor.lastrowid


def get_all_courses(connection: sqlite3.Connection) -> list[sqlite3.Row]:
    """Return all courses ordered by id."""
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM courses ORDER BY id")
    return cursor.fetchall()


def get_courses_by_department(
    connection: sqlite3.Connection, department: str
) -> list[sqlite3.Row]:
    """Filter courses by department."""
    cursor = connection.cursor()
    cursor.execute(
        "SELECT * FROM courses WHERE department = ? ORDER BY id",
        (department,),
    )
    return cursor.fetchall()


def get_courses_by_semester(
    connection: sqlite3.Connection, semester_offered: str
) -> list[sqlite3.Row]:
    """Filter courses by semester offered."""
    cursor = connection.cursor()
    cursor.execute(
        "SELECT * FROM courses WHERE semester_offered = ? ORDER BY id",
        (semester_offered,),
    )
    return cursor.fetchall()


def get_mini_courses(connection: sqlite3.Connection) -> list[sqlite3.Row]:
    """Return courses where mini_course is Y."""
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM courses WHERE mini_course = ? ORDER BY id", ("Y",))
    return cursor.fetchall()


def get_courses_sorted_by_credits(
    connection: sqlite3.Connection, descending: bool = False
) -> list[sqlite3.Row]:
    """Return all courses sorted by credits."""
    cursor = connection.cursor()
    order = "DESC" if descending else "ASC"
    cursor.execute(f"SELECT * FROM courses ORDER BY credits {order}, id ASC")
    return cursor.fetchall()


def get_courses_sorted_by_fce_hours(
    connection: sqlite3.Connection, descending: bool = False
) -> list[sqlite3.Row]:
    """Return all courses sorted by fce_hours."""
    cursor = connection.cursor()
    order = "DESC" if descending else "ASC"
    cursor.execute(
        f"SELECT * FROM courses ORDER BY fce_hours IS NULL, fce_hours {order}, id ASC"
    )
    return cursor.fetchall()


def search_courses_by_description(
    connection: sqlite3.Connection, keyword: str
) -> list[sqlite3.Row]:
    """Search courses with keyword in description (case-insensitive)."""
    cursor = connection.cursor()
    like_term = f"%{keyword}%"
    cursor.execute(
        """
        SELECT * FROM courses
        WHERE description IS NOT NULL
          AND LOWER(description) LIKE LOWER(?)
        ORDER BY id
        """,
        (like_term,),
    )
    return cursor.fetchall()


def get_course_by_id(
    connection: sqlite3.Connection, course_id: int
) -> sqlite3.Row | None:
    """Return one course by id, or None if not found."""
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM courses WHERE id = ?", (course_id,))
    return cursor.fetchone()


def update_course(
    connection: sqlite3.Connection,
    course_id: int,
    course_number: str,
    course_name: str,
    department: str,
    credits: int,
    semester_offered: str,
    mini_course: str,
    description: str | None,
    fce_hours: float | None,
) -> bool:
    """Update one course by id and return True if updated."""
    cursor = connection.cursor()
    cursor.execute(
        """
        UPDATE courses
        SET course_number = ?,
            course_name = ?,
            department = ?,
            credits = ?,
            semester_offered = ?,
            mini_course = ?,
            description = ?,
            fce_hours = ?
        WHERE id = ?
        """,
        (
            course_number,
            course_name,
            department,
            credits,
            semester_offered,
            mini_course,
            description,
            fce_hours,
            course_id,
        ),
    )
    connection.commit()
    return cursor.rowcount > 0


def delete_course(connection: sqlite3.Connection, course_id: int) -> bool:
    """Delete one course by id and return True if deleted."""
    cursor = connection.cursor()
    cursor.execute("DELETE FROM courses WHERE id = ?", (course_id,))
    connection.commit()
    return cursor.rowcount > 0


def query_courses(
    connection: sqlite3.Connection,
    department: str | None = None,
    semester_offered: str | None = None,
    mini_only: bool = False,
    keyword: str | None = None,
    sort_by: str = "id",
    sort_order: str = "asc",
) -> tuple[list[sqlite3.Row], str, tuple]:
    """Run a dynamic read query and return rows + SQL preview + bound params."""
    allowed_sort_columns = {
        "id": "id",
        "credits": "credits",
        "fce_hours": "fce_hours",
    }
    selected_sort = allowed_sort_columns.get(sort_by, "id")
    selected_order = "DESC" if sort_order.lower() == "desc" else "ASC"

    base_sql = "SELECT * FROM courses"
    conditions: list[str] = []
    params: list = []

    if department:
        conditions.append("department = ?")
        params.append(department)
    if semester_offered:
        conditions.append("semester_offered = ?")
        params.append(semester_offered)
    if mini_only:
        conditions.append("mini_course = ?")
        params.append("Y")
    if keyword:
        conditions.append("description IS NOT NULL")
        conditions.append("LOWER(description) LIKE LOWER(?)")
        params.append(f"%{keyword}%")

    where_sql = ""
    if conditions:
        where_sql = " WHERE " + " AND ".join(conditions)

    if selected_sort == "fce_hours":
        order_sql = f" ORDER BY fce_hours IS NULL, fce_hours {selected_order}, id ASC"
    elif selected_sort == "credits":
        order_sql = f" ORDER BY credits {selected_order}, id ASC"
    else:
        order_sql = f" ORDER BY id {selected_order}"

    final_sql = base_sql + where_sql + order_sql
    cursor = connection.cursor()
    cursor.execute(final_sql, tuple(params))
    return cursor.fetchall(), final_sql, tuple(params)


def reset_all_courses(connection: sqlite3.Connection) -> None:
    """Delete all course data and reset AUTOINCREMENT sequence."""
    cursor = connection.cursor()
    cursor.execute("DELETE FROM courses")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name = ?", ("courses",))
    connection.commit()

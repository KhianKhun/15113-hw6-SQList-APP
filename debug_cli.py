"""Terminal debug CLI for Course Catalog (no web UI)."""

from db import (
    add_course,
    connect_db,
    delete_course,
    get_all_courses,
    get_course_by_id,
    initialize_db,
    query_courses,
    reset_all_courses,
    update_course,
)


VALID_SEMESTERS = [
    "Fall only",
    "Spring only",
    "Fall and Spring",
    "Summer only",
    "All semesters",
]


def prompt_non_empty(label: str) -> str:
    while True:
        value = input(label).strip()
        if value:
            return value
        print("Input cannot be empty.")


def prompt_int(label: str) -> int:
    while True:
        try:
            return int(input(label).strip())
        except ValueError:
            print("Please enter an integer.")


def prompt_float_optional(label: str):
    while True:
        raw = input(label).strip()
        if raw == "":
            return None
        try:
            return float(raw)
        except ValueError:
            print("Please enter a number or leave blank.")


def prompt_semester() -> str:
    print("Valid semesters:")
    for s in VALID_SEMESTERS:
        print(f"- {s}")
    while True:
        s = input("Semester offered: ").strip()
        if s in VALID_SEMESTERS:
            return s
        print("Please use one of the options above.")


def prompt_mini() -> str:
    while True:
        val = input("Mini course (Y/N): ").strip().upper()
        if val in {"Y", "N"}:
            return val
        print("Please enter Y or N.")


def print_course(course) -> None:
    if not course:
        print("Course not found.")
        return
    print(
        f"[{course['id']}] {course['course_number']} | {course['course_name']} | "
        f"{course['department']} | {course['credits']} credits | "
        f"{course['semester_offered']} | mini={course['mini_course']} | "
        f"fce={course['fce_hours'] if course['fce_hours'] is not None else 'N/A'}"
    )
    print(f"    desc: {course['description'] if course['description'] else '(none)'}")


def list_courses(connection) -> None:
    rows = get_all_courses(connection)
    print(f"\nTotal: {len(rows)}")
    for row in rows:
        print_course(row)
    print()


def add_course_interactive(connection) -> None:
    print("\nAdd course")
    new_id = add_course(
        connection,
        course_number=prompt_non_empty("Course number: "),
        course_name=prompt_non_empty("Course name: "),
        department=prompt_non_empty("Department: "),
        credits=prompt_int("Credits: "),
        semester_offered=prompt_semester(),
        mini_course=prompt_mini(),
        description=(input("Description (optional): ").strip() or None),
        fce_hours=prompt_float_optional("FCE hours (optional): "),
    )
    print(f"Added course id={new_id}\n")


def read_with_filter(connection) -> None:
    print("\nRead with filter/sort")
    print("1) Department")
    print("2) Semester offered")
    print("3) Mini courses only")
    print("4) Keyword in description")
    print("5) Sort by credits")
    print("6) Sort by fce_hours")
    choice = input("Choose filter type: ").strip()

    kwargs = {
        "department": None,
        "semester_offered": None,
        "mini_only": False,
        "keyword": None,
        "sort_by": "id",
        "sort_order": "asc",
    }

    if choice == "1":
        kwargs["department"] = prompt_non_empty("Department: ")
    elif choice == "2":
        kwargs["semester_offered"] = prompt_semester()
    elif choice == "3":
        kwargs["mini_only"] = True
    elif choice == "4":
        kwargs["keyword"] = prompt_non_empty("Keyword: ")
    elif choice == "5":
        kwargs["sort_by"] = "credits"
        kwargs["sort_order"] = input("Sort order (asc/desc): ").strip().lower() or "asc"
    elif choice == "6":
        kwargs["sort_by"] = "fce_hours"
        kwargs["sort_order"] = input("Sort order (asc/desc): ").strip().lower() or "asc"
    else:
        print("Invalid filter choice.\n")
        return

    rows, sql_preview, params = query_courses(connection, **kwargs)
    print(f"\nSQL: {sql_preview}")
    print(f"Params: {params}")
    print(f"Total: {len(rows)}")
    for row in rows:
        print_course(row)
    print()


def prompt_optional_update(label: str, current: str) -> str:
    raw = input(f"{label} [{current}] (Enter=keep): ").strip()
    return raw if raw else current


def prompt_optional_int_update(label: str, current: int) -> int:
    while True:
        raw = input(f"{label} [{current}] (Enter=keep): ").strip()
        if raw == "":
            return current
        try:
            return int(raw)
        except ValueError:
            print("Please enter an integer or Enter.")


def prompt_optional_float_update(label: str, current):
    shown = "None" if current is None else str(current)
    while True:
        raw = input(f"{label} [{shown}] (Enter=keep, NONE=clear): ").strip()
        if raw == "":
            return current
        if raw.upper() == "NONE":
            return None
        try:
            return float(raw)
        except ValueError:
            print("Please enter a number, NONE, or Enter.")


def update_course_interactive(connection) -> None:
    print("\nUpdate course")
    cid = prompt_int("Course id: ")
    existing = get_course_by_id(connection, cid)
    if existing is None:
        print("Course not found.\n")
        return

    print_course(existing)
    updated = update_course(
        connection,
        course_id=cid,
        course_number=prompt_optional_update("Course number", existing["course_number"]),
        course_name=prompt_optional_update("Course name", existing["course_name"]),
        department=prompt_optional_update("Department", existing["department"]),
        credits=prompt_optional_int_update("Credits", existing["credits"]),
        semester_offered=prompt_optional_update("Semester offered", existing["semester_offered"]),
        mini_course=prompt_optional_update("Mini course (Y/N)", existing["mini_course"]).upper(),
        description=prompt_optional_update(
            "Description",
            existing["description"] if existing["description"] else "",
        )
        or None,
        fce_hours=prompt_optional_float_update("FCE hours", existing["fce_hours"]),
    )
    print("Updated.\n" if updated else "Update failed.\n")


def delete_course_interactive(connection) -> None:
    print("\nDelete course")
    cid = prompt_int("Course id: ")
    existing = get_course_by_id(connection, cid)
    if existing is None:
        print("Course not found.\n")
        return
    print_course(existing)
    confirm = input("Delete this course? (Y/N): ").strip().upper()
    if confirm == "Y":
        ok = delete_course(connection, cid)
        print("Deleted.\n" if ok else "Delete failed.\n")
    else:
        print("Canceled.\n")


def main() -> None:
    connection = connect_db()
    try:
        initialize_db(connection)
        while True:
            print("=== Course Catalog Debug CLI ===")
            print("1) Create: add one course")
            print("2) Read: list all courses")
            print("3) Read: filter/sort courses")
            print("4) Update one course")
            print("5) Delete one course")
            print("6) Find course by id")
            print("7) Reset all data")
            print("0) Exit")
            choice = input("Choose: ").strip()

            if choice == "1":
                add_course_interactive(connection)
            elif choice == "2":
                list_courses(connection)
            elif choice == "3":
                read_with_filter(connection)
            elif choice == "4":
                update_course_interactive(connection)
            elif choice == "5":
                delete_course_interactive(connection)
            elif choice == "6":
                cid = prompt_int("Course id: ")
                print_course(get_course_by_id(connection, cid))
                print()
            elif choice == "7":
                confirm = input("Delete ALL rows and reset ids? (Y/N): ").strip().upper()
                if confirm == "Y":
                    reset_all_courses(connection)
                    print("All data reset.\n")
                else:
                    print("Canceled.\n")
            elif choice == "0":
                print("Bye.")
                break
            else:
                print("Invalid choice.\n")
    finally:
        connection.close()


if __name__ == "__main__":
    main()

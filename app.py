"""Flask web app for Course Catalog CRUD."""

from flask import Flask, flash, redirect, render_template, request, url_for

from db import (
    add_course,
    connect_db,
    delete_course,
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
VALID_SEMESTERS_SET = set(VALID_SEMESTERS)
VALID_MINI_VALUES = {"Y", "N"}

app = Flask(__name__)
app.config["SECRET_KEY"] = "course-catalog-dev-key"


def init_database() -> None:
    """Create database/table if needed when app starts."""
    connection = connect_db()
    try:
        initialize_db(connection)
    finally:
        connection.close()


def validate_course_form(form_data) -> tuple[dict, list[str]]:
    """Validate form values and return cleaned data with error list."""
    errors: list[str] = []

    course_number = form_data.get("course_number", "").strip()
    course_name = form_data.get("course_name", "").strip()
    department = form_data.get("department", "").strip()
    credits_raw = form_data.get("credits", "").strip()
    semester_offered = form_data.get("semester_offered", "").strip()
    mini_course = form_data.get("mini_course", "").strip().upper()
    description_raw = form_data.get("description", "").strip()
    fce_hours_raw = form_data.get("fce_hours", "").strip()

    if not course_number:
        errors.append("Course number is required.")
    if not course_name:
        errors.append("Course name is required.")
    if not department:
        errors.append("Department is required.")

    credits = None
    if not credits_raw:
        errors.append("Credits are required.")
    else:
        try:
            credits = int(credits_raw)
            if credits < 0:
                errors.append("Credits must be 0 or greater.")
        except ValueError:
            errors.append("Credits must be an integer.")

    if semester_offered not in VALID_SEMESTERS_SET:
        errors.append("Semester offered must match one of the valid options.")
    if mini_course not in VALID_MINI_VALUES:
        errors.append("Mini course must be Y or N.")

    description = description_raw if description_raw else None
    fce_hours = None
    if fce_hours_raw:
        try:
            fce_hours = float(fce_hours_raw)
        except ValueError:
            errors.append("FCE hours must be a number or left blank.")

    cleaned = {
        "course_number": course_number,
        "course_name": course_name,
        "department": department,
        "credits": credits,
        "semester_offered": semester_offered,
        "mini_course": mini_course,
        "description": description,
        "fce_hours": fce_hours,
    }
    return cleaned, errors


def is_entry_blank(entry: dict) -> bool:
    """Return True if all entry fields are empty."""
    keys = [
        "course_number",
        "course_name",
        "department",
        "credits",
        "semester_offered",
        "mini_course",
        "description",
        "fce_hours",
    ]
    return all(not str(entry.get(key, "")).strip() for key in keys)


@app.route("/")
def home():
    """Redirect to read page."""
    return redirect(url_for("read_courses"))


@app.route("/courses")
def read_courses():
    """Read page with filter/sort controls and SQL visualization."""
    filters = {
        "department": request.args.get("department", "").strip(),
        "semester_offered": request.args.get("semester_offered", "").strip(),
        "mini_only": request.args.get("mini_only") == "1",
        "keyword": request.args.get("keyword", "").strip(),
        "sort_by": request.args.get("sort_by", "id").strip(),
        "sort_order": request.args.get("sort_order", "asc").strip().lower(),
    }

    connection = connect_db()
    try:
        courses, sql_preview, bound_params = query_courses(
            connection,
            department=filters["department"] or None,
            semester_offered=filters["semester_offered"] or None,
            mini_only=filters["mini_only"],
            keyword=filters["keyword"] or None,
            sort_by=filters["sort_by"],
            sort_order=filters["sort_order"],
        )
    finally:
        connection.close()

    return render_template(
        "courses.html",
        courses=courses,
        filters=filters,
        valid_semesters=VALID_SEMESTERS,
        sql_preview=sql_preview,
        bound_params=bound_params,
    )


@app.route("/courses/new", methods=["GET", "POST"])
def create_course():
    """Create page."""
    form_data = {}
    entries = [{}]
    errors: list[str] = []

    if request.method == "POST":
        # Batch mode from create page (fields named with [])
        if request.form.getlist("course_number[]"):
            entries = []
            to_insert: list[dict] = []

            course_numbers = request.form.getlist("course_number[]")
            course_names = request.form.getlist("course_name[]")
            departments = request.form.getlist("department[]")
            credits_list = request.form.getlist("credits[]")
            semesters = request.form.getlist("semester_offered[]")
            minis = request.form.getlist("mini_course[]")
            descriptions = request.form.getlist("description[]")
            fce_list = request.form.getlist("fce_hours[]")

            row_count = len(course_numbers)
            for idx in range(row_count):
                entry = {
                    "course_number": course_numbers[idx] if idx < len(course_numbers) else "",
                    "course_name": course_names[idx] if idx < len(course_names) else "",
                    "department": departments[idx] if idx < len(departments) else "",
                    "credits": credits_list[idx] if idx < len(credits_list) else "",
                    "semester_offered": semesters[idx] if idx < len(semesters) else "",
                    "mini_course": minis[idx] if idx < len(minis) else "",
                    "description": descriptions[idx] if idx < len(descriptions) else "",
                    "fce_hours": fce_list[idx] if idx < len(fce_list) else "",
                }
                entries.append(entry)

                if is_entry_blank(entry):
                    continue

                cleaned, row_errors = validate_course_form(entry)
                if row_errors:
                    for err in row_errors:
                        errors.append(f"Row {idx + 1}: {err}")
                else:
                    to_insert.append(cleaned)

            if not to_insert and not errors:
                errors.append("Please fill at least one course row before submitting.")

            if not errors and to_insert:
                connection = connect_db()
                try:
                    for item in to_insert:
                        add_course(connection, **item)
                finally:
                    connection.close()
                flash(f"{len(to_insert)} course(s) created successfully.", "success")
                return redirect(url_for("read_courses"))
        else:
            # Fallback single-entry submission
            form_data = request.form.to_dict()
            cleaned, errors = validate_course_form(request.form)
            if not errors:
                connection = connect_db()
                try:
                    new_id = add_course(connection, **cleaned)
                finally:
                    connection.close()
                flash(f"Course created successfully (id={new_id}).", "success")
                return redirect(url_for("read_courses"))
            entries = [form_data]

    return render_template(
        "course_form.html",
        mode="create",
        title="Create Course",
        action_url=url_for("create_course"),
        form_data=form_data,
        entries=entries,
        errors=errors,
        valid_semesters=VALID_SEMESTERS,
    )


@app.route("/courses/<int:course_id>/edit", methods=["GET", "POST"])
def edit_course(course_id: int):
    """Update page."""
    connection = connect_db()
    try:
        existing = get_course_by_id(connection, course_id)
        if existing is None:
            flash(f"Course id={course_id} not found.", "error")
            return redirect(url_for("read_courses"))

        errors: list[str] = []
        if request.method == "POST":
            cleaned, errors = validate_course_form(request.form)
            form_data = request.form.to_dict()
            if not errors:
                updated = update_course(connection, course_id=course_id, **cleaned)
                if updated:
                    flash(f"Course id={course_id} updated successfully.", "success")
                else:
                    flash("Update failed.", "error")
                return redirect(url_for("read_courses"))
        else:
            form_data = {
                "course_number": existing["course_number"],
                "course_name": existing["course_name"],
                "department": existing["department"],
                "credits": str(existing["credits"]),
                "semester_offered": existing["semester_offered"],
                "mini_course": existing["mini_course"],
                "description": existing["description"] or "",
                "fce_hours": (
                    "" if existing["fce_hours"] is None else str(existing["fce_hours"])
                ),
            }
    finally:
        connection.close()

    return render_template(
        "course_form.html",
        mode="edit",
        title=f"Update Course #{course_id}",
        action_url=url_for("edit_course", course_id=course_id),
        form_data=form_data,
        errors=errors,
        valid_semesters=VALID_SEMESTERS,
    )


@app.route("/courses/<int:course_id>/delete", methods=["POST"])
def remove_course(course_id: int):
    """Handle inline delete confirmation submission."""
    connection = connect_db()
    try:
        course = get_course_by_id(connection, course_id)
        if course is None:
            flash(f"Course id={course_id} not found.", "error")
            return redirect(url_for("read_courses"))

        confirmed = request.form.get("confirm_delete", "N") == "Y"
        if confirmed and delete_course(connection, course_id):
            flash(f"Course id={course_id} deleted successfully.", "success")
        else:
            flash("Delete canceled.", "error")
        return redirect(url_for("read_courses"))
    finally:
        connection.close()


@app.route("/courses/reset", methods=["POST"])
def reset_courses():
    """Delete all course rows and reset ids."""
    confirmed = request.form.get("confirm_reset", "N") == "Y"
    if not confirmed:
        flash("Reset canceled.", "error")
        return redirect(url_for("read_courses"))

    connection = connect_db()
    try:
        reset_all_courses(connection)
    finally:
        connection.close()

    flash("All courses were deleted. Database reset complete.", "success")
    return redirect(url_for("read_courses"))


if __name__ == "__main__":
    init_database()
    app.run(debug=True)

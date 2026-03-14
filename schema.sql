CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_number TEXT NOT NULL,
    course_name TEXT NOT NULL,
    department TEXT NOT NULL,
    credits INTEGER NOT NULL,
    semester_offered TEXT NOT NULL,
    mini_course TEXT NOT NULL,
    description TEXT,
    fce_hours REAL
);

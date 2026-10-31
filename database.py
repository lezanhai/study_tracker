
#database.py
import sqlite3
from pathlib import Path
from datetime import date


class DatabaseManager:

    def __init__(self):
        db_path = Path(__file__).resolve().parent / "study_tracker.db"

        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")

        self.create_tables()

    # =================================
    # TẠO CÁC BẢNG
    # =================================

    
    def create_tables(self):

        # Bảng môn học
        query_subjects = """
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL COLLATE NOCASE UNIQUE,
            description TEXT
        )
        """

        # Bảng buổi học
        query_sessions = """
        CREATE TABLE IF NOT EXISTS study_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            study_date TEXT NOT NULL,
            start_time TEXT,
            end_time TEXT,
            duration_seconds INTEGER NOT NULL CHECK(duration_seconds > 0),
            note TEXT,

            FOREIGN KEY (subject_id)
            REFERENCES subjects(id)
            ON DELETE RESTRICT
        )
        """

        # Bảng mục tiêu học tập
        query_goals = """
        CREATE TABLE IF NOT EXISTS study_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            week_start TEXT NOT NULL UNIQUE,
            target_minutes INTEGER NOT NULL CHECK(target_minutes > 0)
        )
        """

        # Bảng bài tập và deadline
        query_tasks = """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            due_date TEXT NOT NULL,

            priority TEXT NOT NULL DEFAULT 'Trung bình'
                CHECK(priority IN ('Thấp', 'Trung bình', 'Cao')),

            status TEXT NOT NULL DEFAULT 'Chưa bắt đầu'
                CHECK(status IN (
                    'Chưa bắt đầu',
                    'Đang thực hiện',
                    'Đã hoàn thành'
                )),

            created_at TEXT DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (subject_id)
            REFERENCES subjects(id)
            ON DELETE RESTRICT
        )
        """

        self.conn.execute(query_subjects)
        self.conn.execute(query_sessions)
        self.conn.execute(query_goals)
        self.conn.execute(query_tasks)

        self.conn.commit()


    # =================================
    # QUẢN LÝ MÔN HỌC
    # =================================

    def add_subject(self, name, description):

        try:
            query = """
            INSERT INTO subjects (name, description)
            VALUES (?, ?)
            """

            self.conn.execute(query, (name, description))
            self.conn.commit()

        except sqlite3.IntegrityError:
            raise ValueError("Môn học này đã tồn tại!")

    def get_subjects(self):

        query = """
        SELECT id, name, description
        FROM subjects
        ORDER BY id DESC
        """

        cursor = self.conn.execute(query)
        return cursor.fetchall()
    
    def update_subject(self, subject_id, name, description):

        try:
            query = """
            UPDATE subjects
            SET name = ?, description = ?
            WHERE id = ?
            """

            self.conn.execute(query, (name, description, subject_id))
            self.conn.commit()

        except sqlite3.IntegrityError:
            raise ValueError("Tên môn học này đã tồn tại!")

    def count_subject_usage(self, subject_id):
        """Trả về (số buổi học, số công việc) đang dùng môn này."""

        sessions = self.conn.execute(
            "SELECT COUNT(*) FROM study_sessions WHERE subject_id = ?",
            (subject_id,)
        ).fetchone()[0]

        tasks = self.conn.execute(
            "SELECT COUNT(*) FROM tasks WHERE subject_id = ?",
            (subject_id,)
        ).fetchone()[0]

        return sessions, tasks

    def delete_subject(self, subject_id):

        try:
            self.conn.execute(
                "DELETE FROM subjects WHERE id = ?",
                (subject_id,)
            )
            self.conn.commit()

        except sqlite3.IntegrityError:
            raise ValueError(
                "Không thể xóa môn học đang có dữ liệu liên quan!"
            )
    # =================================
    # QUẢN LÝ BUỔI HỌC
    # =================================

    def add_session(self, subject_id, study_date, duration_minutes, note):
        """study_date là chuỗi ISO 'YYYY-MM-DD'."""

        duration_seconds = int(round(duration_minutes * 60))

        if duration_seconds <= 0:
            raise ValueError("Thời gian học phải lớn hơn 0!")

        query = """
        INSERT INTO study_sessions (
            subject_id,
            study_date,
            duration_seconds,
            note
        )
        VALUES (?, ?, ?, ?)
        """

        self.conn.execute(
            query,
            (subject_id, study_date, duration_seconds, note)
        )

        self.conn.commit()

    def add_timed_session(
        self,
        subject_id,
        start_time,
        end_time,
        duration_seconds,
        note
    ):

        if duration_seconds <= 0:
            raise ValueError("Thời gian học phải lớn hơn 0!")

        study_date = start_time[:10]

        query = """
        INSERT INTO study_sessions (
            subject_id,
            study_date,
            start_time,
            end_time,
            duration_seconds,
            note
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """

        self.conn.execute(
            query,
            (
                subject_id,
                study_date,
                start_time,
                end_time,
                duration_seconds,
                note
            )
        )

        self.conn.commit()

    def get_sessions(self):

        query = """
        SELECT
            study_sessions.id,
            subjects.name,
            study_sessions.study_date,
            study_sessions.duration_seconds,
            study_sessions.note

        FROM study_sessions

        JOIN subjects
        ON study_sessions.subject_id = subjects.id

        ORDER BY study_sessions.id DESC
        """

        cursor = self.conn.execute(query)
        return cursor.fetchall()
    def get_session(self, session_id):

        query = """
        SELECT id, subject_id, study_date, duration_seconds, note
        FROM study_sessions
        WHERE id = ?
        """

        return self.conn.execute(query, (session_id,)).fetchone()

    def update_session(self, session_id, subject_id, duration_minutes, note):

        duration_seconds = int(round(duration_minutes * 60))

        if duration_seconds <= 0:
            raise ValueError("Thời gian học phải lớn hơn 0!")

        query = """
        UPDATE study_sessions
        SET subject_id = ?, duration_seconds = ?, note = ?
        WHERE id = ?
        """

        self.conn.execute(
            query,
            (subject_id, duration_seconds, note, session_id)
        )

        self.conn.commit()

    def delete_session(self, session_id):

        self.conn.execute(
            "DELETE FROM study_sessions WHERE id = ?",
            (session_id,)
        )

        self.conn.commit()
        
    def get_sessions_for_export(self, start_date, end_date):

        query = """
        SELECT
            study_sessions.study_date,
            subjects.name,
            study_sessions.start_time,
            study_sessions.end_time,
            study_sessions.duration_seconds,
            study_sessions.note

        FROM study_sessions

        JOIN subjects
        ON study_sessions.subject_id = subjects.id

        WHERE study_sessions.study_date BETWEEN ? AND ?

        ORDER BY study_sessions.study_date ASC, study_sessions.id ASC
        """

        return self.conn.execute(
            query,
            (start_date, end_date)
        ).fetchall()
    # =================================
    # THỐNG KÊ THỜI GIAN HỌC
    # =================================

    def get_statistics(self, start_date, end_date):

        summary_query = """
        SELECT
            COALESCE(SUM(duration_seconds), 0),
            COUNT(*),
            COUNT(DISTINCT subject_id)

        FROM study_sessions

        WHERE study_date BETWEEN ? AND ?
        """

        summary = self.conn.execute(
            summary_query,
            (start_date, end_date)
        ).fetchone()

        subject_query = """
        SELECT
            subjects.name,
            COUNT(study_sessions.id),
            COALESCE(SUM(study_sessions.duration_seconds), 0)

        FROM study_sessions

        JOIN subjects
        ON study_sessions.subject_id = subjects.id

        WHERE study_sessions.study_date BETWEEN ? AND ?

        GROUP BY subjects.id, subjects.name

        ORDER BY SUM(study_sessions.duration_seconds) DESC
        """

        subject_statistics = self.conn.execute(
            subject_query,
            (start_date, end_date)
        ).fetchall()

        daily_query = """
        SELECT
            study_date,
            COUNT(*),
            COALESCE(SUM(duration_seconds), 0)

        FROM study_sessions

        WHERE study_date BETWEEN ? AND ?

        GROUP BY study_date

        ORDER BY study_date DESC
        """

        daily_statistics = self.conn.execute(
            daily_query,
            (start_date, end_date)
        ).fetchall()

        return summary, subject_statistics, daily_statistics

    # =================================
    # QUẢN LÝ MỤC TIÊU HỌC TẬP
    # =================================

    # Lưu hoặc cập nhật mục tiêu tuần
    def save_weekly_goal(self, week_start, target_minutes):

        if target_minutes <= 0:
            raise ValueError("Mục tiêu phải lớn hơn 0!")

        query = """
        INSERT INTO study_goals (week_start, target_minutes)
        VALUES (?, ?)

        ON CONFLICT(week_start)
        DO UPDATE SET target_minutes = excluded.target_minutes
        """

        self.conn.execute(
            query,
            (week_start, target_minutes)
        )

        self.conn.commit()

    # Lấy mục tiêu tuần
    def get_weekly_goal(self, week_start):

        query = """
        SELECT target_minutes
        FROM study_goals
        WHERE week_start = ?
        """

        result = self.conn.execute(
            query,
            (week_start,)
        ).fetchone()

        return result[0] if result else None

    # Tính tổng thời gian học trong tuần
    def get_weekly_study_seconds(self, start_date, end_date):

        query = """
        SELECT COALESCE(SUM(duration_seconds), 0)
        FROM study_sessions
        WHERE study_date BETWEEN ? AND ?
        """

        result = self.conn.execute(
            query,
            (start_date, end_date)
        ).fetchone()

        return result[0]

    
    # =================================
    # QUẢN LÝ BÀI TẬP VÀ DEADLINE
    # =================================

    # Thêm công việc
    def add_task(
        self,
        subject_id,
        title,
        description,
        due_date,
        priority
    ):

        query = """
        INSERT INTO tasks (
            subject_id,
            title,
            description,
            due_date,
            priority
        )
        VALUES (?, ?, ?, ?, ?)
        """

        self.conn.execute(
            query,
            (
                subject_id,
                title,
                description,
                due_date,
                priority
            )
        )

        self.conn.commit()

    # Lấy thông tin một công việc
    def get_task(self, task_id):

        query = """
        SELECT
            id,
            subject_id,
            title,
            description,
            due_date,
            priority,
            status
        FROM tasks
        WHERE id = ?
        """

        return self.conn.execute(
            query,
            (task_id,)
        ).fetchone()

    # Lấy danh sách công việc
    def get_tasks(self, status_filter="Tất cả"):

        today = date.today().isoformat()

        query = """
        SELECT
            tasks.id,
            subjects.name,
            tasks.title,
            tasks.due_date,
            tasks.priority,

            CASE
                WHEN tasks.status != 'Đã hoàn thành'
                     AND tasks.due_date < ?
                THEN 'Quá hạn'
                ELSE tasks.status
            END AS display_status

        FROM tasks

        JOIN subjects
        ON tasks.subject_id = subjects.id
        """

        parameters = [today]

        if status_filter == "Quá hạn":

            query += """
            WHERE tasks.status != 'Đã hoàn thành'
            AND tasks.due_date < ?
            """

            parameters.append(today)

        elif status_filter != "Tất cả":

            query += """
            WHERE tasks.status = ?
            """

            parameters.append(status_filter)

        query += """
        ORDER BY
            CASE
                WHEN tasks.status != 'Đã hoàn thành'
                     AND tasks.due_date < ?
                THEN 0
                ELSE 1
            END,
            tasks.due_date ASC
        """

        parameters.append(today)

        return self.conn.execute(
            query,
            parameters
        ).fetchall()

    # Cập nhật thông tin công việc
    def update_task(
        self,
        task_id,
        subject_id,
        title,
        description,
        due_date,
        priority
    ):

        query = """
        UPDATE tasks
        SET
            subject_id = ?,
            title = ?,
            description = ?,
            due_date = ?,
            priority = ?
        WHERE id = ?
        """

        self.conn.execute(
            query,
            (
                subject_id,
                title,
                description,
                due_date,
                priority,
                task_id
            )
        )

        self.conn.commit()

    # Cập nhật trạng thái
    def update_task_status(self, task_id, status):

        allowed_statuses = [
            "Chưa bắt đầu",
            "Đang thực hiện",
            "Đã hoàn thành"
        ]

        if status not in allowed_statuses:
            raise ValueError("Trạng thái không hợp lệ!")

        query = """
        UPDATE tasks
        SET status = ?
        WHERE id = ?
        """

        self.conn.execute(
            query,
            (status, task_id)
        )

        self.conn.commit()

    # Xóa công việc
    def delete_task(self, task_id):

        query = """
        DELETE FROM tasks
        WHERE id = ?
        """

        self.conn.execute(
            query,
            (task_id,)
        )

        self.conn.commit()

    # =================================
    # ĐÓNG KẾT NỐI
    # =================================

    def close(self):
        self.conn.close()

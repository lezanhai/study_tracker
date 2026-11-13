
# seed_demo.py
from datetime import datetime, date, time, timedelta

from database import DatabaseManager


def seed_demo_data():

    db = DatabaseManager()

    try:
        # =====================================
        # 1. TẠO CÁC MÔN HỌC MẪU
        # =====================================

        sample_subjects = [
            ("Python", "Lập trình Python và OOP"),
            ("Toán A3", "Đại số tuyến tính"),
            ("Cơ sở dữ liệu", "SQL và quản trị cơ sở dữ liệu"),
            ("Tiếng Anh", "Học từ vựng và luyện giao tiếp")
        ]

        for name, description in sample_subjects:

            try:
                db.add_subject(name, description)

            except ValueError:
                # Bỏ qua nếu môn học đã tồn tại
                pass

        subjects = db.get_subjects()

        subject_map = {
            subject[1]: subject[0]
            for subject in subjects
        }

        print("Đã kiểm tra danh sách môn học.")

        # =====================================
        # 2. XÓA DỮ LIỆU DEMO CŨ
        # =====================================
        # Chỉ xóa những dữ liệu có nhãn [DEMO].
        # Không xóa dữ liệu học tập thật của bạn.

        db.conn.execute("""
            DELETE FROM study_sessions
            WHERE note LIKE '[DEMO]%'
        """)

        db.conn.execute("""
            DELETE FROM tasks
            WHERE title LIKE '[DEMO]%'
        """)

        db.conn.commit()

        # =====================================
        # 3. TẠO LỊCH SỬ HỌC TẬP
        # =====================================

        today = date.today()

        for days_ago in range(14):

            study_day = today - timedelta(days=days_ago)

            # Một số ngày có 2 buổi, ngày khác có 1 buổi
            number_of_sessions = 2 if days_ago % 3 == 0 else 1

            for index in range(number_of_sessions):

                # Luân phiên các môn học
                subject = subjects[
                    (days_ago + index) % len(subjects)
                ]

                subject_id = subject[0]

                # Giờ bắt đầu: 08:00 hoặc 12:00
                start = datetime.combine(
                    study_day,
                    time(hour=8 + index * 4)
                )

                # Thời gian học từ 35 đến 90 phút
                duration_minutes = (
                    35 + (days_ago * 7 + index * 13) % 56
                )

                end = start + timedelta(
                    minutes=duration_minutes
                )

                duration_seconds = duration_minutes * 60

                db.add_timed_session(
                    subject_id,
                    start.isoformat(
                        sep=" ",
                        timespec="seconds"
                    ),
                    end.isoformat(
                        sep=" ",
                        timespec="seconds"
                    ),
                    duration_seconds,
                    f"[DEMO] Buổi học mẫu - {subject[1]}"
                )

        print("Đã tạo lịch sử học tập.")

        # =====================================
        # 4. TẠO MỤC TIÊU HỌC TẬP THEO TUẦN
        # =====================================

        # Xác định ngày thứ Hai của tuần hiện tại
        monday = today - timedelta(days=today.weekday())

        for week_offset in range(4):

            week_start = monday - timedelta(
                weeks=week_offset
            )

            target_minutes = 600 + week_offset * 60

            db.save_weekly_goal(
                week_start.isoformat(),
                target_minutes
            )

        print("Đã tạo mục tiêu học tập.")

        # =====================================
        # 5. TẠO CÔNG VIỆC MẪU
        # =====================================

        sample_tasks = [
            (
                "Python",
                "[DEMO] Hoàn thành bài tập OOP",
                "Ôn tập class, object và tính kế thừa",
                today + timedelta(days=2),
                "Cao",
                "Đang thực hiện"
            ),
            (
                "Toán A3",
                "[DEMO] Ôn tập ánh xạ tuyến tính",
                "Làm bài tập về Ker và Im",
                today + timedelta(days=5),
                "Trung bình",
                "Chưa bắt đầu"
            ),
            (
                "Cơ sở dữ liệu",
                "[DEMO] Hoàn thành bài tập SQL",
                "Ôn tập JOIN, GROUP BY và truy vấn",
                today - timedelta(days=2),
                "Cao",
                "Chưa bắt đầu"
            ),
            (
                "Tiếng Anh",
                "[DEMO] Hoàn thành bài Speaking",
                "Chuẩn bị nội dung thuyết trình",
                today - timedelta(days=1),
                "Thấp",
                "Đã hoàn thành"
            )
        ]

        for (
            subject_name,
            title,
            description,
            due_date,
            priority,
            status
        ) in sample_tasks:

            db.add_task(
                subject_map[subject_name],
                title,
                description,
                due_date.isoformat(),
                priority
            )

            # Lấy mã công việc vừa thêm
            task_id = db.conn.execute(
                "SELECT last_insert_rowid()"
            ).fetchone()[0]

            # Cập nhật trạng thái
            db.update_task_status(
                task_id,
                status
            )

        print("Đã tạo công việc mẫu.")

        print("\n================================")
        print("HOÀN TẤT TẠO DỮ LIỆU DEMO!")
        print("================================")

    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_data()

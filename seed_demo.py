from datetime import datetime, timedelta
import random
from database import DatabaseManager

db = DatabaseManager()

for name in ["Python", "Toán rời rạc", "Tiếng Anh", "Cơ sở dữ liệu"]:
    try:
        db.add_subject(name, "Môn học mẫu")
    except ValueError:
        pass  # môn đã tồn tại

subjects = db.get_subjects()
today = datetime.now()

for days_ago in range(10):
    for _ in range(random.randint(1, 3)):
        subject = random.choice(subjects)
        start = (today - timedelta(days=days_ago)).replace(
            hour=random.randint(7, 20), minute=0, second=0, microsecond=0
        )
        seconds = random.randint(20, 120) * 60
        end = start + timedelta(seconds=seconds)
        db.add_timed_session(
            subject[0],
            start.isoformat(sep=" ", timespec="seconds"),
            end.isoformat(sep=" ", timespec="seconds"),
            seconds,
            "[DEMO]"
        )

db.close()
print("Đã thêm dữ liệu mẫu")
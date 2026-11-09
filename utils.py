# utils.py
from datetime import date, timedelta


def format_duration(total_seconds):
    """Đổi số giây thành chuỗi dễ đọc: '1 giờ 5 phút', '2 phút 5 giây'..."""

    total_seconds = int(total_seconds)

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    if hours > 0:
        return f"{hours} giờ {minutes} phút"

    if minutes > 0:
        return f"{minutes} phút {seconds} giây"

    return f"{seconds} giây"


def get_date_range(period, today=None):
    """Trả về (ngày bắt đầu, ngày kết thúc) dạng chuỗi ISO
    theo lựa chọn: Hôm nay / Tuần này / Tháng này / Tất cả."""

    today = today or date.today()

    if period == "Hôm nay":
        start_date = today

    elif period == "Tuần này":
        start_date = today - timedelta(days=today.weekday())

    elif period == "Tháng này":
        start_date = today.replace(day=1)

    else:
        start_date = date(1, 1, 1)

    return start_date.isoformat(), today.isoformat()


def setup_table(table, columns):
    """
    columns: danh sách (mã_cột, tiêu_đề, độ_rộng, căn_lề)
    Tiêu đề và dữ liệu dùng CHUNG một kiểu căn lề
    nên luôn thẳng hàng với nhau.
    """

    for column_id, title, width, anchor in columns:

        table.heading(
            column_id,
            text=title,
            anchor=anchor
        )

        table.column(
            column_id,
            width=width,
            minwidth=width,
            anchor=anchor,
            stretch=True
        )
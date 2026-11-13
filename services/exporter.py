# exporter.py
import pandas as pd

RAW_COLUMNS = [
    "study_date",
    "subject",
    "start_time",
    "end_time",
    "duration_seconds",
    "note"
]


def build_frames(rows):
    """Chuyển dữ liệu từ database thành 3 bảng Pandas."""

    raw = pd.DataFrame(rows, columns=RAW_COLUMNS)

    raw["minutes"] = (raw["duration_seconds"] / 60).round(1)

    for column in ("start_time", "end_time", "note"):
        raw[column] = raw[column].fillna("")

    total_seconds = raw["duration_seconds"].sum()

    # Bảng 1: chi tiết từng buổi học
    detail = pd.DataFrame({
        "Ngày học": raw["study_date"],
        "Môn học": raw["subject"],
        "Giờ bắt đầu": raw["start_time"],
        "Giờ kết thúc": raw["end_time"],
        "Thời gian (phút)": raw["minutes"],
        "Nội dung": raw["note"]
    })

    # Bảng 2: tổng hợp theo môn học
    grouped_subject = (
        raw.groupby("subject")["duration_seconds"]
        .agg(["count", "sum"])
        .reset_index()
        .sort_values("sum", ascending=False)
    )

    by_subject = pd.DataFrame({
        "Môn học": grouped_subject["subject"],
        "Số buổi": grouped_subject["count"],
        "Tổng thời gian (phút)": (grouped_subject["sum"] / 60).round(1),
        "Tỷ lệ (%)": (grouped_subject["sum"] / total_seconds * 100).round(1)
    })

    # Bảng 3: tổng hợp theo ngày
    grouped_day = (
        raw.groupby("study_date")["duration_seconds"]
        .agg(["count", "sum"])
        .reset_index()
        .sort_values("study_date")
    )

    by_day = pd.DataFrame({
        "Ngày học": grouped_day["study_date"],
        "Số buổi": grouped_day["count"],
        "Tổng thời gian (phút)": (grouped_day["sum"] / 60).round(1)
    })

    return {
        "Buổi học": detail,
        "Theo môn": by_subject,
        "Theo ngày": by_day
    }


def _write_excel(frames, path):

    # Import tại đây để app vẫn chạy nếu chưa cài openpyxl
    from openpyxl.utils import get_column_letter

    with pd.ExcelWriter(path, engine="openpyxl") as writer:

        for sheet_name, frame in frames.items():

            frame.to_excel(writer, sheet_name=sheet_name, index=False)

            sheet = writer.sheets[sheet_name]

            # Tự chỉnh độ rộng cột cho dễ đọc
            for index, column in enumerate(frame.columns, start=1):

                longest = max(
                    [len(str(column))]
                    + [len(str(value)) for value in frame[column]]
                )

                sheet.column_dimensions[
                    get_column_letter(index)
                ].width = min(longest + 3, 50)


def export_report(rows, path):
    """Xuất báo cáo ra .xlsx hoặc .csv tùy đuôi file."""

    if not rows:
        raise ValueError("Không có dữ liệu để xuất!")

    frames = build_frames(rows)
    lower_path = path.lower()

    if lower_path.endswith(".csv"):
        # utf-8-sig để Excel trên Windows đọc đúng tiếng Việt
        frames["Buổi học"].to_csv(
            path,
            index=False,
            encoding="utf-8-sig"
        )

    elif lower_path.endswith(".xlsx"):
        _write_excel(frames, path)

    else:
        raise ValueError("Chỉ hỗ trợ định dạng .xlsx và .csv!")
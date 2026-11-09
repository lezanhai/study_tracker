# theme.py
from tkinter import ttk

# =========================================
# CẤU HÌNH MÀU SẮC
# =========================================

BG = "#F1F5F9"
WHITE = "#FFFFFF"
NAVY = "#172554"
BLUE = "#2563EB"
BLUE_HOVER = "#1D4ED8"
TEAL = "#0F766E"
TEXT = "#1E293B"
MUTED = "#64748B"
BORDER = "#E2E8F0"
RED = "#DC2626"

# Bảng màu cho biểu đồ
CHART_COLORS = [
    "#2563EB", "#0F766E", "#F59E0B", "#DC2626",
    "#7C3AED", "#0891B2", "#65A30D", "#DB2777"
]


def apply_style():
    """Cấu hình giao diện ttk cho toàn ứng dụng.
    Phải gọi SAU khi đã tạo cửa sổ gốc tk.Tk()."""

    style = ttk.Style()
    style.theme_use("clam")

    style.configure(".", font=("Segoe UI", 10))

    style.configure("TFrame", background=BG)
    style.configure("Card.TFrame", background=WHITE)

    style.configure(
        "TLabel",
        background=BG,
        foreground=TEXT,
        font=("Segoe UI", 10)
    )

    style.configure(
        "Title.TLabel",
        background=BG,
        foreground=NAVY,
        font=("Segoe UI", 20, "bold")
    )

    style.configure(
        "Subtitle.TLabel",
        background=BG,
        foreground=MUTED
    )

    style.configure(
        "CardTitle.TLabel",
        background=WHITE,
        foreground=NAVY,
        font=("Segoe UI", 11, "bold")
    )

    style.configure(
        "Value.TLabel",
        background=WHITE,
        foreground=BLUE,
        font=("Segoe UI", 19, "bold")
    )

    style.configure(
        "TButton",
        font=("Segoe UI", 10, "bold"),
        padding=(14, 9),
        background=BLUE,
        foreground=WHITE,
        borderwidth=0
    )

    style.map(
        "TButton",
        background=[
            ("active", BLUE_HOVER),
            ("disabled", "#CBD5E1")
        ],
        foreground=[
            ("disabled", "#64748B")
        ]
    )

    style.configure(
        "Secondary.TButton",
        background="#E2E8F0",
        foreground=NAVY
    )

    style.configure(
        "Danger.TButton",
        background=RED,
        foreground=WHITE
    )

    style.configure(
        "TNotebook",
        background=BG,
        borderwidth=0
    )

    style.configure(
        "TNotebook.Tab",
        background="#E2E8F0",
        foreground=MUTED,
        padding=(15, 12),
        font=("Segoe UI", 10, "bold")
    )

    style.map(
        "TNotebook.Tab",
        background=[
            ("selected", WHITE),
            ("active", "#DBEAFE")
        ],
        foreground=[
            ("selected", BLUE),
            ("active", NAVY)
        ]
    )

    style.configure(
        "Treeview",
        background=WHITE,
        fieldbackground=WHITE,
        foreground=TEXT,
        rowheight=32,
        font=("Segoe UI", 10)
    )

    style.configure(
        "Treeview.Heading",
        background="#E2E8F0",
        foreground=NAVY,
        font=("Segoe UI", 10, "bold"),
        padding=10,
        relief="flat"
    )

    style.map(
        "Treeview",
        background=[("selected", "#DBEAFE")],
        foreground=[("selected", NAVY)]
    )

    style.configure("TEntry", padding=8, fieldbackground=WHITE)
    style.configure("TCombobox", padding=7, fieldbackground=WHITE)

    style.configure(
        "Horizontal.TProgressbar",
        troughcolor="#E2E8F0",
        background=TEAL,
        thickness=16
    )
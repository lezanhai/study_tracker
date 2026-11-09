# base_tab.py
from tkinter import ttk


class BaseTab:
    """Lớp cha cho mọi tab: giữ khung chứa, database và các hàm dựng
    giao diện dùng chung (tiêu đề trang, thẻ nội dung)."""

    def __init__(self, parent, db):

        self.parent = parent
        self.db = db

    def page_title(self, title, subtitle):

        ttk.Label(
            self.parent,
            text=title,
            style="Title.TLabel"
        ).pack(anchor="w", padx=25, pady=(22, 3))

        ttk.Label(
            self.parent,
            text=subtitle,
            style="Subtitle.TLabel"
        ).pack(anchor="w", padx=25, pady=(0, 18))

    def create_card(self, title=None):

        card = ttk.Frame(
            self.parent,
            style="Card.TFrame",
            padding=18
        )

        card.pack(fill="x", padx=25, pady=8)

        if title:
            ttk.Label(
                card,
                text=title,
                style="CardTitle.TLabel"
            ).pack(anchor="w", pady=(0, 12))

        return card
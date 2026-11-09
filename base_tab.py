
# base_tab.py

from tkinter import ttk


class BaseTab:
    """
    Lớp cha cho các tab trong Study Tracker.

    Chứa những thành phần giao diện được sử dụng chung:
    - Tiêu đề trang
    - Tiêu đề phụ
    - Thẻ nội dung
    """

    def __init__(self, parent, db):

        self.parent = parent
        self.db = db

    # =====================================
    # TIÊU ĐỀ TRANG
    # =====================================

    def page_title(self, title, subtitle):

        ttk.Label(
            self.parent,
            text=title,
            style="Title.TLabel"
        ).pack(
            anchor="w",
            padx=25,
            pady=(22, 3)
        )

        ttk.Label(
            self.parent,
            text=subtitle,
            style="Subtitle.TLabel"
        ).pack(
            anchor="w",
            padx=25,
            pady=(0, 18)
        )

    # =====================================
    # TẠO THẺ NỘI DUNG
    # =====================================

    def create_card(
        self,
        title=None,
        fill="x",
        expand=False
    ):

        card = ttk.Frame(
            self.parent,
            style="Card.TFrame",
            padding=18
        )

        card.pack(
            fill=fill,
            expand=expand,
            padx=25,
            pady=8
        )

        if title:

            ttk.Label(
                card,
                text=title,
                style="CardTitle.TLabel"
            ).pack(
                anchor="w",
                pady=(0, 12)
            )

        return card

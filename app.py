import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

DB_NAME = "expenses.db"

BG = "#F5F7FB"
CARD = "#FFFFFF"
TEXT = "#172033"
MUTED = "#7B8496"
PRIMARY = "#5B5FEF"
PRIMARY_DARK = "#484CD0"
SIDEBAR = "#171B2E"
BORDER = "#E7EAF0"
DANGER = "#E95464"


class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME)
        self.cur = self.conn.cursor()
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS expenses(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def add(self, title, amount, category):
        self.cur.execute(
            "INSERT INTO expenses(title, amount, category, date) VALUES(?,?,?,?)",
            (title, amount, category, datetime.now().strftime("%Y-%m-%d"))
        )
        self.conn.commit()

    def update(self, expense_id, title, amount, category):
        self.cur.execute(
            "UPDATE expenses SET title=?, amount=?, category=? WHERE id=?",
            (title, amount, category, expense_id)
        )
        self.conn.commit()

    def delete(self, expense_id):
        self.cur.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
        self.conn.commit()

    def all(self, search=""):
        if search:
            self.cur.execute("""
                SELECT id,title,amount,category,date FROM expenses
                WHERE title LIKE ? OR category LIKE ?
                ORDER BY date DESC, id DESC
            """, (f"%{search}%", f"%{search}%"))
        else:
            self.cur.execute("""
                SELECT id,title,amount,category,date FROM expenses
                ORDER BY date DESC, id DESC
            """)
        return self.cur.fetchall()

    def stats(self):
        self.cur.execute("SELECT COALESCE(SUM(amount),0), COUNT(*) FROM expenses")
        total, count = self.cur.fetchone()
        self.cur.execute("""
            SELECT category, SUM(amount)
            FROM expenses GROUP BY category ORDER BY SUM(amount) DESC
        """)
        return total, count, self.cur.fetchall()

    def close(self):
        self.conn.close()


class ExpenseApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ExpenseFlow")
        self.geometry("1180x760")
        self.minsize(1050, 680)
        self.configure(bg=BG)

        self.db = Database()
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh_table())

        self.setup_styles()
        self.build_sidebar()
        self.build_main()
        self.refresh()
        self.protocol("WM_DELETE_WINDOW", self.close_app)

    def setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "Treeview", background=CARD, fieldbackground=CARD,
            foreground=TEXT, rowheight=42, borderwidth=0,
            font=("Segoe UI", 10)
        )
        style.configure(
            "Treeview.Heading", background="#F1F3F8",
            foreground=MUTED, relief="flat",
            font=("Segoe UI", 9, "bold"), padding=10
        )
        style.map(
            "Treeview",
            background=[("selected", "#E9E9FF")],
            foreground=[("selected", TEXT)]
        )
        style.configure(
            "TCombobox", fieldbackground="#F8F9FC",
            background="#F8F9FC", foreground=TEXT,
            bordercolor=BORDER, arrowsize=16, padding=7
        )

    def build_sidebar(self):
        sidebar = tk.Frame(self, bg=SIDEBAR, width=235)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        logo = tk.Frame(sidebar, bg=SIDEBAR)
        logo.pack(fill="x", padx=24, pady=(28, 38))

        tk.Label(
            logo, text="₹", font=("Segoe UI", 19, "bold"),
            bg=PRIMARY, fg="white", width=2
        ).pack(side="left", padx=(0, 10))

        tk.Label(
            logo, text="ExpenseFlow",
            font=("Segoe UI", 17, "bold"),
            bg=SIDEBAR, fg="white"
        ).pack(side="left")

        self.nav_button(sidebar, "▣", "Dashboard", True)
        self.nav_button(sidebar, "＋", "Add Expense", False, self.open_form)
        self.nav_button(sidebar, "▤", "Transactions", False,
                        self.show_transactions)

        tk.Frame(sidebar, bg="#292E46", height=1).pack(
            fill="x", padx=24, pady=24
        )

        tk.Label(
            sidebar, text="YOUR MONEY",
            font=("Segoe UI", 8, "bold"),
            bg=SIDEBAR, fg="#707891"
        ).pack(anchor="w", padx=28, pady=(0, 12))

        self.side_total = tk.Label(
            sidebar, text="₹0.00",
            font=("Segoe UI", 19, "bold"),
            bg=SIDEBAR, fg="white"
        )
        self.side_total.pack(anchor="w", padx=28)

        tk.Label(
            sidebar, text="Total recorded spending",
            font=("Segoe UI", 9),
            bg=SIDEBAR, fg="#8B93A9"
        ).pack(anchor="w", padx=28)

        tk.Frame(sidebar, bg=SIDEBAR).pack(expand=True)

        tk.Label(
            sidebar, text="Python • SQLite • OOP",
            font=("Segoe UI", 8),
            bg=SIDEBAR, fg="#6F778F"
        ).pack(pady=20)

    def nav_button(self, parent, symbol, text, active, command=None):
        bg = PRIMARY if active else SIDEBAR
        frame = tk.Frame(parent, bg=bg)
        frame.pack(fill="x", padx=14, pady=3)

        label = tk.Label(
            frame, text=f"{symbol}   {text}",
            anchor="w", padx=14, pady=11,
            font=("Segoe UI", 10, "bold" if active else "normal"),
            bg=bg, fg="white" if active else "#AEB5C7",
            cursor="hand2"
        )
        label.pack(fill="x")

        if command:
            label.bind("<Button-1>", lambda e: command())

    def build_main(self):
        main = tk.Frame(self, bg=BG)
        main.pack(side="left", fill="both", expand=True)

        header = tk.Frame(main, bg=BG)
        header.pack(fill="x", padx=38, pady=(30, 10))

        tk.Label(
            header, text="Good day 👋",
            font=("Segoe UI", 10), bg=BG, fg=MUTED
        ).pack(anchor="w")

        tk.Label(
            header, text="Your financial overview",
            font=("Segoe UI", 25, "bold"),
            bg=BG, fg=TEXT
        ).pack(anchor="w")

        tk.Button(
            header, text="＋  Add Expense",
            command=self.open_form,
            bg=PRIMARY, fg="white",
            activebackground=PRIMARY_DARK,
            relief="flat", bd=0,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2", padx=18, pady=11
        ).pack(side="right", pady=12)

        cards = tk.Frame(main, bg=BG)
        cards.pack(fill="x", padx=38, pady=16)

        self.total_card = self.metric_card(
            cards, "TOTAL SPENDING", "₹0.00", "All recorded expenses"
        )
        self.count_card = self.metric_card(
            cards, "TRANSACTIONS", "0", "Expenses recorded"
        )
        self.category_card = self.metric_card(
            cards, "TOP CATEGORY", "—", "Highest spending category"
        )

        body = tk.Frame(main, bg=BG)
        body.pack(fill="both", expand=True, padx=38, pady=(4, 30))

        analytics = tk.Frame(
            body, bg=CARD, highlightbackground=BORDER,
            highlightthickness=1
        )
        analytics.pack(side="left", fill="both", expand=True, padx=(0, 16))

        tk.Label(
            analytics, text="Spending by category",
            font=("Segoe UI", 14, "bold"),
            bg=CARD, fg=TEXT
        ).pack(anchor="w", padx=22, pady=(20, 2))

        tk.Label(
            analytics, text="A quick view of where your money goes",
            font=("Segoe UI", 9), bg=CARD, fg=MUTED
        ).pack(anchor="w", padx=22)

        self.chart = tk.Canvas(analytics, bg=CARD, highlightthickness=0)
        self.chart.pack(fill="both", expand=True, padx=18, pady=15)

        transactions = tk.Frame(
            body, bg=CARD, width=530,
            highlightbackground=BORDER, highlightthickness=1
        )
        transactions.pack(side="left", fill="both", expand=True)
        transactions.pack_propagate(False)

        top = tk.Frame(transactions, bg=CARD)
        top.pack(fill="x", padx=20, pady=(18, 10))

        tk.Label(
            top, text="Recent transactions",
            font=("Segoe UI", 14, "bold"),
            bg=CARD, fg=TEXT
        ).pack(side="left")

        tk.Entry(
            top, textvariable=self.search_var,
            relief="flat", bg="#F5F6FA",
            fg=TEXT, font=("Segoe UI", 9), width=20
        ).pack(side="right", ipady=7)

        table_wrap = tk.Frame(transactions, bg=CARD)
        table_wrap.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        columns = ("id", "title", "amount", "category", "date")
        self.tree = ttk.Treeview(
            table_wrap, columns=columns,
            show="headings", selectmode="browse"
        )

        headings = {
            "id": "#", "title": "Expense",
            "amount": "Amount", "category": "Category", "date": "Date"
        }
        widths = {"id": 40, "title": 150, "amount": 100,
                  "category": 100, "date": 100}

        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="w")

        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(
            table_wrap, orient="vertical", command=self.tree.yview
        )
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        actions = tk.Frame(transactions, bg=CARD)
        actions.pack(fill="x", padx=20, pady=(0, 18))

        tk.Button(
            actions, text="Edit", command=self.edit_selected,
            bg="#EEF0FF", fg=PRIMARY, relief="flat",
            font=("Segoe UI", 9, "bold"), cursor="hand2",
            padx=16, pady=8
        ).pack(side="left")

        tk.Button(
            actions, text="Delete", command=self.delete_selected,
            bg="#FFF0F1", fg=DANGER, relief="flat",
            font=("Segoe UI", 9, "bold"), cursor="hand2",
            padx=16, pady=8
        ).pack(side="left", padx=8)

    def metric_card(self, parent, title, value, subtitle):
        frame = tk.Frame(
            parent, bg=CARD, height=112,
            highlightbackground=BORDER, highlightthickness=1
        )
        frame.pack(side="left", fill="x", expand=True, padx=(0, 14))
        frame.pack_propagate(False)

        tk.Label(
            frame, text=title, font=("Segoe UI", 8, "bold"),
            bg=CARD, fg=MUTED
        ).pack(anchor="w", padx=18, pady=(16, 1))

        value_label = tk.Label(
            frame, text=value, font=("Segoe UI", 20, "bold"),
            bg=CARD, fg=TEXT
        )
        value_label.pack(anchor="w", padx=18)

        tk.Label(
            frame, text=subtitle, font=("Segoe UI", 8),
            bg=CARD, fg=MUTED
        ).pack(anchor="w", padx=18)

        return value_label

    def open_form(self, edit_id=None, existing=None):
        win = tk.Toplevel(self)
        win.title("Edit Expense" if edit_id else "Add Expense")
        win.geometry("420x440")
        win.resizable(False, False)
        win.configure(bg=CARD)
        win.transient(self)
        win.grab_set()

        tk.Label(
            win, text="Edit expense" if edit_id else "Add a new expense",
            font=("Segoe UI", 20, "bold"),
            bg=CARD, fg=TEXT
        ).pack(anchor="w", padx=32, pady=(28, 4))

        tk.Label(
            win, text="Keep your spending organized.",
            font=("Segoe UI", 9), bg=CARD, fg=MUTED
        ).pack(anchor="w", padx=32, pady=(0, 24))

        title_var = tk.StringVar(value=existing[1] if existing else "")
        amount_var = tk.StringVar(value=str(existing[2]) if existing else "")
        category_var = tk.StringVar(
            value=existing[3] if existing else "Food"
        )

        def add_field(label, variable):
            tk.Label(
                win, text=label, font=("Segoe UI", 9, "bold"),
                bg=CARD, fg=MUTED
            ).pack(anchor="w", padx=32, pady=(0, 5))

            tk.Entry(
                win, textvariable=variable,
                font=("Segoe UI", 10), relief="flat",
                bg="#F7F8FB", fg=TEXT,
                highlightthickness=1,
                highlightbackground=BORDER
            ).pack(fill="x", padx=32, ipady=9, pady=(0, 15))

        add_field("Expense name", title_var)
        add_field("Amount (₹)", amount_var)

        tk.Label(
            win, text="Category", font=("Segoe UI", 9, "bold"),
            bg=CARD, fg=MUTED
        ).pack(anchor="w", padx=32, pady=(0, 5))

        ttk.Combobox(
            win, textvariable=category_var,
            values=["Food", "Travel", "Shopping", "Bills",
                    "Education", "Entertainment", "Health", "Other"],
            state="readonly"
        ).pack(fill="x", padx=32, ipady=5, pady=(0, 25))

        def save():
            title = title_var.get().strip()
            category = category_var.get().strip()

            try:
                amount = float(amount_var.get())
                if amount <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror(
                    "Invalid amount",
                    "Enter a valid positive amount.", parent=win
                )
                return

            if not title:
                messagebox.showerror(
                    "Missing name",
                    "Enter an expense name.", parent=win
                )
                return

            if edit_id:
                self.db.update(edit_id, title, amount, category)
            else:
                self.db.add(title, amount, category)

            win.destroy()
            self.refresh()

        tk.Button(
            win, text="Save Expense", command=save,
            bg=PRIMARY, fg="white",
            activebackground=PRIMARY_DARK,
            relief="flat", bd=0,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2", pady=11
        ).pack(fill="x", padx=32)

    def edit_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo(
                "Edit expense", "Select a transaction first."
            )
            return

        expense_id = self.tree.item(selected[0])["values"][0]
        row = next(
            (r for r in self.db.all() if r[0] == expense_id), None
        )
        if row:
            self.open_form(edit_id=expense_id, existing=row)

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo(
                "Delete expense", "Select a transaction first."
            )
            return

        expense_id = self.tree.item(selected[0])["values"][0]

        if messagebox.askyesno(
            "Delete expense",
            "Delete the selected transaction?"
        ):
            self.db.delete(expense_id)
            self.refresh()

    def show_transactions(self):
        win = tk.Toplevel(self)
        win.title("All Transactions")
        win.geometry("900x600")
        win.minsize(750, 500)
        win.configure(bg=BG)
        win.transient(self)

        tk.Label(
            win,
            text="All Transactions",
            font=("Segoe UI", 22, "bold"),
            bg=BG,
            fg=TEXT
        ).pack(anchor="w", padx=30, pady=(25, 4))

        tk.Label(
            win,
            text="View all your recorded expenses",
            font=("Segoe UI", 10),
            bg=BG,
            fg=MUTED
        ).pack(anchor="w", padx=30, pady=(0, 20))

        panel = tk.Frame(
            win,
            bg=CARD,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        panel.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        columns = ("id", "title", "amount", "category", "date")
        tree = ttk.Treeview(
            panel,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        headings = {
            "id": "ID",
            "title": "Expense",
            "amount": "Amount",
            "category": "Category",
            "date": "Date"
        }

        widths = {
            "id": 60,
            "title": 250,
            "amount": 150,
            "category": 180,
            "date": 150
        }

        for col in columns:
            tree.heading(col, text=headings[col])
            tree.column(col, width=widths[col], anchor="w")

        scrollbar = ttk.Scrollbar(
            panel,
            orient="vertical",
            command=tree.yview
        )
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(15, 0),
            pady=15
        )
        scrollbar.pack(
            side="right",
            fill="y",
            padx=(0, 15),
            pady=15
        )

        for row in self.db.all():
            tree.insert(
                "",
                "end",
                values=(
                    row[0],
                    row[1],
                    f"₹{row[2]:,.2f}",
                    row[3],
                    row[4]
                )
            )

    def refresh_table(self):
        if not hasattr(self, "tree"):
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in self.db.all(self.search_var.get().strip()):
            self.tree.insert(
                "", "end",
                values=(
                    row[0], row[1], f"₹{row[2]:,.2f}",
                    row[3], row[4]
                )
            )

    def refresh(self):
        self.refresh_table()
        total, count, categories = self.db.stats()

        self.total_card.config(text=f"₹{total:,.2f}")
        self.count_card.config(text=str(count))
        self.category_card.config(
            text=categories[0][0] if categories else "—"
        )
        self.side_total.config(text=f"₹{total:,.2f}")

        self.after(50, self.draw_chart)

    def draw_chart(self):
        self.chart.delete("all")
        width = max(self.chart.winfo_width(), 300)
        height = max(self.chart.winfo_height(), 230)
        _, _, categories = self.db.stats()

        if not categories:
            self.chart.create_text(
                width / 2, height / 2,
                text="No spending data yet",
                fill=MUTED, font=("Segoe UI", 11)
            )
            return

        total = sum(x[1] for x in categories)
        max_amount = max(x[1] for x in categories)
        colors = [
            "#5B5FEF", "#20A779", "#F4B740", "#E95464",
            "#4C9AFF", "#A56EFF"
        ]

        left, right = 145, width - 28
        bar_width = max(right - left, 100)

        for i, (category, amount) in enumerate(categories[:6]):
            y = 25 + i * 43
            percent = amount / total if total else 0

            self.chart.create_text(
                8, y + 9, text=category[:17],
                anchor="w", fill=TEXT,
                font=("Segoe UI", 9)
            )

            self.chart.create_rectangle(
                left, y, right, y + 17,
                fill="#F0F2F7", outline=""
            )

            self.chart.create_rectangle(
                left, y,
                left + bar_width * amount / max_amount, y + 17,
                fill=colors[i % len(colors)], outline=""
            )

            self.chart.create_text(
                right, y + 8, text=f"{percent:.0%}",
                anchor="e", fill=MUTED,
                font=("Segoe UI", 8, "bold")
            )

    def close_app(self):
        self.db.close()
        self.destroy()


if __name__ == "__main__":
    app = ExpenseApp()
    app.mainloop()

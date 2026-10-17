import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import mysql.connector as s
import os
from connection import get_connection, hash_password, verify_password, init_db
import book_management as bm
import students_management as sm
import issue_return as ir
import importlib

# Dynamic import for library report module with space in filename
try:
    lr = importlib.import_module("library report")
except ImportError:
    lr = None


class LibraryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Library & Student Management System")
        self.geometry("1120x720")
        self.minsize(980, 620)

        # Apply modern style configuration
        self.setup_styles()

        # Current logged in user info
        self.current_user = None

        # Container for screens
        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)

        # Initialize database automatically on startup
        ok, msg = init_db()
        if not ok:
            messagebox.showwarning(
                "Database Notice",
                f"Could not automatically initialize database:\n{msg}\n\n"
                "Please ensure that your MySQL server is running on 127.0.0.1:3306."
            )

        # Show Login Screen first
        self.show_login_screen()

    def setup_styles(self):
        self.style = ttk.Style(self)
        if "clam" in self.style.theme_names():
            self.style.theme_use("clam")

        self.configure(bg="#F1F5F9")
        self.style.configure(".", background="#F1F5F9", font=("Segoe UI", 10))

        # Frames
        self.style.configure("Card.TFrame", background="#FFFFFF", relief="flat")
        self.style.configure("Header.TFrame", background="#1E293B")
        self.style.configure("Sidebar.TFrame", background="#1E293B")

        # Buttons
        self.style.configure(
            "Primary.TButton",
            background="#2563EB",
            foreground="#FFFFFF",
            font=("Segoe UI", 10, "bold"),
            borderwidth=0,
            padding=6
        )
        self.style.map("Primary.TButton", background=[("active", "#1D4ED8")])

        self.style.configure(
            "Success.TButton",
            background="#10B981",
            foreground="#FFFFFF",
            font=("Segoe UI", 10, "bold"),
            borderwidth=0,
            padding=6
        )
        self.style.map("Success.TButton", background=[("active", "#059669")])

        self.style.configure(
            "Danger.TButton",
            background="#EF4444",
            foreground="#FFFFFF",
            font=("Segoe UI", 10, "bold"),
            borderwidth=0,
            padding=6
        )
        self.style.map("Danger.TButton", background=[("active", "#DC2626")])

        # Treeview styling
        self.style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 10, "bold"),
            background="#E2E8F0",
            foreground="#1E293B"
        )
        self.style.configure(
            "Treeview",
            rowheight=26,
            font=("Segoe UI", 9),
            background="#FFFFFF",
            fieldbackground="#FFFFFF"
        )

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    # ==========================================================
    # LOGIN & REGISTRATION SCREEN
    # ==========================================================
    def show_login_screen(self):
        self.clear_container()

        center_frame = tk.Frame(self.container, bg="#F1F5F9")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        card = tk.Frame(center_frame, bg="#FFFFFF", padx=35, pady=30, highlightthickness=1, highlightbackground="#CBD5E1")
        card.pack()

        tk.Label(card, text="📚", font=("Segoe UI", 32), bg="#FFFFFF").pack()
        tk.Label(card, text="LIBRARY MANAGEMENT SYSTEM", font=("Segoe UI", 14, "bold"), fg="#1E293B", bg="#FFFFFF").pack(pady=(5, 2))
        self.auth_subtitle = tk.Label(card, text="Please login to your account", font=("Segoe UI", 10), fg="#64748B", bg="#FFFFFF")
        self.auth_subtitle.pack(pady=(0, 20))

        self.auth_form = tk.Frame(card, bg="#FFFFFF")
        self.auth_form.pack(fill="x")

        self.is_register_mode = False
        self.render_auth_form()

    def render_auth_form(self):
        for w in self.auth_form.winfo_children():
            w.destroy()

        if not self.is_register_mode:
            # LOGIN MODE
            self.auth_subtitle.config(text="Enter your credentials to access the system")

            tk.Label(self.auth_form, text="Username", font=("Segoe UI", 9, "bold"), fg="#334155", bg="#FFFFFF", anchor="w").pack(fill="x")
            self.login_user_entry = ttk.Entry(self.auth_form, width=32, font=("Segoe UI", 10))
            self.login_user_entry.pack(fill="x", pady=(2, 12))
            default_user = os.getenv("DEFAULT_ADMIN_USER", "")
            if default_user:
                self.login_user_entry.insert(0, default_user)

            tk.Label(self.auth_form, text="Password", font=("Segoe UI", 9, "bold"), fg="#334155", bg="#FFFFFF", anchor="w").pack(fill="x")
            self.login_pwd_entry = ttk.Entry(self.auth_form, width=32, show="•", font=("Segoe UI", 10))
            self.login_pwd_entry.pack(fill="x", pady=(2, 8))

            # Show password toggle
            self.show_pwd_var = tk.BooleanVar(value=False)
            chk = tk.Checkbutton(
                self.auth_form,
                text="Show Password",
                variable=self.show_pwd_var,
                bg="#FFFFFF",
                fg="#64748B",
                font=("Segoe UI", 9),
                activebackground="#FFFFFF",
                command=lambda: self.login_pwd_entry.config(show="" if self.show_pwd_var.get() else "•")
            )
            chk.pack(anchor="w", pady=(0, 15))

            btn_login = ttk.Button(self.auth_form, text="Log In", style="Primary.TButton", command=self.handle_login)
            btn_login.pack(fill="x", pady=(0, 10))

            toggle_frame = tk.Frame(self.auth_form, bg="#FFFFFF")
            toggle_frame.pack(fill="x")
            tk.Label(toggle_frame, text="Need a new account?", fg="#64748B", bg="#FFFFFF", font=("Segoe UI", 9)).pack(side="left")
            btn_toggle = tk.Button(
                toggle_frame,
                text="Register here",
                fg="#2563EB",
                bg="#FFFFFF",
                font=("Segoe UI", 9, "bold"),
                bd=0,
                cursor="hand2",
                command=self.switch_to_register
            )
            btn_toggle.pack(side="left", padx=5)

            self.login_pwd_entry.bind("<Return>", lambda e: self.handle_login())
            self.login_user_entry.bind("<Return>", lambda e: self.login_pwd_entry.focus())
            self.login_user_entry.focus()

        else:
            # REGISTER MODE
            self.auth_subtitle.config(text="Create a new administrator or staff account")

            tk.Label(self.auth_form, text="Full Name", font=("Segoe UI", 9, "bold"), fg="#334155", bg="#FFFFFF", anchor="w").pack(fill="x")
            self.reg_fullname_entry = ttk.Entry(self.auth_form, width=32, font=("Segoe UI", 10))
            self.reg_fullname_entry.pack(fill="x", pady=(2, 10))

            tk.Label(self.auth_form, text="Unique Username", font=("Segoe UI", 9, "bold"), fg="#334155", bg="#FFFFFF", anchor="w").pack(fill="x")
            self.reg_user_entry = ttk.Entry(self.auth_form, width=32, font=("Segoe UI", 10))
            self.reg_user_entry.pack(fill="x", pady=(2, 10))

            tk.Label(self.auth_form, text="Password", font=("Segoe UI", 9, "bold"), fg="#334155", bg="#FFFFFF", anchor="w").pack(fill="x")
            self.reg_pwd_entry = ttk.Entry(self.auth_form, width=32, show="•", font=("Segoe UI", 10))
            self.reg_pwd_entry.pack(fill="x", pady=(2, 10))

            tk.Label(self.auth_form, text="Role", font=("Segoe UI", 9, "bold"), fg="#334155", bg="#FFFFFF", anchor="w").pack(fill="x")
            self.reg_role_combo = ttk.Combobox(self.auth_form, values=["Admin", "Librarian", "Staff"], state="readonly")
            self.reg_role_combo.set("Admin")
            self.reg_role_combo.pack(fill="x", pady=(2, 15))

            btn_register = ttk.Button(self.auth_form, text="Create Account", style="Success.TButton", command=self.handle_register)
            btn_register.pack(fill="x", pady=(0, 10))

            toggle_frame = tk.Frame(self.auth_form, bg="#FFFFFF")
            toggle_frame.pack(fill="x")
            tk.Label(toggle_frame, text="Already have an account?", fg="#64748B", bg="#FFFFFF", font=("Segoe UI", 9)).pack(side="left")
            btn_toggle = tk.Button(
                toggle_frame,
                text="Log In",
                fg="#2563EB",
                bg="#FFFFFF",
                font=("Segoe UI", 9, "bold"),
                bd=0,
                cursor="hand2",
                command=self.switch_to_login
            )
            btn_toggle.pack(side="left", padx=5)

    def switch_to_register(self):
        self.is_register_mode = True
        self.render_auth_form()

    def switch_to_login(self):
        self.is_register_mode = False
        self.render_auth_form()

    def handle_login(self):
        username = self.login_user_entry.get().strip()
        password = self.login_pwd_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Input Required", "Please enter both username and password.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor(buffered=True)
            cursor.execute(
                "SELECT USER_ID, USERNAME, PASSWORD_HASH, FULL_NAME, ROLE FROM users WHERE USERNAME = %s",
                (username,)
            )
            user_row = cursor.fetchone()

            if user_row and verify_password(password, user_row[2]):
                self.current_user = {
                    "user_id": user_row[0],
                    "username": user_row[1],
                    "fullname": user_row[3],
                    "role": user_row[4]
                }
                cursor.close()
                conn.close()
                self.show_main_dashboard()
            else:
                cursor.close()
                conn.close()
                messagebox.showerror("Login Failed", "Invalid username or password.")

        except s.Error as e:
            messagebox.showerror("Database Error", f"Could not connect to database:\n{e}")

    def handle_register(self):
        fullname = self.reg_fullname_entry.get().strip()
        username = self.reg_user_entry.get().strip()
        password = self.reg_pwd_entry.get().strip()
        role = self.reg_role_combo.get().strip()

        if not fullname or not username or not password:
            messagebox.showwarning("Validation Error", "All fields are required.")
            return

        if len(password) < 4:
            messagebox.showwarning("Password Notice", "Password must be at least 4 characters.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT USER_ID FROM users WHERE USERNAME = %s", (username,))
            if cursor.fetchone():
                messagebox.showerror("Duplicate Username", f"Username '{username}' is already taken.")
                cursor.close()
                conn.close()
                return

            pwd_hash = hash_password(password)
            cursor.execute(
                """
                INSERT INTO users (USERNAME, PASSWORD_HASH, FULL_NAME, ROLE)
                VALUES (%s, %s, %s, %s)
                """,
                (username, pwd_hash, fullname, role)
            )
            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo("Success", f"Account '{username}' created successfully! You can now log in.")
            self.switch_to_login()

        except s.Error as e:
            messagebox.showerror("Database Error", f"Registration failed:\n{e}")

    # ==========================================================
    # MAIN DASHBOARD SHELL
    # ==========================================================
    def show_main_dashboard(self):
        self.clear_container()

        # Top Header Bar
        header = tk.Frame(self.container, bg="#1E293B", height=60, padx=20, pady=10)
        header.pack(fill="x", side="top")

        tk.Label(header, text="📖 LIBRARY & STUDENT MANAGEMENT SYSTEM", font=("Segoe UI", 13, "bold"), fg="#FFFFFF", bg="#1E293B").pack(side="left")

        user_info = f"👤 {self.current_user['fullname']} ({self.current_user['role']})"
        tk.Label(header, text=user_info, font=("Segoe UI", 10), fg="#94A3B8", bg="#1E293B").pack(side="right", padx=(10, 15))

        tk.Button(
            header,
            text="Log Out",
            font=("Segoe UI", 9, "bold"),
            fg="#FFFFFF",
            bg="#EF4444",
            activebackground="#DC2626",
            activeforeground="#FFFFFF",
            bd=0,
            padx=10,
            pady=3,
            cursor="hand2",
            command=self.show_login_screen
        ).pack(side="right")

        # Body Layout: Sidebar + Main Content Area
        body = tk.Frame(self.container, bg="#F1F5F9")
        body.pack(fill="both", expand=True)

        sidebar = tk.Frame(body, bg="#1E293B", width=220)
        sidebar.pack(fill="y", side="left")
        sidebar.pack_propagate(False)

        self.content_area = tk.Frame(body, bg="#F1F5F9", padx=25, pady=20)
        self.content_area.pack(fill="both", expand=True, side="right")

        self.nav_buttons = {}
        nav_items = [
            ("dashboard", "📊  Dashboard"),
            ("books", "📚  Books Management"),
            ("students", "🎓  Students Management"),
            ("issue_return", "🔄  Issue & Return"),
            ("reports", "📈  Reports & Analytics")
        ]

        tk.Label(sidebar, text="MAIN NAVIGATION", font=("Segoe UI", 8, "bold"), fg="#64748B", bg="#1E293B", anchor="w", padx=20, pady=12).pack(fill="x")

        for key, text in nav_items:
            btn = tk.Button(
                sidebar,
                text=text,
                font=("Segoe UI", 10),
                fg="#E2E8F0",
                bg="#1E293B",
                activebackground="#334155",
                activeforeground="#FFFFFF",
                bd=0,
                anchor="w",
                padx=20,
                pady=11,
                cursor="hand2",
                command=lambda k=key: self.switch_view(k)
            )
            btn.pack(fill="x")
            self.nav_buttons[key] = btn

        self.switch_view("dashboard")

    def switch_view(self, view_name):
        for key, btn in self.nav_buttons.items():
            if key == view_name:
                btn.config(bg="#2563EB", fg="#FFFFFF", font=("Segoe UI", 10, "bold"))
            else:
                btn.config(bg="#1E293B", fg="#E2E8F0", font=("Segoe UI", 10))

        for w in self.content_area.winfo_children():
            w.destroy()

        if view_name == "dashboard":
            self.render_dashboard_view()
        elif view_name == "books":
            self.render_books_view()
        elif view_name == "students":
            self.render_students_view()
        elif view_name == "issue_return":
            self.render_issue_return_view()
        elif view_name == "reports":
            self.render_reports_view()

    # ==========================================================
    # 1. DASHBOARD VIEW
    # ==========================================================
    def render_dashboard_view(self):
        head = tk.Frame(self.content_area, bg="#F1F5F9")
        head.pack(fill="x", pady=(0, 20))
        tk.Label(head, text="Dashboard Overview", font=("Segoe UI", 16, "bold"), fg="#1E293B", bg="#F1F5F9").pack(side="left")
        
        ttk.Button(head, text="🔄 Refresh Data", style="Primary.TButton", command=self.render_dashboard_view).pack(side="right")

        # Metrics using backend library report
        summary = lr.get_summary() if lr else {}
        cards_frame = tk.Frame(self.content_area, bg="#F1F5F9")
        cards_frame.pack(fill="x", pady=(0, 25))

        kpis = [
            ("Total Titles", summary.get("total_titles", 0), "📚", "#2563EB"),
            ("Total Copies", summary.get("total_copies", 0), "📦", "#0284C7"),
            ("Currently Issued", summary.get("issued_books", 0), "📖", "#F59E0B"),
            ("Active Students", summary.get("active_students", 0), "🎓", "#10B981"),
            ("Overdue Books", summary.get("overdue_books", 0), "⚠️", "#EF4444"),
            ("Pending Fines", f"Rs. {summary.get('pending_fines', 0.0):.2f}", "💰", "#8B5CF6")
        ]

        for i, (title, val, icon, color) in enumerate(kpis):
            col = i % 3
            row = i // 3
            card = tk.Frame(cards_frame, bg="#FFFFFF", padx=20, pady=16, highlightthickness=1, highlightbackground="#E2E8F0")
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            cards_frame.columnconfigure(col, weight=1)

            top = tk.Frame(card, bg="#FFFFFF")
            top.pack(fill="x")
            tk.Label(top, text=title, font=("Segoe UI", 9, "bold"), fg="#64748B", bg="#FFFFFF").pack(side="left")
            tk.Label(top, text=icon, font=("Segoe UI", 14), bg="#FFFFFF").pack(side="right")
            tk.Label(card, text=str(val), font=("Segoe UI", 18, "bold"), fg=color, bg="#FFFFFF").pack(anchor="w", pady=(8, 0))

        # Recent Active Loans Table
        act_card = tk.Frame(self.content_area, bg="#FFFFFF", padx=20, pady=18, highlightthickness=1, highlightbackground="#E2E8F0")
        act_card.pack(fill="both", expand=True)

        tk.Label(act_card, text="Recent Active Issued Books", font=("Segoe UI", 12, "bold"), fg="#1E293B", bg="#FFFFFF").pack(anchor="w", pady=(0, 10))

        cols = ("Issue ID", "Student Name", "Book Name", "Issue Date", "Due Date", "Status / Days")
        tree = ttk.Treeview(act_card, columns=cols, show="headings", height=8)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, anchor="center", width=140)
        tree.column("Student Name", anchor="w", width=180)
        tree.column("Book Name", anchor="w", width=200)
        tree.pack(fill="both", expand=True)

        try:
            today = datetime.date.today()
            active_list = ir.get_active_issues()[:10]
            for r in active_list:
                days_diff = (r[6] - today).days
                st_text = f"OVERDUE ({abs(days_diff)}d)" if days_diff < 0 else f"{days_diff} days left"
                tree.insert("", "end", values=(r[0], r[2], r[4], str(r[5]), str(r[6]), st_text))
        except Exception:
            pass

    # ==========================================================
    # 2. BOOK MANAGEMENT VIEW
    # ==========================================================
    def render_books_view(self):
        head = tk.Frame(self.content_area, bg="#F1F5F9")
        head.pack(fill="x", pady=(0, 15))
        tk.Label(head, text="📚 Books Management", font=("Segoe UI", 16, "bold"), fg="#1E293B", bg="#F1F5F9").pack(side="left")

        ttk.Button(head, text="➕ Add Book", style="Success.TButton", command=self.dialog_add_book).pack(side="right", padx=5)
        ttk.Button(head, text="✏️ Update Selected", style="Primary.TButton", command=self.dialog_update_book).pack(side="right", padx=5)
        ttk.Button(head, text="🚫 Deactivate Book", style="Danger.TButton", command=self.deactivate_selected_book).pack(side="right", padx=5)

        # Search Bar
        search_frame = tk.Frame(self.content_area, bg="#FFFFFF", padx=15, pady=12, highlightthickness=1, highlightbackground="#CBD5E1")
        search_frame.pack(fill="x", pady=(0, 15))

        tk.Label(search_frame, text="Search Book:", font=("Segoe UI", 9, "bold"), fg="#334155", bg="#FFFFFF").pack(side="left", padx=(0, 10))
        self.book_search_var = tk.StringVar()
        book_search_entry = ttk.Entry(search_frame, textvariable=self.book_search_var, width=35)
        book_search_entry.pack(side="left", padx=(0, 10))
        book_search_entry.bind("<KeyRelease>", lambda e: self.load_books_data())

        ttk.Button(search_frame, text="Clear", command=lambda: [self.book_search_var.set(""), self.load_books_data()]).pack(side="left")

        # Table Card
        table_card = tk.Frame(self.content_area, bg="#FFFFFF", padx=15, pady=15, highlightthickness=1, highlightbackground="#CBD5E1")
        table_card.pack(fill="both", expand=True)

        cols = ("Book ID", "Book Name", "Class", "Available Copies", "Status")
        self.books_tree = ttk.Treeview(table_card, columns=cols, show="headings", selectmode="browse")

        for c in cols:
            self.books_tree.heading(c, text=c)
            self.books_tree.column(c, anchor="center", width=120)
        self.books_tree.column("Book Name", anchor="w", width=320)

        sb = ttk.Scrollbar(table_card, orient="vertical", command=self.books_tree.yview)
        self.books_tree.configure(yscrollcommand=sb.set)

        self.books_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self.load_books_data()

    def load_books_data(self):
        for item in self.books_tree.get_children():
            self.books_tree.delete(item)

        q = self.book_search_var.get().strip()
        try:
            records = bm.get_books(q)
            for r in records:
                self.books_tree.insert("", "end", values=(r[0], r[1], r[2], r[3], r[4]))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load books: {e}")

    def dialog_add_book(self):
        dialog = tk.Toplevel(self)
        dialog.title("Add New Book")
        dialog.geometry("400x340")
        dialog.configure(bg="#FFFFFF")
        dialog.transient(self)
        dialog.grab_set()

        tk.Label(dialog, text="Add New Book Record", font=("Segoe UI", 12, "bold"), fg="#1E293B", bg="#FFFFFF").pack(pady=(15, 15))

        f = tk.Frame(dialog, bg="#FFFFFF", padx=25)
        f.pack(fill="both", expand=True)

        tk.Label(f, text="Book Name", font=("Segoe UI", 9, "bold"), fg="#334155", bg="#FFFFFF", anchor="w").pack(fill="x")
        name_entry = ttk.Entry(f)
        name_entry.pack(fill="x", pady=(2, 10))

        tk.Label(f, text="Class / Category", font=("Segoe UI", 9, "bold"), fg="#334155", bg="#FFFFFF", anchor="w").pack(fill="x")
        class_entry = ttk.Entry(f)
        class_entry.pack(fill="x", pady=(2, 10))

        tk.Label(f, text="Available Quantity", font=("Segoe UI", 9, "bold"), fg="#334155", bg="#FFFFFF", anchor="w").pack(fill="x")
        qty_entry = ttk.Entry(f)
        qty_entry.insert(0, "1")
        qty_entry.pack(fill="x", pady=(2, 15))

        def save():
            name = name_entry.get().strip()
            cls_name = class_entry.get().strip()
            try:
                qty = int(qty_entry.get().strip())
            except ValueError:
                messagebox.showwarning("Validation Error", "Quantity must be an integer.", parent=dialog)
                return

            ok, msg, _ = bm.add_book(name, cls_name, qty)
            if ok:
                messagebox.showinfo("Success", msg, parent=dialog)
                dialog.destroy()
                self.load_books_data()
            else:
                messagebox.showerror("Error", msg, parent=dialog)

        ttk.Button(f, text="Save Book", style="Success.TButton", command=save).pack(fill="x")

    def dialog_update_book(self):
        sel = self.books_tree.selection()
        if not sel:
            messagebox.showwarning("Selection Required", "Please select a book row to update.")
            return

        item = self.books_tree.item(sel[0])
        book_id, book_name, book_class, book_qty, _ = item["values"]

        dialog = tk.Toplevel(self)
        dialog.title(f"Update Book #{book_id}")
        dialog.geometry("400x340")
        dialog.configure(bg="#FFFFFF")
        dialog.transient(self)
        dialog.grab_set()

        tk.Label(dialog, text=f"Update Book (ID: {book_id})", font=("Segoe UI", 12, "bold"), fg="#1E293B", bg="#FFFFFF").pack(pady=(15, 15))

        f = tk.Frame(dialog, bg="#FFFFFF", padx=25)
        f.pack(fill="both", expand=True)

        tk.Label(f, text="Book Name", font=("Segoe UI", 9, "bold"), fg="#334155", bg="#FFFFFF", anchor="w").pack(fill="x")
        name_entry = ttk.Entry(f)
        name_entry.insert(0, book_name)
        name_entry.pack(fill="x", pady=(2, 10))

        tk.Label(f, text="Class / Category", font=("Segoe UI", 9, "bold"), fg="#334155", bg="#FFFFFF", anchor="w").pack(fill="x")
        class_entry = ttk.Entry(f)
        class_entry.insert(0, book_class)
        class_entry.pack(fill="x", pady=(2, 10))

        tk.Label(f, text="Available Quantity", font=("Segoe UI", 9, "bold"), fg="#334155", bg="#FFFFFF", anchor="w").pack(fill="x")
        qty_entry = ttk.Entry(f)
        qty_entry.insert(0, str(book_qty))
        qty_entry.pack(fill="x", pady=(2, 15))

        def update():
            name = name_entry.get().strip()
            cls_name = class_entry.get().strip()
            try:
                qty = int(qty_entry.get().strip())
            except ValueError:
                messagebox.showwarning("Validation Error", "Quantity must be an integer.", parent=dialog)
                return

            ok, msg = bm.update_book(book_id, name, cls_name, qty)
            if ok:
                messagebox.showinfo("Success", msg, parent=dialog)
                dialog.destroy()
                self.load_books_data()
            else:
                messagebox.showerror("Error", msg, parent=dialog)

        ttk.Button(f, text="Update Details", style="Primary.TButton", command=update).pack(fill="x")

    def deactivate_selected_book(self):
        sel = self.books_tree.selection()
        if not sel:
            messagebox.showwarning("Selection Required", "Please select a book to deactivate.")
            return

        item = self.books_tree.item(sel[0])
        book_id, book_name, _, _, book_status = item["values"]

        if book_status == "INACTIVE":
            messagebox.showinfo("Already Inactive", "This book is already marked as INACTIVE.")
            return

        confirm = messagebox.askyesno(
            "Confirm Deactivation",
            f"Are you sure you want to deactivate '{book_name}' (ID: {book_id})?\n"
            "Quantity will be set to 0 and status set to INACTIVE."
        )
        if not confirm:
            return

        ok, msg = bm.deactivate_book(book_id)
        if ok:
            messagebox.showinfo("Success", msg)
            self.load_books_data()
        else:
            messagebox.showerror("Error", msg)

    # ==========================================================
    # 3. STUDENT MANAGEMENT VIEW
    # ==========================================================
    def render_students_view(self):
        head = tk.Frame(self.content_area, bg="#F1F5F9")
        head.pack(fill="x", pady=(0, 15))
        tk.Label(head, text="🎓 Students Management", font=("Segoe UI", 16, "bold"), fg="#1E293B", bg="#F1F5F9").pack(side="left")

        ttk.Button(head, text="➕ Add Student", style="Success.TButton", command=self.dialog_add_student).pack(side="right", padx=5)
        ttk.Button(head, text="✏️ Update Selected", style="Primary.TButton", command=self.dialog_update_student).pack(side="right", padx=5)
        ttk.Button(head, text="📜 TC / Status Toggle", style="Danger.TButton", command=self.dialog_tc_status_student).pack(side="right", padx=5)

        # Search Bar
        search_frame = tk.Frame(self.content_area, bg="#FFFFFF", padx=15, pady=12, highlightthickness=1, highlightbackground="#CBD5E1")
        search_frame.pack(fill="x", pady=(0, 15))

        tk.Label(search_frame, text="Search Student:", font=("Segoe UI", 9, "bold"), fg="#334155", bg="#FFFFFF").pack(side="left", padx=(0, 10))
        self.student_search_var = tk.StringVar()
        student_search_entry = ttk.Entry(search_frame, textvariable=self.student_search_var, width=35)
        student_search_entry.pack(side="left", padx=(0, 10))
        student_search_entry.bind("<KeyRelease>", lambda e: self.load_students_data())

        ttk.Button(search_frame, text="Clear", command=lambda: [self.student_search_var.set(""), self.load_students_data()]).pack(side="left")

        # Table Card
        table_card = tk.Frame(self.content_area, bg="#FFFFFF", padx=15, pady=15, highlightthickness=1, highlightbackground="#CBD5E1")
        table_card.pack(fill="both", expand=True)

        cols = ("SRNO", "Name", "Class", "Sec", "Address", "Parents Name", "Mobile No", "TC Issued", "Status")
        self.students_tree = ttk.Treeview(table_card, columns=cols, show="headings", selectmode="browse")

        for c in cols:
            self.students_tree.heading(c, text=c)
            self.students_tree.column(c, anchor="center", width=95)
        self.students_tree.column("Name", anchor="w", width=140)
        self.students_tree.column("Address", anchor="w", width=160)
        self.students_tree.column("Parents Name", anchor="w", width=140)

        sb = ttk.Scrollbar(table_card, orient="vertical", command=self.students_tree.yview)
        self.students_tree.configure(yscrollcommand=sb.set)

        self.students_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self.load_students_data()

    def load_students_data(self):
        for item in self.students_tree.get_children():
            self.students_tree.delete(item)

        q = self.student_search_var.get().strip()
        try:
            records = sm.get_students(q)
            for r in records:
                tc_str = "YES" if r[7] else "NO"
                self.students_tree.insert(
                    "",
                    "end",
                    values=(r[0], r[1], r[2], r[3], r[4], r[5], r[6], tc_str, r[8])
                )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load students: {e}")

    def dialog_add_student(self):
        dialog = tk.Toplevel(self)
        dialog.title("Add New Student")
        dialog.geometry("450x460")
        dialog.configure(bg="#FFFFFF")
        dialog.transient(self)
        dialog.grab_set()

        tk.Label(dialog, text="Add New Student Record", font=("Segoe UI", 12, "bold"), fg="#1E293B", bg="#FFFFFF").pack(pady=(15, 12))

        f = tk.Frame(dialog, bg="#FFFFFF", padx=25)
        f.pack(fill="both", expand=True)

        tk.Label(f, text="Student Name", font=("Segoe UI", 9, "bold"), fg="#334155", bg="#FFFFFF", anchor="w").pack(fill="x")
        name_e = ttk.Entry(f)
        name_e.pack(fill="x", pady=(2, 8))

        row1 = tk.Frame(f, bg="#FFFFFF")
        row1.pack(fill="x", pady=(0, 8))
        tk.Label(row1, text="Class", font=("Segoe UI", 9, "bold"), fg="#334155", bg="#FFFFFF", anchor="w").grid(row=0, column=0, sticky="w")
        tk.Label(row1, text="Section", font=("Segoe UI", 9, "bold"), fg="#334155", bg="#FFFFFF", anchor="w").grid(row=0, column=1, sticky="w", padx=(10, 0))
        class_e = ttk.Entry(row1, width=18)
        class_e.grid(row=1, column=0, sticky="w")
        sec_combo = ttk.Combobox(row1, values=["A", "B", "C"], width=12, state="readonly")
        sec_combo.set("A")
        sec_combo.grid(row=1, column=1, sticky="w", padx=(10, 0))

        tk.Label(f, text="Address", font=("Segoe UI", 9, "bold"), fg="#334155", bg="#FFFFFF", anchor="w").pack(fill="x")
        addr_e = ttk.Entry(f)
        addr_e.pack(fill="x", pady=(2, 8))

        tk.Label(f, text="Parent's Name", font=("Segoe UI", 9, "bold"), fg="#334155", bg="#FFFFFF", anchor="w").pack(fill="x")
        parent_e = ttk.Entry(f)
        parent_e.pack(fill="x", pady=(2, 8))

        tk.Label(f, text="Mobile Number", font=("Segoe UI", 9, "bold"), fg="#334155", bg="#FFFFFF", anchor="w").pack(fill="x")
        mob_e = ttk.Entry(f)
        mob_e.pack(fill="x", pady=(2, 15))

        def save():
            ok, msg, _ = sm.add_student(
                name_e.get(),
                class_e.get(),
                sec_combo.get(),
                addr_e.get(),
                parent_e.get(),
                mob_e.get()
            )
            if ok:
                messagebox.showinfo("Success", msg, parent=dialog)
                dialog.destroy()
                self.load_students_data()
            else:
                messagebox.showerror("Error", msg, parent=dialog)

        ttk.Button(f, text="Save Student", style="Success.TButton", command=save).pack(fill="x")

    def dialog_update_student(self):
        sel = self.students_tree.selection()
        if not sel:
            messagebox.showwarning("Selection Required", "Please select a student row to update.")
            return

        item = self.students_tree.item(sel[0])
        srno, name, cls, sec, addr, parent, mob, _, _ = item["values"]

        dialog = tk.Toplevel(self)
        dialog.title(f"Update Student #{srno}")
        dialog.geometry("450x460")
        dialog.configure(bg="#FFFFFF")
        dialog.transient(self)
        dialog.grab_set()

        tk.Label(dialog, text=f"Update Student (SRNO: {srno})", font=("Segoe UI", 12, "bold"), fg="#1E293B", bg="#FFFFFF").pack(pady=(15, 12))

        f = tk.Frame(dialog, bg="#FFFFFF", padx=25)
        f.pack(fill="both", expand=True)

        tk.Label(f, text="Student Name", font=("Segoe UI", 9, "bold"), fg="#334155", bg="#FFFFFF", anchor="w").pack(fill="x")
        name_e = ttk.Entry(f)
        name_e.insert(0, name)
        name_e.pack(fill="x", pady=(2, 8))

        row1 = tk.Frame(f, bg="#FFFFFF")
        row1.pack(fill="x", pady=(0, 8))
        tk.Label(row1, text="Class", font=("Segoe UI", 9, "bold"), fg="#334155", bg="#FFFFFF", anchor="w").grid(row=0, column=0, sticky="w")
        tk.Label(row1, text="Section", font=("Segoe UI", 9, "bold"), fg="#334155", bg="#FFFFFF", anchor="w").grid(row=0, column=1, sticky="w", padx=(10, 0))
        class_e = ttk.Entry(row1, width=18)
        class_e.insert(0, cls)
        class_e.grid(row=1, column=0, sticky="w")
        sec_combo = ttk.Combobox(row1, values=["A", "B", "C"], width=12, state="readonly")
        sec_combo.set(sec if sec in ["A", "B", "C"] else "A")
        sec_combo.grid(row=1, column=1, sticky="w", padx=(10, 0))

        tk.Label(f, text="Address", font=("Segoe UI", 9, "bold"), fg="#334155", bg="#FFFFFF", anchor="w").pack(fill="x")
        addr_e = ttk.Entry(f)
        addr_e.insert(0, addr)
        addr_e.pack(fill="x", pady=(2, 8))

        tk.Label(f, text="Parent's Name", font=("Segoe UI", 9, "bold"), fg="#334155", bg="#FFFFFF", anchor="w").pack(fill="x")
        parent_e = ttk.Entry(f)
        parent_e.insert(0, parent)
        parent_e.pack(fill="x", pady=(2, 8))

        tk.Label(f, text="Mobile Number", font=("Segoe UI", 9, "bold"), fg="#334155", bg="#FFFFFF", anchor="w").pack(fill="x")
        mob_e = ttk.Entry(f)
        mob_e.insert(0, str(mob))
        mob_e.pack(fill="x", pady=(2, 15))

        def update():
            ok, msg = sm.update_student(
                srno,
                name_e.get(),
                class_e.get(),
                sec_combo.get(),
                addr_e.get(),
                parent_e.get(),
                mob_e.get()
            )
            if ok:
                messagebox.showinfo("Success", msg, parent=dialog)
                dialog.destroy()
                self.load_students_data()
            else:
                messagebox.showerror("Error", msg, parent=dialog)

        ttk.Button(f, text="Update Student", style="Primary.TButton", command=update).pack(fill="x")

    def dialog_tc_status_student(self):
        sel = self.students_tree.selection()
        if not sel:
            messagebox.showwarning("Selection Required", "Please select a student row first.")
            return

        item = self.students_tree.item(sel[0])
        srno, name, _, _, _, _, _, tc, status = item["values"]

        dialog = tk.Toplevel(self)
        dialog.title(f"TC & Status - {name}")
        dialog.geometry("380x250")
        dialog.configure(bg="#FFFFFF")
        dialog.transient(self)
        dialog.grab_set()

        tk.Label(dialog, text=f"Student TC / Status: {name}", font=("Segoe UI", 11, "bold"), fg="#1E293B", bg="#FFFFFF").pack(pady=(15, 10))

        f = tk.Frame(dialog, bg="#FFFFFF", padx=25)
        f.pack(fill="both", expand=True)

        tk.Label(f, text=f"Current Status: {status} | TC Issued: {tc}", font=("Segoe UI", 9), fg="#64748B", bg="#FFFFFF").pack(anchor="w", pady=(0, 15))

        tk.Label(f, text="Change TC Issued Status:", font=("Segoe UI", 9, "bold"), fg="#334155", bg="#FFFFFF", anchor="w").pack(fill="x")
        tc_combo = ttk.Combobox(f, values=["YES (Set Status to INACTIVE)", "NO (Set Status to ACTIVE)"], state="readonly")
        tc_combo.set("YES (Set Status to INACTIVE)" if tc == "NO" else "NO (Set Status to ACTIVE)")
        tc_combo.pack(fill="x", pady=(2, 20))

        def apply_tc():
            chosen = tc_combo.get()
            new_tc = 1 if "YES" in chosen else 0
            new_status = "INACTIVE" if "YES" in chosen else "Active"

            ok, msg = sm.update_tc_status(srno, new_tc, new_status)
            if ok:
                messagebox.showinfo("Success", msg, parent=dialog)
                dialog.destroy()
                self.load_students_data()
            else:
                messagebox.showerror("Error", msg, parent=dialog)

        ttk.Button(f, text="Apply Change", style="Primary.TButton", command=apply_tc).pack(fill="x")

    # ==========================================================
    # 4. ISSUE & RETURN VIEW
    # ==========================================================
    def render_issue_return_view(self):
        head = tk.Frame(self.content_area, bg="#F1F5F9")
        head.pack(fill="x", pady=(0, 15))
        tk.Label(head, text="🔄 Book Issue & Return System", font=("Segoe UI", 16, "bold"), fg="#1E293B", bg="#F1F5F9").pack(side="left")

        actions_frame = tk.Frame(self.content_area, bg="#F1F5F9")
        actions_frame.pack(fill="x", pady=(0, 15))

        # CARD 1: ISSUE BOOK
        issue_card = tk.Frame(actions_frame, bg="#FFFFFF", padx=18, pady=15, highlightthickness=1, highlightbackground="#CBD5E1")
        issue_card.pack(side="left", fill="both", expand=True, padx=(0, 8))

        tk.Label(issue_card, text="📤 Issue a Book", font=("Segoe UI", 11, "bold"), fg="#1E293B", bg="#FFFFFF").pack(anchor="w", pady=(0, 10))

        i_row1 = tk.Frame(issue_card, bg="#FFFFFF")
        i_row1.pack(fill="x", pady=2)
        tk.Label(i_row1, text="Student SRNO:", font=("Segoe UI", 9, "bold"), fg="#334155", bg="#FFFFFF", width=14, anchor="w").pack(side="left")
        self.issue_student_e = ttk.Entry(i_row1, width=16)
        self.issue_student_e.pack(side="left")

        i_row2 = tk.Frame(issue_card, bg="#FFFFFF")
        i_row2.pack(fill="x", pady=4)
        tk.Label(i_row2, text="Book SRNO (ID):", font=("Segoe UI", 9, "bold"), fg="#334155", bg="#FFFFFF", width=14, anchor="w").pack(side="left")
        self.issue_book_e = ttk.Entry(i_row2, width=16)
        self.issue_book_e.pack(side="left")

        ttk.Button(issue_card, text="Confirm Issue Book", style="Success.TButton", command=self.handle_gui_issue_book).pack(fill="x", pady=(10, 0))

        # CARD 2: RETURN BOOK & PAY FINE
        return_card = tk.Frame(actions_frame, bg="#FFFFFF", padx=18, pady=15, highlightthickness=1, highlightbackground="#CBD5E1")
        return_card.pack(side="right", fill="both", expand=True, padx=(8, 0))

        tk.Label(return_card, text="📥 Return Book & Pay Fine", font=("Segoe UI", 11, "bold"), fg="#1E293B", bg="#FFFFFF").pack(anchor="w", pady=(0, 10))

        r_row1 = tk.Frame(return_card, bg="#FFFFFF")
        r_row1.pack(fill="x", pady=2)
        tk.Label(r_row1, text="Enter Issue ID:", font=("Segoe UI", 9, "bold"), fg="#334155", bg="#FFFFFF", width=14, anchor="w").pack(side="left")
        self.return_issue_id_e = ttk.Entry(r_row1, width=16)
        self.return_issue_id_e.pack(side="left")

        btn_box = tk.Frame(return_card, bg="#FFFFFF")
        btn_box.pack(fill="x", pady=(10, 0))
        ttk.Button(btn_box, text="Return Book", style="Primary.TButton", command=self.handle_gui_return_book).pack(side="left", fill="x", expand=True, padx=(0, 4))
        ttk.Button(btn_box, text="Pay Fine", style="Success.TButton", command=self.handle_gui_pay_fine).pack(side="right", fill="x", expand=True, padx=(4, 0))

        # Table of Currently Issued Books
        table_card = tk.Frame(self.content_area, bg="#FFFFFF", padx=15, pady=15, highlightthickness=1, highlightbackground="#CBD5E1")
        table_card.pack(fill="both", expand=True)

        t_head = tk.Frame(table_card, bg="#FFFFFF")
        t_head.pack(fill="x", pady=(0, 10))
        tk.Label(t_head, text="Active Issued Books", font=("Segoe UI", 11, "bold"), fg="#1E293B", bg="#FFFFFF").pack(side="left")
        ttk.Button(t_head, text="🔍 Check Student History", command=self.dialog_student_history).pack(side="right")

        cols = ("Issue ID", "Student ID", "Student Name", "Book ID", "Book Name", "Issue Date", "Due Date", "Current Fine")
        self.issued_tree = ttk.Treeview(table_card, columns=cols, show="headings", height=8)

        for c in cols:
            self.issued_tree.heading(c, text=c)
            self.issued_tree.column(c, anchor="center", width=110)
        self.issued_tree.column("Student Name", anchor="w", width=160)
        self.issued_tree.column("Book Name", anchor="w", width=180)

        sb = ttk.Scrollbar(table_card, orient="vertical", command=self.issued_tree.yview)
        self.issued_tree.configure(yscrollcommand=sb.set)

        self.issued_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self.load_issued_table()

    def load_issued_table(self):
        for item in self.issued_tree.get_children():
            self.issued_tree.delete(item)

        try:
            records = ir.get_active_issues()
            today = datetime.date.today()
            for r in records:
                late_days = max(0, (today - r[6]).days)
                fine_amount = late_days * 2
                fine_str = f"Rs. {fine_amount:.2f}" if fine_amount > 0 else "Rs. 0.00"

                self.issued_tree.insert(
                    "",
                    "end",
                    values=(r[0], r[1], r[2], r[3], r[4], str(r[5]), str(r[6]), fine_str)
                )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load issued books: {e}")

    def handle_gui_issue_book(self):
        st_id = self.issue_student_e.get().strip()
        bk_id = self.issue_book_e.get().strip()

        try:
            student_srno = int(st_id)
            book_id = int(bk_id)
        except ValueError:
            messagebox.showwarning("Validation Error", "Please enter valid numeric Student and Book IDs.")
            return

        ok, msg, details = ir.issue_book(student_srno, book_id)
        if ok:
            messagebox.showinfo(
                "Book Issued Successfully",
                f"Issue ID: {details['issue_id']}\n"
                f"Student: {details['student_name']}\n"
                f"Book: {details['book_name']}\n"
                f"Due Date: {details['due_date']}"
            )
            self.issue_student_e.delete(0, "end")
            self.issue_book_e.delete(0, "end")
            self.load_issued_table()
        else:
            messagebox.showerror("Notice", msg)

    def handle_gui_return_book(self):
        iss_id = self.return_issue_id_e.get().strip()
        try:
            issue_id = int(iss_id)
        except ValueError:
            messagebox.showwarning("Validation Error", "Please enter a valid numeric Issue ID.")
            return

        ok, msg, details = ir.return_book(issue_id)
        if ok:
            fine_info = f"Late Days: {details['late_days']}\nFine: Rs. {details['fine']:.2f}"
            if details['fine'] > 0:
                fine_info += " (PENDING - Click Pay Fine to settle)"
            else:
                fine_info += " (NO FINE DUE)"

            messagebox.showinfo(
                "Return Processed",
                f"Book returned successfully!\n\n"
                f"Student: {details['student_name']}\n"
                f"Book: {details['book_name']}\n"
                f"{fine_info}"
            )
            self.load_issued_table()
        else:
            messagebox.showerror("Error", msg)

    def handle_gui_pay_fine(self):
        iss_id = self.return_issue_id_e.get().strip()
        try:
            issue_id = int(iss_id)
        except ValueError:
            messagebox.showwarning("Validation Error", "Please enter a valid numeric Issue ID.")
            return

        ok, msg = ir.pay_fine(issue_id)
        if ok:
            messagebox.showinfo("Payment Successful", msg)
            self.load_issued_table()
        else:
            messagebox.showwarning("Notice", msg)

    def dialog_student_history(self):
        dialog = tk.Toplevel(self)
        dialog.title("Student Book History")
        dialog.geometry("750x450")
        dialog.configure(bg="#FFFFFF")
        dialog.transient(self)

        top_f = tk.Frame(dialog, bg="#FFFFFF", padx=15, pady=12)
        top_f.pack(fill="x")

        tk.Label(top_f, text="Student SRNO:", font=("Segoe UI", 9, "bold"), fg="#334155", bg="#FFFFFF").pack(side="left", padx=(0, 10))
        srno_e = ttk.Entry(top_f, width=15)
        srno_e.pack(side="left", padx=(0, 10))

        student_info_lbl = tk.Label(top_f, text="", font=("Segoe UI", 10, "bold"), fg="#2563EB", bg="#FFFFFF")
        student_info_lbl.pack(side="left", padx=10)

        cols = ("Issue ID", "Book", "Issued Date", "Due Date", "Returned Date", "Fine", "Paid")
        tree = ttk.Treeview(dialog, columns=cols, show="headings", height=10)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, anchor="center", width=100)
        tree.column("Book", anchor="w", width=180)

        tree.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        def search_history():
            for item in tree.get_children():
                tree.delete(item)

            val = srno_e.get().strip()
            try:
                s_id = int(val)
            except ValueError:
                messagebox.showwarning("Input Error", "Please enter a valid numeric SRNO.", parent=dialog)
                return

            res, status = ir.get_student_history(s_id)
            if not res:
                student_info_lbl.config(text=status, fg="#EF4444")
                return

            student_info_lbl.config(text=f"Student: {res['student_name']}", fg="#2563EB")
            records = res["records"]

            if not records:
                messagebox.showinfo("History", "No book history found for this student.", parent=dialog)
            else:
                for r in records:
                    ret = str(r[4]) if r[4] else "Not Returned"
                    paid_str = "PAID" if r[6] else "PENDING"
                    tree.insert("", "end", values=(r[0], r[1], str(r[2]), str(r[3]), ret, f"Rs. {float(r[5]):.2f}", paid_str))

        ttk.Button(top_f, text="Search History", style="Primary.TButton", command=search_history).pack(side="left")

    # ==========================================================
    # 5. REPORTS & ANALYTICS VIEW
    # ==========================================================
    def render_reports_view(self):
        head = tk.Frame(self.content_area, bg="#F1F5F9")
        head.pack(fill="x", pady=(0, 15))
        tk.Label(head, text="📈 Library Reports & Analytics", font=("Segoe UI", 16, "bold"), fg="#1E293B", bg="#F1F5F9").pack(side="left")

        nb = ttk.Notebook(self.content_area)
        nb.pack(fill="both", expand=True)

        tab_overdue = ttk.Frame(nb, padding=15)
        tab_fines = ttk.Frame(nb, padding=15)
        tab_monthly = ttk.Frame(nb, padding=15)

        nb.add(tab_overdue, text=" ⚠️ Overdue Books ")
        nb.add(tab_fines, text=" 💰 Pending Fines ")
        nb.add(tab_monthly, text=" 📅 Monthly Summary ")

        # TAB 1: Overdue Books Table
        cols1 = ("Issue ID", "SRNO", "Student Name", "Mobile", "Book Name", "Due Date", "Days Late", "Fine (Rs.)")
        tree_overdue = ttk.Treeview(tab_overdue, columns=cols1, show="headings")
        for c in cols1:
            tree_overdue.heading(c, text=c)
            tree_overdue.column(c, anchor="center", width=105)
        tree_overdue.column("Student Name", anchor="w", width=150)
        tree_overdue.column("Book Name", anchor="w", width=170)
        tree_overdue.pack(fill="both", expand=True)

        # TAB 2: Pending Fines Table
        cols2 = ("Issue ID", "SRNO", "Student Name", "Book Name", "Due Date", "Pending Fine (Rs.)")
        tree_fines = ttk.Treeview(tab_fines, columns=cols2, show="headings")
        for c in cols2:
            tree_fines.heading(c, text=c)
            tree_fines.column(c, anchor="center", width=120)
        tree_fines.column("Student Name", anchor="w", width=180)
        tree_fines.column("Book Name", anchor="w", width=200)
        tree_fines.pack(fill="both", expand=True)

        # TAB 3: Monthly Summary Card
        m_card = tk.Frame(tab_monthly, bg="#FFFFFF", padx=30, pady=25, highlightthickness=1, highlightbackground="#CBD5E1")
        m_card.pack(fill="x", pady=10)

        current_month = datetime.date.today().strftime("%B %Y")
        tk.Label(m_card, text=f"Monthly Activity for {current_month}", font=("Segoe UI", 14, "bold"), fg="#1E293B", bg="#FFFFFF").pack(anchor="w", pady=(0, 15))

        m_stats_frame = tk.Frame(m_card, bg="#FFFFFF")
        m_stats_frame.pack(fill="x")

        # Load Reports Data using backend module
        if lr:
            try:
                for r in lr.get_overdue_report():
                    tree_overdue.insert("", "end", values=(r[0], r[1], r[2], r[3], r[4], str(r[5]), r[6], f"Rs. {r[7]:.2f}"))

                for r in lr.get_pending_fines_report():
                    tree_fines.insert("", "end", values=(r[0], r[1], r[2], r[3], str(r[4]), f"Rs. {float(r[5]):.2f}"))

                m_data = lr.get_monthly_report()
                box1 = tk.Frame(m_stats_frame, bg="#EFF6FF", padx=20, pady=15, highlightthickness=1, highlightbackground="#BFDBFE")
                box1.pack(side="left", fill="both", expand=True, padx=(0, 10))
                tk.Label(box1, text="Books Issued This Month", font=("Segoe UI", 10, "bold"), fg="#1E40AF", bg="#EFF6FF").pack(anchor="w")
                tk.Label(box1, text=str(m_data["issued_this_month"]), font=("Segoe UI", 22, "bold"), fg="#2563EB", bg="#EFF6FF").pack(anchor="w", pady=(5, 0))

                box2 = tk.Frame(m_stats_frame, bg="#ECFDF5", padx=20, pady=15, highlightthickness=1, highlightbackground="#A7F3D0")
                box2.pack(side="left", fill="both", expand=True, padx=(10, 0))
                tk.Label(box2, text="Books Returned This Month", font=("Segoe UI", 10, "bold"), fg="#065F46", bg="#ECFDF5").pack(anchor="w")
                tk.Label(box2, text=str(m_data["returned_this_month"]), font=("Segoe UI", 22, "bold"), fg="#10B981", bg="#ECFDF5").pack(anchor="w", pady=(5, 0))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load reports: {e}")


def main():
    app = LibraryApp()
    app.mainloop()


if __name__ == "__main__":
    main()

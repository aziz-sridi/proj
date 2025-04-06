# base_panel.py
import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from styles import *

class BasePanel(ttk.Frame):
    def __init__(self, master, user_id, notebook=None):
        super().__init__(master)
        self.user_id = user_id
        self.db = Database()
        self.notebook = notebook
        configure_styles()
        self.create_messaging_tab()

    def create_messaging_tab(self):
        self.messaging_frame = ttk.Frame(self.master)
        self.messaging_frame.grid_rowconfigure(1, weight=1)
        self.messaging_frame.grid_columnconfigure(1, weight=1)

        # Left: Conversations List
        self.users_tree = ttk.Treeview(self.messaging_frame, columns=("user",), show="headings", selectmode="browse", height=15)
        self.users_tree.heading("user", text="Conversations")
        self.users_tree.column("user", width=200)
        self.users_tree.grid(row=0, column=0, rowspan=3, padx=(10, 5), pady=10, sticky="ns")

        self.users_tree.bind("<<TreeviewSelect>>", self.on_user_selected)

        # Chat Messages Tree
        self.messages_tree = ttk.Treeview(self.messaging_frame, columns=("sender", "message", "time"), show="headings", selectmode="none")
        self.messages_tree.heading("sender", text="From")
        self.messages_tree.heading("message", text="Message")
        self.messages_tree.heading("time", text="Time")
        self.messages_tree.column("sender", width=100, anchor="w")
        self.messages_tree.column("message", width=300, anchor="w")
        self.messages_tree.column("time", width=150, anchor="center")
        self.messages_tree.grid(row=0, column=1, padx=(5,10), pady=10, sticky="nsew")

        # Scrollbar for messages
        scrollbar = ttk.Scrollbar(self.messaging_frame, orient="vertical", command=self.messages_tree.yview)
        scrollbar.grid(row=0, column=2, sticky="ns", pady=10)
        self.messages_tree.configure(yscrollcommand=scrollbar.set)

        # Message entry
        self.message_entry = ttk.Entry(self.messaging_frame)
        self.message_entry.grid(row=1, column=1, columnspan=2, padx=10, pady=5, sticky="ew")

        # Send button
        self.send_btn = ttk.Button(self.messaging_frame, text="Send", command=self.send_message)
        self.send_btn.grid(row=2, column=1, columnspan=2, padx=10, pady=(0,10), sticky="ew")

        self.selected_user_id = None

        self.load_users()

    def load_users(self):
        try:
            self.db.cursor.execute("""
                SELECT DISTINCT u.id, u.name, u.role
                FROM users u
                WHERE u.id != %s
            """, (self.user_id,))
            self.users = self.db.cursor.fetchall()

            for item in self.users_tree.get_children():
                self.users_tree.delete(item)

            for user in self.users:
                display_name = f"{user['name']} ({user['role']})"
                self.users_tree.insert('', 'end', iid=str(user['id']), values=(display_name,))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load users: {str(e)}")

    def on_user_selected(self, event):
        selected = self.users_tree.selection()
        if selected:
            self.selected_user_id = int(selected[0])
            self.load_messages_with_user(self.selected_user_id)

    def load_messages_with_user(self, other_user_id):
        try:
            self.db.cursor.execute("""
                SELECT 
                    u.name AS sender_name, m.message, m.timestamp 
                FROM messages m
                JOIN users u ON m.sender_id = u.id
                WHERE (m.receiver_id = %s AND m.sender_id = %s) 
                OR (m.receiver_id = %s AND m.sender_id = %s)
                ORDER BY m.timestamp ASC
            """, (self.user_id, other_user_id, other_user_id, self.user_id))

            for item in self.messages_tree.get_children():
                self.messages_tree.delete(item)

            for msg in self.db.cursor.fetchall():
                self.messages_tree.insert('', 'end', values=(
                    msg['sender_name'],
                    msg['message'],
                    msg['timestamp'].strftime("%Y-%m-%d %H:%M")
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load messages: {str(e)}")

    def send_message(self):
        message = self.message_entry.get()
        if not self.selected_user_id or not message:
            messagebox.showwarning("Warning", "Please select a user and enter a message")
            return

        try:
            self.db.cursor.execute(
                "INSERT INTO messages (sender_id, receiver_id, message) VALUES (%s, %s, %s)",
                (self.user_id, self.selected_user_id, message)
            )
            self.db.connection.commit()
            self.message_entry.delete(0, 'end')
            self.load_messages_with_user(self.selected_user_id)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send message: {str(e)}")

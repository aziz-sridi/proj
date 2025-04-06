import tkinter as tk
from tkinter import messagebox
from database import Database
from admin_panel import AdminPanel
from doctor_panel import DoctorPanel

class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.db = Database()
        self.setup_ui()
    
    def setup_ui(self):
        self.root.title("Clinic Login")
        self.root.geometry("300x200")
        
        tk.Label(self.root, text="Username:").pack(pady=5)
        self.entry_user = tk.Entry(self.root)
        self.entry_user.pack(pady=5)
        
        tk.Label(self.root, text="Password:").pack(pady=5)
        self.entry_pass = tk.Entry(self.root, show="*")
        self.entry_pass.pack(pady=5)
        
        tk.Button(self.root, text="Login", command=self.login).pack(pady=10)
    
    def login(self):
        username = self.entry_user.get()
        password = self.entry_pass.get()
        
        user_data = self.db.authenticate(username, password)
        
        if user_data:
            user_id, role = user_data['id'], user_data['role']
            self.root.withdraw()
            
            if role == "PDG":
                admin_window = tk.Toplevel()
                AdminPanel(admin_window, user_id)
            elif role == "Médecin":
                doctor_window = tk.Toplevel()
                DoctorPanel(doctor_window, user_id)
        else:
            messagebox.showerror("Error", "Invalid credentials")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = LoginWindow()
    app.run()
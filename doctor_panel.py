import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import shutil
import os
import platform
import subprocess
from datetime import datetime
from dateutil import parser
from database import Database
from styles import configure_styles
from base_panel import BasePanel

class DoctorPanel(BasePanel):
    def __init__(self, master, doctor_id):
        super().__init__(master, doctor_id)
        self.doctor_id = doctor_id
        self.db = Database()
        configure_styles()
        self.create_widgets()
        

    def create_widgets(self):
        self.notebook = ttk.Notebook(self.master)
        
        # Create tabs
        self.appointments_frame = ttk.Frame(self.notebook)
        self.acts_frame = ttk.Frame(self.notebook)
        self.files_frame = ttk.Frame(self.notebook)
        self.messaging_frame = BasePanel(self.notebook, self.doctor_id, self.notebook)

        self.create_appointments_tab()
        self.create_acts_tab()
        self.create_files_tab()
        self.create_messaging_tab()

        self.notebook.add(self.appointments_frame, text="🗓️ Appointments")
        self.notebook.add(self.acts_frame, text="💼 Medical Acts")
        self.notebook.add(self.files_frame, text="📁 Files")
        self.notebook.add(self.messaging_frame, text="💬 Messages")

        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

    # ------------------- Appointments Tab -------------------
    def create_appointments_tab(self):
        frame = self.appointments_frame
        frame.grid_columnconfigure(1, weight=1)

        # Entry Form
        ttk.Label(frame, text="Patient Name:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.patient_name = ttk.Entry(frame)
        self.patient_name.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ttk.Label(frame, text="Date:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.appointment_date = DateEntry(frame, date_pattern="yyyy-mm-dd")
        self.appointment_date.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        ttk.Label(frame, text="Time (HH:MM):").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.appointment_time = ttk.Entry(frame)
        self.appointment_time.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=15)
        ttk.Button(btn_frame, text="Add Appointment", command=self.add_appointment).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Update Selected", command=self.update_appointment).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Delete Selected", command=self.delete_appointment).pack(side="left", padx=5)

        # Treeview with Scrollbar
        self.appointments_tree = ttk.Treeview(frame, columns=('ID', 'Patient', 'Date', 'Time'), show='headings', height=15)
        for col, width in [('ID', 50), ('Patient', 150), ('Date', 100), ('Time', 80)]:
            self.appointments_tree.heading(col, text=col)
            self.appointments_tree.column(col, width=width, anchor='center')
        self.appointments_tree.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.appointments_tree.yview)
        scrollbar.grid(row=4, column=2, sticky="ns")
        self.appointments_tree.configure(yscrollcommand=scrollbar.set)
        
        self.appointments_tree.bind('<<TreeviewSelect>>', self.on_appointment_select)
        self.load_appointments()

    def on_appointment_select(self, event):
        selected = self.appointments_tree.selection()
        if selected:
            values = self.appointments_tree.item(selected[0])['values']
            self.patient_name.delete(0, 'end')
            self.patient_name.insert(0, values[1])
            self.appointment_date.set_date(values[2])
            self.appointment_time.delete(0, 'end')
            self.appointment_time.insert(0, values[3])

    def validate_datetime(self, date_str, time_str):
        try:
            datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            return True
        except ValueError:
            return False

    def add_appointment(self):
        patient = self.patient_name.get()
        date = self.appointment_date.get()
        time = self.appointment_time.get()

        if not all([patient, date, time]):
            messagebox.showwarning("Warning", "All fields are required")
            return

        if not self.validate_datetime(date, time):
            messagebox.showwarning("Warning", "Invalid date/time format. Use YYYY-MM-DD and HH:MM")
            return

        try:
            datetime_str = f"{date} {time}:00"
            self.db.cursor.execute("""
                INSERT INTO appointments (doctor_id, patient_name, appointment_time)
                VALUES (%s, %s, %s)
            """, (self.doctor_id, patient, datetime_str))
            self.db.connection.commit()
            self.patient_name.delete(0, 'end')
            self.appointment_time.delete(0, 'end')
            self.load_appointments()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add appointment: {str(e)}")

    def load_appointments(self):
        try:
            self.appointments_tree.delete(*self.appointments_tree.get_children())
            appointments = self.db.get_appointments(self.doctor_id)
            for appt in appointments:
                appointment_id = appt['id']
                patient_name = appt['patient_name']
                appointment_time = appt['appointment_time']
                date_str = appointment_time.strftime("%Y-%m-%d")
                time_str = appointment_time.strftime("%H:%M")
                self.appointments_tree.insert('', 'end', 
                    values=(appointment_id, patient_name, date_str, time_str))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load appointments: {str(e)}")
    def update_appointment(self):
        selected = self.appointments_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an appointment to update")
            return

        values = self.appointments_tree.item(selected[0])['values']
        if not values:
            return
        appointment_id = values[0]
        patient = self.patient_name.get()
        date = self.appointment_date.get()
        time = self.appointment_time.get()

        if not all([patient, date, time]):
            messagebox.showwarning("Warning", "All fields are required")
            return

        if not self.validate_datetime(date, time):
            messagebox.showwarning("Warning", "Invalid date/time format. Use YYYY-MM-DD and HH:MM")
            return

        try:
            datetime_str = f"{date} {time}:00"
            self.db.cursor.execute("""
                UPDATE appointments 
                SET patient_name=%s, appointment_time=%s 
                WHERE id=%s
            """, (patient, datetime_str, appointment_id))
            self.db.connection.commit()
            self.load_appointments()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update appointment: {str(e)}")

    def delete_appointment(self):
        selected = self.appointments_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an appointment to delete")
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this appointment?"):
            try:
                appointment_id = self.appointments_tree.item(selected[0])['values'][0]
                self.db.cursor.execute("DELETE FROM appointments WHERE id=%s", (appointment_id,))
                self.db.connection.commit()
                self.load_appointments()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete appointment: {str(e)}")

    # ------------------- Medical Acts Tab -------------------
    def create_acts_tab(self):
        frame = self.acts_frame
        frame.grid_columnconfigure(1, weight=1)

        # Entry Form
        fields = ["Act Name:", "Description:", "Required Tools:"]
        self.act_entries = []
        for i, text in enumerate(fields):
            ttk.Label(frame, text=text).grid(row=i, column=0, padx=10, pady=10, sticky="e")
            entry = ttk.Entry(frame)
            entry.grid(row=i, column=1, padx=10, pady=10, sticky="ew")
            self.act_entries.append(entry)

        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=15)
        ttk.Button(btn_frame, text="Add Medical Act", command=self.add_medical_act).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Update Selected", command=self.update_medical_act).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Delete Selected", command=self.delete_medical_act).pack(side="left", padx=5)

        # Treeview with Scrollbar
        self.acts_tree = ttk.Treeview(frame, columns=('ID', 'Name', 'Description', 'Tools'), show='headings', height=15)
        for col, width in [('ID', 50), ('Name', 150), ('Description', 200), ('Tools', 150)]:
            self.acts_tree.heading(col, text=col)
            self.acts_tree.column(col, width=width, anchor='w')
        self.acts_tree.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.acts_tree.yview)
        scrollbar.grid(row=4, column=2, sticky="ns")
        self.acts_tree.configure(yscrollcommand=scrollbar.set)
        
        self.acts_tree.bind('<<TreeviewSelect>>', self.on_act_select)
        self.load_acts()

    def on_act_select(self, event):
        selected = self.acts_tree.selection()
        if selected:
            values = self.acts_tree.item(selected[0])['values']
            for entry, value in zip(self.act_entries, values[1:]):
                entry.delete(0, 'end')
                entry.insert(0, value)

    def load_acts(self):
        try:
            self.acts_tree.delete(*self.acts_tree.get_children())
            acts = self.db.get_acts(self.doctor_id)
            for act in acts:
                act_id = act['id']
                name = act['name']
                description = act['description']
                tools = act['tools']
                self.acts_tree.insert('', 'end', 
                    values=(act_id, name, description, tools))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load medical acts: {str(e)}")

    def add_medical_act(self):
        name, description, tools = [entry.get() for entry in self.act_entries]
        if not all([name, description, tools]):
            messagebox.showwarning("Warning", "All fields are required")
            return

        try:
            self.db.add_act(self.doctor_id, name, description, tools)
            self.load_acts()
            for entry in self.act_entries:
                entry.delete(0, 'end')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add medical act: {str(e)}")

    def update_medical_act(self):
        selected = self.acts_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a medical act to update")
            return

        act_id = self.acts_tree.item(selected[0])['values'][0]
        name, description, tools = [entry.get() for entry in self.act_entries]

        if not all([name, description, tools]):
            messagebox.showwarning("Warning", "All fields are required")
            return

        try:
            self.db.cursor.execute("""
                UPDATE acts 
                SET name=%s, description=%s, tools=%s 
                WHERE id=%s
            """, (name, description, tools, act_id))
            self.db.connection.commit()
            self.load_acts()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update medical act: {str(e)}")

    def delete_medical_act(self):
        selected = self.acts_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a medical act to delete")
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this medical act?"):
            try:
                act_id = self.acts_tree.item(selected[0])['values'][0]
                self.db.cursor.execute("DELETE FROM acts WHERE id=%s", (act_id,))
                self.db.connection.commit()
                self.load_acts()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete medical act: {str(e)}")

    # ------------------- Files Tab -------------------
    def create_files_tab(self):
        frame = self.files_frame
        frame.grid_columnconfigure(1, weight=1)

        ttk.Label(frame, text="Patient Name:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.file_patient_name = ttk.Entry(frame)
        self.file_patient_name.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ttk.Button(frame, text="Upload File", command=self.upload_file).grid(row=1, column=0, columnspan=2, pady=10)

        # Treeview with Scrollbar
        self.files_tree = ttk.Treeview(frame, columns=('ID', 'Patient', 'File Name', 'Uploaded'), show='headings', height=15)
        for col, width in [('ID', 50), ('Patient', 150), ('File Name', 200), ('Uploaded', 150)]:
            self.files_tree.heading(col, text=col)
            self.files_tree.column(col, width=width, anchor='w')
        self.files_tree.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.files_tree.yview)
        scrollbar.grid(row=2, column=2, sticky="ns")
        self.files_tree.configure(yscrollcommand=scrollbar.set)

        # Button Frame for Open/Delete
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")
        
        # Configure button frame columns
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        
        # Add buttons to btn_frame
        ttk.Button(btn_frame, text="Open File", command=self.open_file).grid(row=0, column=0, padx=5, sticky="ew")
        ttk.Button(btn_frame, text="Delete File", command=self.delete_file).grid(row=0, column=1, padx=5, sticky="ew")

        self.load_files()
    def upload_file(self):
        file_path = filedialog.askopenfilename()
        patient_name = self.file_patient_name.get()

        if not file_path or not patient_name:
            messagebox.showwarning("Warning", "Please select a file and enter patient name")
            return

        try:
            file_name = os.path.basename(file_path)
            dest_folder = "uploaded_files"
            os.makedirs(dest_folder, exist_ok=True)
            new_path = os.path.join(dest_folder, file_name)
            shutil.copy(file_path, new_path)
            
            self.db.cursor.execute("""
                INSERT INTO files (doctor_id, patient_name, file_name, file_path)
                VALUES (%s, %s, %s, %s)
            """, (self.doctor_id, patient_name, file_name, new_path))
            self.db.connection.commit()
            self.load_files()
            self.file_patient_name.delete(0, 'end')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to upload file: {str(e)}")

    def load_files(self):
        try:
            self.files_tree.delete(*self.files_tree.get_children())
            self.db.cursor.execute("""
                SELECT id, patient_name, file_name, uploaded_at 
                FROM files 
                WHERE doctor_id=%s
            """, (self.doctor_id,))
            files = self.db.cursor.fetchall()
            for file in files:
                # Extract data from dictionary
                file_id = file['id']
                patient = file['patient_name']
                filename = file['file_name']
                uploaded = file['uploaded_at'].strftime("%Y-%m-%d %H:%M")
                self.files_tree.insert('', 'end', 
                    values=(file_id, patient, filename, uploaded))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load files: {str(e)}")

    def open_file(self):
        selected = self.files_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a file to open")
            return

        try:
            file_id = self.files_tree.item(selected[0])['values'][0]
            self.db.cursor.execute("SELECT file_path FROM files WHERE id=%s", (file_id,))
            file_record = self.db.cursor.fetchone()
            if file_record:
                file_path = file_record['file_path']
                # Open file based on OS
                if platform.system() == 'Darwin':
                    subprocess.call(('open', file_path))
                elif platform.system() == 'Windows':
                    os.startfile(file_path)
                else:
                    subprocess.call(('xdg-open', file_path))
            else:
                messagebox.showerror("Error", "File not found in database")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {str(e)}")
    
    def delete_file(self):
        selected = self.files_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a file to delete")
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to permanently delete this file?"):
            try:
                file_id = self.files_tree.item(selected[0])['values'][0]
                
                # Get file path first
                self.db.cursor.execute("SELECT file_path FROM files WHERE id=%s", (file_id,))
                file_record = self.db.cursor.fetchone()
                
                if file_record:
                    file_path = file_record['file_path']
                    
                    # Delete physical file
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    else:
                        messagebox.showwarning("Warning", "File not found on disk - database entry will still be removed")
                    
                    # Use the new database method
                    self.db.delete_file(file_id)
                    self.load_files()
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete file: {str(e)}")
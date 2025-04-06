import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from base_panel import BasePanel
from styles import configure_styles

class AdminPanel(BasePanel):
    def __init__(self, master, user_id):
        self.master = master
        self.notebook = ttk.Notebook(master)
        super().__init__(master, user_id, notebook=self.notebook) 
        self.db = Database()
        self.create_widgets()
        configure_styles()


    def create_widgets(self):
        self.notebook = ttk.Notebook(self.master)
        
        # Create tabs
        self.stock_frame = ttk.Frame(self.notebook)
        self.doctors_frame = ttk.Frame(self.notebook)
        self.appointments_frame = ttk.Frame(self.notebook)

       
        self.create_messaging_tab()
        self.notebook.add(self.stock_frame, text="📦 Stock Management")
        self.notebook.add(self.doctors_frame, text="👨⚕️ Doctors Management")
        self.notebook.add(self.appointments_frame, text="📅 All Appointments")
        self.notebook.add(self.messaging_frame, text="💬 Messages")
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)
         
        self.create_stock_tab()
        self.create_doctors_tab()
        self.create_appointments_tab()
        

        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

    # STOCK MANAGEMENT TAB
    def create_stock_tab(self):
        frame = self.stock_frame
        frame.grid_columnconfigure(1, weight=1)
        
        # Entry Form
        ttk.Label(frame, text="Material Name:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.stock_name = ttk.Entry(frame)
        self.stock_name.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        ttk.Label(frame, text="Quantity:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.stock_quantity = ttk.Entry(frame)
        self.stock_quantity.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=15)
        ttk.Button(btn_frame, text="Add", command=self.add_stock).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Update", command=self.update_stock).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Delete", command=self.delete_stock).pack(side="left", padx=5)
        
        # Treeview
        self.stock_tree = ttk.Treeview(frame, columns=('id', 'name', 'quantity'), show='headings')
        self.stock_tree.heading('id', text='ID')
        self.stock_tree.heading('name', text='Material Name')
        self.stock_tree.heading('quantity', text='Quantity')
        self.stock_tree.column('id', width=50, anchor='center')
        self.stock_tree.column('name', width=200)
        self.stock_tree.column('quantity', width=100, anchor='center')
        self.stock_tree.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.stock_tree.yview)
        scrollbar.grid(row=3, column=2, sticky="ns")
        self.stock_tree.configure(yscrollcommand=scrollbar.set)
        
        # Bind selection
        self.stock_tree.bind('<<TreeviewSelect>>', self.on_stock_select)
        self.load_stock()

    def on_stock_select(self, event):
        selected = self.stock_tree.selection()
        if selected:
            item = self.stock_tree.item(selected[0])['values']
            self.stock_name.delete(0, 'end')
            self.stock_name.insert(0, item[1])
            self.stock_quantity.delete(0, 'end')
            self.stock_quantity.insert(0, item[2])

    def load_stock(self):
        try:
            self.stock_tree.delete(*self.stock_tree.get_children())
            self.db.cursor.execute("SELECT * FROM stock")
            for item in self.db.cursor.fetchall():
                self.stock_tree.insert('', 'end', values=(
                    item['id'],
                    item['name'],
                    item['quantity']
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load stock: {str(e)}")

    def add_stock(self):
        name = self.stock_name.get()
        quantity = self.stock_quantity.get()
        
        if not name or not quantity.isdigit():
            messagebox.showwarning("Warning", "Please enter valid name and quantity")
            return
            
        try:
            self.db.cursor.execute(
                "INSERT INTO stock (name, quantity) VALUES (%s, %s)",
                (name, int(quantity)))
            self.db.connection.commit()
            self.load_stock()
            self.stock_name.delete(0, 'end')
            self.stock_quantity.delete(0, 'end')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add stock: {str(e)}")

    def update_stock(self):
        selected = self.stock_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item to update")
            return
            
        try:
            item_id = self.stock_tree.item(selected[0])['values'][0]
            self.db.cursor.execute(
                "UPDATE stock SET name=%s, quantity=%s WHERE id=%s",
                (self.stock_name.get(), int(self.stock_quantity.get()), item_id))
            self.db.connection.commit()
            self.load_stock()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update stock: {str(e)}")

    def delete_stock(self):
        selected = self.stock_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item to delete")
            return
            
        try:
            item_id = self.stock_tree.item(selected[0])['values'][0]
            self.db.cursor.execute("DELETE FROM stock WHERE id=%s", (item_id,))
            self.db.connection.commit()
            self.load_stock()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete item: {str(e)}")

    # DOCTORS MANAGEMENT TAB
    def create_doctors_tab(self):
        frame = self.doctors_frame
        frame.grid_columnconfigure(1, weight=1)
        
        # Entry Form
        ttk.Label(frame, text="Doctor Name:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.doctor_name = ttk.Entry(frame)
        self.doctor_name.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        ttk.Label(frame, text="Specialty:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.doctor_specialty = ttk.Entry(frame)
        self.doctor_specialty.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        ttk.Label(frame, text="Availability:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.doctor_availability = ttk.Entry(frame)
        self.doctor_availability.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=15)
        ttk.Button(btn_frame, text="Add", command=self.add_doctor).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Update", command=self.update_doctor).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Delete", command=self.delete_doctor).pack(side="left", padx=5)
        
        # Treeview
        self.doctors_tree = ttk.Treeview(frame, columns=('id', 'name', 'specialty', 'availability'), show='headings')
        self.doctors_tree.heading('id', text='ID')
        self.doctors_tree.heading('name', text='Name')
        self.doctors_tree.heading('specialty', text='Specialty')
        self.doctors_tree.heading('availability', text='Availability')
        self.doctors_tree.column('id', width=50, anchor='center')
        self.doctors_tree.column('name', width=150)
        self.doctors_tree.column('specialty', width=150)
        self.doctors_tree.column('availability', width=100, anchor='center')
        self.doctors_tree.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.doctors_tree.yview)
        scrollbar.grid(row=4, column=2, sticky="ns")
        self.doctors_tree.configure(yscrollcommand=scrollbar.set)
        
        # Bind selection
        self.doctors_tree.bind('<<TreeviewSelect>>', self.on_doctor_select)
        self.load_doctors()

    def on_doctor_select(self, event):
        selected = self.doctors_tree.selection()
        if selected:
            item = self.doctors_tree.item(selected[0])['values']
            self.doctor_name.delete(0, 'end')
            self.doctor_name.insert(0, item[1])
            self.doctor_specialty.delete(0, 'end')
            self.doctor_specialty.insert(0, item[2])
            self.doctor_availability.delete(0, 'end')
            self.doctor_availability.insert(0, item[3])

    def load_doctors(self):
        try:
            self.doctors_tree.delete(*self.doctors_tree.get_children())
            self.db.cursor.execute("SELECT * FROM doctors")
            for item in self.db.cursor.fetchall():
                self.doctors_tree.insert('', 'end', values=(
                    item['id'],
                    item['name'],
                    item['specialty'],
                    item['availability']
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load doctors: {str(e)}")

    def add_doctor(self):
        name = self.doctor_name.get()
        specialty = self.doctor_specialty.get()
        availability = self.doctor_availability.get()
        
        if not all([name, specialty, availability]):
            messagebox.showwarning("Warning", "All fields are required")
            return
            
        try:
            self.db.cursor.execute(
                "INSERT INTO doctors (name, specialty, availability) VALUES (%s, %s, %s)",
                (name, specialty, availability))
            self.db.connection.commit()
            self.load_doctors()
            self.doctor_name.delete(0, 'end')
            self.doctor_specialty.delete(0, 'end')
            self.doctor_availability.delete(0, 'end')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add doctor: {str(e)}")

    def update_doctor(self):
        selected = self.doctors_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a doctor to update")
            return
            
        try:
            doctor_id = self.doctors_tree.item(selected[0])['values'][0]
            self.db.cursor.execute(
                "UPDATE doctors SET name=%s, specialty=%s, availability=%s WHERE id=%s",
                (self.doctor_name.get(), self.doctor_specialty.get(), 
                 self.doctor_availability.get(), doctor_id))
            self.db.connection.commit()
            self.load_doctors()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update doctor: {str(e)}")

    def delete_doctor(self):
        selected = self.doctors_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a doctor to delete")
            return
            
        try:
            doctor_id = self.doctors_tree.item(selected[0])['values'][0]
            self.db.cursor.execute("DELETE FROM doctors WHERE id=%s", (doctor_id,))
            self.db.connection.commit()
            self.load_doctors()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete doctor: {str(e)}")

    # APPOINTMENTS TAB
    def create_appointments_tab(self):
        frame = self.appointments_frame
        frame.grid_columnconfigure(0, weight=1)
        
        # Treeview
        self.appointments_tree = ttk.Treeview(
            frame, 
            columns=('id', 'doctor', 'patient', 'time'), 
            show='headings',
            height=15
        )
        self.appointments_tree.heading('id', text='ID')
        self.appointments_tree.heading('doctor', text='Doctor')
        self.appointments_tree.heading('patient', text='Patient')
        self.appointments_tree.heading('time', text='Appointment Time')
        self.appointments_tree.column('id', width=50, anchor='center')
        self.appointments_tree.column('doctor', width=150)
        self.appointments_tree.column('patient', width=150)
        self.appointments_tree.column('time', width=150, anchor='center')
        self.appointments_tree.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.appointments_tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.appointments_tree.configure(yscrollcommand=scrollbar.set)
        
        self.load_appointments()

    def load_appointments(self):
        try:
            self.appointments_tree.delete(*self.appointments_tree.get_children())
            appointments = self.db.get_appointments()
            for appt in appointments:
                self.db.cursor.execute("SELECT name FROM doctors WHERE id=%s", (appt['doctor_id'],))
                doctor = self.db.cursor.fetchone()
                
                # Handle case where doctor might be deleted
                doctor_name = doctor['name'] if doctor else "Unknown Doctor"
                
                self.appointments_tree.insert('', 'end', values=(
                    appt['id'],
                    doctor_name,
                    appt['patient_name'],
                    appt['appointment_time'].strftime("%Y-%m-%d %H:%M")
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load appointments: {str(e)}")
import mysql.connector
from mysql.connector import Error
import configparser
from tkinter import messagebox

class Database:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.connection = self.connect()
        self.cursor = self.connection.cursor(dictionary=True)
        
    def connect(self):
        try:
            return mysql.connector.connect(
                host=self.config['database']['host'],
                user=self.config['database']['user'],
                password=self.config['database']['password'],
                database=self.config['database']['database'],
                port=self.config['database']['port']
            )
        except Error as e:
            messagebox.showerror("Database Error", str(e))
            
    def authenticate(self, username, password):
        try:
            self.cursor.execute("""
                SELECT id, role FROM users 
                WHERE username=%s AND password=%s
            """, (username, password))
            return self.cursor.fetchone()  
        except Error as e:
            messagebox.showerror("Database Error", str(e))
            return None
    
    # Stock Management
    def get_stock(self):
        self.cursor.execute("SELECT * FROM stock")
        return self.cursor.fetchall()
    
    def add_stock(self, name, quantity):
        self.cursor.execute("INSERT INTO stock (name, quantity) VALUES (%s, %s)", 
                           (name, quantity))
        self.connection.commit()
    
    # Doctor Management
    def get_doctors(self):
        self.cursor.execute("SELECT * FROM doctors")
        return self.cursor.fetchall()
    
    def add_doctor(self, name, specialty, availability):
        self.cursor.execute("""
            INSERT INTO doctors (name, specialty, availability) 
            VALUES (%s, %s, %s)
        """, (name, specialty, availability))
        self.connection.commit()
    
    # Appointments Management
    def get_appointments(self, doctor_id=None):
        if doctor_id:
            self.cursor.execute("SELECT * FROM appointments WHERE doctor_id=%s", (doctor_id,))
        else:
            self.cursor.execute("SELECT * FROM appointments")
        return self.cursor.fetchall()
    
    # Medical Acts Management
    def get_acts(self, doctor_id):
        self.cursor.execute("SELECT * FROM acts WHERE doctor_id=%s", (doctor_id,))
        return self.cursor.fetchall()

    def add_act(self, doctor_id, name, description, tools):
        self.cursor.execute("""
            INSERT INTO acts (doctor_id, name, description, tools) 
            VALUES (%s, %s, %s, %s)
        """, (doctor_id, name, description, tools))
        self.connection.commit()

    def update_act(self, act_id, name, description, tools):
        self.cursor.execute("""
            UPDATE acts 
            SET name=%s, description=%s, tools=%s 
            WHERE id=%s
        """, (name, description, tools, act_id))
        self.connection.commit()

    def delete_act(self, act_id):
        self.cursor.execute("DELETE FROM acts WHERE id=%s", (act_id,))
        self.connection.commit()

    
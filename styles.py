# styles.py
import tkinter as tk
from tkinter import ttk

COLOR_PRIMARY = "#2c3e50"
COLOR_SECONDARY = "#3498db"
COLOR_LIGHT = "#ecf0f1"
COLOR_DARK = "#34495e"

def configure_styles():
    style = ttk.Style()
    style.theme_use('clam')
    
    # Configure main styles
    style.configure('TFrame', background=COLOR_LIGHT)
    style.configure('TLabel', background=COLOR_LIGHT, foreground=COLOR_DARK, font=('Helvetica', 10))
    style.configure('TButton', background=COLOR_SECONDARY, foreground='white', 
                   font=('Helvetica', 10, 'bold'), borderwidth=1)
    style.map('TButton', background=[('active', COLOR_PRIMARY), ('disabled', '#cccccc')])
    
    # Treeview styles
    style.configure('Treeview', font=('Helvetica', 10), rowheight=25,
                   background=COLOR_LIGHT, fieldbackground=COLOR_LIGHT)
    style.configure('Treeview.Heading', font=('Helvetica', 11, 'bold'), 
                   background=COLOR_PRIMARY, foreground='white')
    style.map('Treeview', background=[('selected', COLOR_SECONDARY)])
    
    # Entry styles
    style.configure('TEntry', font=('Helvetica', 10), fieldbackground='white')
    
    # Notebook styles
    style.configure('TNotebook', background=COLOR_LIGHT)
    style.configure('TNotebook.Tab', font=('Helvetica', 10, 'bold'), 
                   padding=[15, 5], background=COLOR_PRIMARY, foreground='white')
    style.map('TNotebook.Tab', background=[('selected', COLOR_SECONDARY), ('active', COLOR_PRIMARY)])
    
    # Combobox styles
    style.configure('TCombobox', fieldbackground='white')
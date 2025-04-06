import tkinter as tk
from tkinter import ttk

# Clinic-themed colors
COLOR_PRIMARY = "#1A5276"     # A deep, calm blue
COLOR_SECONDARY = "#117A65"   # A clean, medical green
COLOR_ACCENT = "#D5F5E3"      # Very light mint green
COLOR_LIGHT = "#FBFCFC"       # Almost white
COLOR_DARK = "#154360"        # Navy/dark blue text
COLOR_DISABLED = "#BFC9CA"    # Light grey for disabled
COLOR_BORDER = "#D6DBDF"

def configure_styles():
    style = ttk.Style()
    style.theme_use('clam')

    # Global styles
    style.configure('TFrame', background=COLOR_LIGHT)
    style.configure('TLabel', background=COLOR_LIGHT, foreground=COLOR_DARK, font=('Segoe UI', 10))
    
    style.configure('TButton',
        background=COLOR_SECONDARY,
        foreground='white',
        font=('Segoe UI', 10, 'bold'),
        borderwidth=0,
        padding=6
    )
    style.map('TButton',
        background=[('active', COLOR_PRIMARY), ('disabled', COLOR_DISABLED)],
        foreground=[('disabled', 'white')]
    )

    # Treeview
    style.configure('Treeview',
        font=('Segoe UI', 10),
        rowheight=26,
        background=COLOR_ACCENT,
        fieldbackground=COLOR_ACCENT,
        foreground=COLOR_DARK,
        bordercolor=COLOR_BORDER
    )
    style.configure('Treeview.Heading',
        font=('Segoe UI', 10, 'bold'),
        background=COLOR_PRIMARY,
        foreground='white'
    )
    style.map('Treeview',
        background=[('selected', COLOR_SECONDARY)],
        foreground=[('selected', 'white')]
    )

    # Entry
    style.configure('TEntry',
        font=('Segoe UI', 10),
        fieldbackground='white',
        foreground=COLOR_DARK,
        bordercolor=COLOR_BORDER
    )

    # Combobox
    style.configure('TCombobox',
        font=('Segoe UI', 10),
        fieldbackground='white',
        background='white'
    )

    # Notebook tabs (for admin/doctor panels)
    style.configure('TNotebook', background=COLOR_LIGHT, borderwidth=0)
    style.configure('TNotebook.Tab',
        font=('Segoe UI', 10, 'bold'),
        padding=[12, 6],
        background=COLOR_PRIMARY,
        foreground='white'
    )
    style.map('TNotebook.Tab',
        background=[('selected', COLOR_SECONDARY), ('active', COLOR_PRIMARY)],
        foreground=[('selected', 'white')]
    )

import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import sys
import os
import threading
from dotenv import load_dotenv
load_dotenv()
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
from app.db.db_handler import fetch_latest_samples

# --- UI State ---
SAMPLE_LIMIT = 20
samples = []
selected_sample_idx = 0
has_data = False
error_message = None

def fetch_data():
    global samples, has_data, error_message, all_samples
    try:
        all_samples = fetch_latest_samples(limit=SAMPLE_LIMIT*5)  # fetch more for filtering
        # Populate filter dropdowns
        client_ids = sorted(set(s['client_id'] for s in all_samples if s['client_id'] != 'NO DATA'))
        channel_ids = sorted(set(s['channel_id'] for s in all_samples if s['channel_id'] != 'NO DATA'))
        client_filter_dropdown['values'] = ['All Clients'] + client_ids
        channel_filter_dropdown['values'] = ['All Channels'] + channel_ids
        # Apply filters
        filtered = all_samples
        if client_filter_var.get() and client_filter_var.get() != 'All Clients':
            filtered = [s for s in filtered if s['client_id'] == client_filter_var.get()]
        if channel_filter_var.get() and channel_filter_var.get() != 'All Channels':
            filtered = [s for s in filtered if s['channel_id'] == channel_filter_var.get()]
        samples = filtered[:SAMPLE_LIMIT]
        has_data = bool(samples)
        error_message = None
    except Exception as e:
        samples = []
        has_data = False
        error_message = str(e)

def update_ui():
    # Clear and update plots and fields
    for widget in raw_frame.winfo_children():
        widget.destroy()
    for widget in filtered_frame.winfo_children():
        widget.destroy()
    for widget in class_frame.winfo_children():
        widget.destroy()
    for widget in client_frame.winfo_children():
        widget.destroy()
    # Dropdown label
    ttk.Label(client_frame, text="Client:").pack(anchor='w', padx=5, pady=5)
    # Sample selection
    if has_data:
        sample_list = [f"{s['timestamp']} | {s['client_id']}" for s in samples]
        sample_dropdown['values'] = sample_list
        sample_dropdown.current(selected_sample_idx)
        sample = samples[selected_sample_idx]
        raw_signal = sample.get('raw_signal', [])
        filtered_signal = sample.get('filtered_signal', [])
        client_id = sample['client_id']
        class_label = sample['klasse']
    else:
        sample_dropdown['values'] = ['NO DATA']
        sample_dropdown.current(0)
        raw_signal = []
        filtered_signal = []
        client_id = 'NO DATA'
        class_label = 'NO DATA'
    # Plot raw
    fig1, ax1 = plt.subplots(figsize=(4, 2))
    if has_data and raw_signal:
        ax1.plot(raw_signal)
        ax1.set_title("Raw Signal")
    else:
        ax1.text(0.5, 0.5, 'NO DATA', fontsize=16, ha='center', va='center', color='red')
        ax1.set_title("Raw Signal")
    canvas1 = FigureCanvasTkAgg(fig1, master=raw_frame)
    canvas1.get_tk_widget().pack(fill='both', expand=True)
    canvas1.draw()
    # Plot filtered
    fig2, ax2 = plt.subplots(figsize=(4, 2))
    if has_data and filtered_signal:
        ax2.plot(filtered_signal)
        ax2.set_title("Filtered Signal")
    else:
        ax2.text(0.5, 0.5, 'NO DATA', fontsize=16, ha='center', va='center', color='red')
        ax2.set_title("Filtered Signal")
    canvas2 = FigureCanvasTkAgg(fig2, master=filtered_frame)
    canvas2.get_tk_widget().pack(fill='both', expand=True)
    canvas2.draw()
    # Dropdown
    client_dropdown = ttk.Combobox(client_frame, values=[client_id])
    client_dropdown.pack(fill='x', padx=5, pady=5)
    client_dropdown.set(client_id)
    # Class display
    ttk.Label(class_frame, text=f"Class: {class_label}", font=("Arial", 24)).pack(expand=True)
    # Error message
    if error_message:
        if not hasattr(update_ui, 'error_label'):
            update_ui.error_label = ttk.Label(main_frame, text=f"Database Error: {error_message}", foreground='red', font=("Arial", 12, "bold"))
            update_ui.error_label.pack(side='top', pady=5)
        else:
            update_ui.error_label.config(text=f"Database Error: {error_message}")
            update_ui.error_label.pack(side='top', pady=5)
        messagebox.showerror("Database Error", error_message)
    else:
        if hasattr(update_ui, 'error_label'):
            update_ui.error_label.pack_forget()
    # NO DATA label
    if not has_data:
        if not hasattr(update_ui, 'no_data_label'):
            update_ui.no_data_label = ttk.Label(main_frame, text="Waiting for data... Please check your sensor or connection.", foreground='red', font=("Arial", 14, "bold"))
            update_ui.no_data_label.pack(side='top', pady=10)
        else:
            update_ui.no_data_label.pack(side='top', pady=10)
    else:
        if hasattr(update_ui, 'no_data_label'):
            update_ui.no_data_label.pack_forget()

def on_sample_select(event):
    global selected_sample_idx
    selected_sample_idx = sample_dropdown.current()
    update_ui()

def on_refresh():
    fetch_data()
    update_ui()

def auto_refresh_loop():
    if auto_refresh_var.get():
        on_refresh()
        root.after(5000, auto_refresh_loop)

def on_auto_refresh_toggle():
    if auto_refresh_var.get():
        auto_refresh_loop()

def on_client_filter_select(event):
    fetch_data()
    update_ui()

def on_channel_filter_select(event):
    fetch_data()
    update_ui()

def show_help():
    help_text = (
        "Sensor Dashboard Help\n\n"
        "- The dashboard displays raw and filtered sensor signals for each sample.\n"
        "- Use the dropdowns to filter by client or channel.\n"
        "- Select a sample from the list to view its details.\n"
        "- Use the Refresh button or enable Auto-Refresh for live updates.\n"
        "- If no data is available, check your sensor or connection.\n"
        "- Errors will be shown at the top of the window.\n"
    )
    messagebox.showinfo("Help / About", help_text)

# --- Create root window ---
root = tk.Tk()
root.title("Sensor Dashboard")
root.geometry("1000x600")

main_frame = ttk.Frame(root, padding=10)
main_frame.pack(fill='both', expand=True)

top_frame = ttk.Frame(main_frame)
top_frame.pack(side='top', fill='both', expand=True)

bottom_frame = ttk.Frame(main_frame)
bottom_frame.pack(side='bottom', fill='both', expand=True)

raw_frame = ttk.LabelFrame(top_frame, text="Rohdaten")
raw_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)

filtered_frame = ttk.LabelFrame(top_frame, text="Gefilterten Daten")
filtered_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)

client_frame = ttk.LabelFrame(bottom_frame, text="Wählen Sie ein Client")
client_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)

class_frame = ttk.LabelFrame(bottom_frame, text="Klasse")
class_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)

# Add filter dropdowns above the sample list
filter_frame = ttk.Frame(main_frame)
filter_frame.pack(side='top', fill='x', pady=5)
client_filter_var = tk.StringVar()
channel_filter_var = tk.StringVar()
client_filter_dropdown = ttk.Combobox(filter_frame, textvariable=client_filter_var, state='readonly')
client_filter_dropdown.pack(side='left', padx=5)
channel_filter_dropdown = ttk.Combobox(filter_frame, textvariable=channel_filter_var, state='readonly')
channel_filter_dropdown.pack(side='left', padx=5)
client_filter_dropdown.set('All Clients')
channel_filter_dropdown.set('All Channels')

# Add menu bar
menu_bar = tk.Menu(root)
help_menu = tk.Menu(menu_bar, tearoff=0)
help_menu.add_command(label="Help / About", command=show_help)
menu_bar.add_cascade(label="Help", menu=help_menu)
root.config(menu=menu_bar)

# --- Controls ---
controls_frame = ttk.Frame(main_frame)
controls_frame.pack(side='top', fill='x', pady=5)
refresh_button = ttk.Button(controls_frame, text="Refresh", command=on_refresh)
refresh_button.pack(side='left', padx=5)
auto_refresh_var = tk.BooleanVar()
auto_refresh_check = ttk.Checkbutton(controls_frame, text="Auto-Refresh", variable=auto_refresh_var, command=on_auto_refresh_toggle)
auto_refresh_check.pack(side='left', padx=5)

sample_dropdown = ttk.Combobox(controls_frame, state='readonly')
sample_dropdown.pack(side='left', padx=5)
sample_dropdown.bind('<<ComboboxSelected>>', on_sample_select)

client_filter_dropdown.bind('<<ComboboxSelected>>', on_client_filter_select)
channel_filter_dropdown.bind('<<ComboboxSelected>>', on_channel_filter_select)

def start_tkinter_ui():
    global root
    # --- Initial load ---
    fetch_data()
    update_ui()
    # --- Start UI ---
    root.mainloop()
import threading
import sys
import os
from dotenv import load_dotenv
load_dotenv()

# Import the backend and UI starters
from main import start_backend
from tkinter_ui import start_tkinter_ui
# ⬇️ NEW: Import the schema initializer
from app.db.db_handler import initialize_schema

def run_backend():
     # NEW: Initialize schema from schema.sql
    initialize_schema()
    start_backend()

if __name__ == "__main__":
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()
    # Start Tkinter UI in main thread
    start_tkinter_ui() 
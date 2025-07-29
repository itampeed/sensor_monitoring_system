# backend/main.py

import asyncio
import sys
import os

# For Windows compatibility with asyncio
if sys.platform.startswith('win') and sys.version_info >= (3, 8):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from dotenv import load_dotenv
load_dotenv()

from app.ml.trainer import train_from_csv
from app.ws.websocket_server import start_server
from app.utils.logger import log



def start_backend():
    try:
        log("🚀 Starting sensor monitoring system backend...")

        # Train the ML model
        train_from_csv("Trainingsdaten_Timmi.csv")
        log("✅ Model trained successfully.")

        # Start WebSocket server
        asyncio.run(start_server())

    except KeyboardInterrupt:
        log("🛑 Server shut down by user.")
    except Exception as e:
        log(f"❌ Unexpected error: {e}", level="ERROR")

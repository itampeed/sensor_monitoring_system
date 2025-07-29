# Sensor Monitoring System

This is a real-time sensor data monitoring and visualization system built with Python. It uses TimescaleDB (PostgreSQL) to store time-series data, a machine learning model to classify sensor signals, and a Tkinter-based GUI for live visualization.

---

## 🚀 Features

- 📡 Real-time WebSocket-based sensor data ingestion
- 📊 Visualization of raw and filtered signals via Tkinter
- 🧠 ML-based classification of incoming samples
- 🗂️ TimescaleDB for efficient time-series storage
- 🔒 User authentication and password reset functionality

---

## 🏗️ Project Structure

sensor_monitoring_system/
├── app/ # Core backend logic (DB, ML, processing)
├── .env # Environment config (DB credentials, etc.)
├── run_all.py # Starts backend and UI
├── tkinter_ui.py # Live dashboard GUI
├── requirements.txt # Python dependencies
├── README.md # Project documentation


---

## 🛠️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/your-username/sensor-monitoring-system.git
cd sensor-monitoring-system
```

### 2. Create a virtual environment
```bash 
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
### 4. Configure Environment Variables
Create an .env file and configure the below varialbes
```bash
DB_HOST=localhost
DB_NAME=sensor_data
DB_USER=postgres
DB_PASS=your_password
DB_PORT=5432
JWT_SECRET='Your_Secret'
```

### 5. Run the Application
```bash
python run_all.py
```

## And all good to go then
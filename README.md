# 🛫 AA Miles Price Tracker

A Python-based tool to **monitor American Airlines award (miles) flights**, log price changes, and send alerts via [Pushover](https://pushover.net/).

## ✨ Features

- Monitors multiple **departure dates**, **origins**, and **destinations**
- Filters only **non-stop flights**
- Tracks and logs:
  - Flight number
  - Departure time
  - Price in miles
- Notifies when price drops, increases, or stays the same
- Stores logs in CSV files (`flight_price_log_v2.csv`, `execution_log_v2.csv`)

## 🔧 Setup

1. **Clone the repo**
   ```
   git clone https://github.com/yourusername/aa-miles-tracker.git
   cd aa-miles-tracker
   ```

2. **Create a virtual environment**
   ```
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```

3. **Install requirements**
   ```
   pip install -r requirements.txt
   ```

4. **Create a `.env` file**
   ```
   PUSHOVER_USER_KEY=your_pushover_user_key
   PUSHOVER_API_TOKEN=your_pushover_app_token
   ```

## 🚀 Running the script

```
python aa_miles_tracker.py
```

You’ll receive notifications on your Pushover app when the price for any monitored route changes.

## 📁 Files

- `flight_price_log_v2.csv`: Tracks historical flight prices
- `execution_log_v2.csv`: Logs execution status and messages
- `aa_miles_tracker.py`: Main script

## 🔄 Configuration

In `aa_miles_tracker.py`:

```
DATES_TO_MONITOR = ["2025-05-23", "2025-05-24"]
ORIGINS = ["MIA"]
DESTINATIONS = ["SFO"]
```

You can easily add multiple origins or destinations like:

```
ORIGINS = ["MIA", "FLL"]
DESTINATIONS = ["SFO", "LAX"]
```

## 📲 Example Notification

> 📉 2025-05-23 MIA→SFO Flight 2035 at 07:33 dropped to 14000 miles (-500).

## 📌 Disclaimer

This script is for **personal use only** and not affiliated with American Airlines. Please monitor usage to avoid violating their terms of service. Polling once every few hours is recommended.

## 🧠 Future Ideas

- SQLite or PostgreSQL integration
- Daily summary email or digest
- Web dashboard with historical charts

## 📜 License

MIT — Feel free to use and modify.

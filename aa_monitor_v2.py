import requests
import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()
PUSHOVER_USER_KEY = os.getenv("PUSHOVER_USER_KEY")
PUSHOVER_API_TOKEN = os.getenv("PUSHOVER_API_TOKEN")

# Config
DATES_TO_MONITOR = ["2025-05-23", "2025-05-24"]
ORIGINS = ["LAX"]
DESTINATIONS = ["SFO"]
LOG_FILE = "flight_price_log_v2.csv"
EXECUTION_LOG_FILE = "execution_log_v2.csv"

API_URL = "https://www.aa.com/booking/api/search/itinerary"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Origin": "https://www.aa.com",
    "Referer": "https://www.aa.com/booking/choose-flights/1",
}

def get_payload(departure_date, origin, destination):
    return {
        "metadata": {"selectedProducts": [], "tripType": "OneWay", "udo": {}},
        "passengers": [{"type": "adult", "count": 3}], # Adjust passenger count as needed
        "requestHeader": {"clientId": "AAcom"},
        "slices": [{
            "allCarriers": True,
            "cabin": "",
            "departureDate": departure_date,
            "destination": destination,
            "destinationNearbyAirports": False,
            "maxStops": None,
            "origin": origin,
            "originNearbyAirports": False,
        }
        ],
        "tripOptions": {
            "corporateBooking": False,
            "fareType": "Lowest",
            "locale": "en_US",
            "searchType": "Award"
        },
        "loyaltyInfo": None,
        "version": "",
        "queryParams": {
            "sliceIndex": 0,
            "sessionId": "",
            "solutionSet": "",
            "solutionId": "",
            "sort": "CARRIER"
        }
    }

def fetch_flight_data(payload):
    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        date = payload["slices"][0]["departureDate"]
        origin = payload["slices"][0]["origin"]
        destination = payload["slices"][0]["destination"]
        log_execution("ERROR", f"{date} {origin}→{destination}: {e}")
        return None

def process_flights(data, date, origin, destination):
    log_entries = []
    notifications = []
    execution_logs = []

    if os.path.exists(LOG_FILE):
        previous_log = pd.read_csv(LOG_FILE)
    else:
        previous_log = pd.DataFrame(columns=[
            "Timestamp", "Date", "Origin", "Destination", 
            "Flight Number", "Departure Time", "Award Points"
        ])

    for flight in data.get("slices", []):
        if len(flight.get("segments", [])) > 1:
            continue  # Filter only non-stop flights

        segment = flight["segments"][0]
        flight_number = segment["flight"]["flightNumber"]
        raw_time = segment["departureDateTime"]
        departure_time = raw_time.split("T")[1].split("-")[0][:5]
        award_points = flight["pricingDetail"][0]["perPassengerAwardPoints"]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        log_entries.append([
            timestamp, date, origin, destination, 
            flight_number, departure_time, award_points
        ])

        prev = previous_log[
            (previous_log["Flight Number"] == int(flight_number)) &
            (previous_log["Date"] == date) &
            (previous_log["Origin"] == origin) &
            (previous_log["Destination"] == destination)
        ]

        if not prev.empty:
            prev_points = prev["Award Points"].iloc[-1]
            diff = award_points - prev_points

            if diff < 0:
                msg = f"📉 {date} {origin}→{destination} Flight {flight_number} at {departure_time[:16]} dropped to {award_points} miles (-{abs(diff)})."
                notifications.append(msg)
                execution_logs.append([timestamp, "Price Dropped", msg])
            elif diff > 0:
                msg = f"📈 {date} {origin}→{destination} Flight {flight_number} at {departure_time[:16]} increased to {award_points} miles (+{diff})."
                notifications.append(msg)
                execution_logs.append([timestamp, "Price Increased", msg])
            else:
                execution_logs.append([timestamp, "Price Unchanged", f"{date} Flight {flight_number} at {departure_time[:16]} unchanged."])
        else:
            execution_logs.append([timestamp, "First Run", f"{date} {origin}→{destination} Flight {flight_number} at {departure_time[:16]} - {award_points} miles."])

    return log_entries, notifications, execution_logs

def log_flight_data(entries):
    df = pd.DataFrame(entries, columns=[
        "Timestamp", "Date", "Origin", "Destination", 
        "Flight Number", "Departure Time", "Award Points"
    ])
    df.to_csv(LOG_FILE, mode="a", header=not os.path.exists(LOG_FILE), index=False)

def log_execution(status, detail):
    df = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d %H:%M:%S"), status, detail]],
                      columns=["Timestamp", "Status", "Details"])
    df.to_csv(EXECUTION_LOG_FILE, mode="a", header=not os.path.exists(EXECUTION_LOG_FILE), index=False)

def send_notifications(messages):
    if not PUSHOVER_USER_KEY or not PUSHOVER_API_TOKEN:
        log_execution("ERROR", "Missing Pushover credentials.")
        return
    for msg in messages:
        payload = {
            "token": PUSHOVER_API_TOKEN,
            "user": PUSHOVER_USER_KEY,
            "message": msg,
            "title": "Award Flight Alert"
        }
        requests.post("https://api.pushover.net/1/messages.json", data=payload)

def main():
    for date in DATES_TO_MONITOR:
        for origin in ORIGINS:
            for destination in DESTINATIONS:
                payload = get_payload(date, origin, destination)
                data = fetch_flight_data(payload)
                if not data:
                    continue
                logs, notifications, execs = process_flights(data, date, origin, destination)
                log_flight_data(logs)
                for e in execs:
                    log_execution(e[1], e[2])
                if notifications:
                    send_notifications(notifications)

if __name__ == "__main__":
    main()

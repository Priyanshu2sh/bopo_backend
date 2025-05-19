import schedule
import time
import requests

def run_global_point_deduction():
    url = "http://192.168.110.38:8000/api/bopo_award/cron-deduct-global/"
    try:
        response = requests.get(url)
        print(f"[SCHEDULED] Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"[ERROR] Failed to call URL: {e}")

# Schedule at midnight
# schedule.every(1).day.at("00:00").do(run_global_point_deduction)
schedule.every(1).days.do(run_global_point_deduction)

print("Scheduler started. Waiting for midnight task...")

while True:
    schedule.run_pending()
    time.sleep(60)

# monitoring.py
import psutil
import pandas as pd
from datetime import datetime
import time
import os
import logging

DATA_FILE = "metrics_log.csv"
LOG_FILE = "monitoring.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

def get_metrics():
    load1, load5, load15 = psutil.getloadavg() if hasattr(psutil, "getloadavg") else (0, 0, 0)
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent,
        "net_sent": psutil.net_io_counters().bytes_sent,
        "net_recv": psutil.net_io_counters().bytes_recv,
        "load_avg_1min": load1,
        "load_avg_5min": load5,
        "load_avg_15min": load15
    }

def save_metrics(metrics):
    df = pd.DataFrame([metrics])
    try:
        if not os.path.exists(DATA_FILE):
            df.to_csv(DATA_FILE, index=False)
        else:
            df.to_csv(DATA_FILE, mode='a', index=False, header=False)
    except Exception as e:
        logging.error(f"Ошибка при сохранении: {e}")

def run_monitor(interval_seconds=10):
    print(f"Сбор метрик каждые {interval_seconds} секунд. Ctrl+C для остановки.")
    try:
        while True:
            metrics = get_metrics()
            save_metrics(metrics)
            logging.info(f"Метрики: {metrics}")
            print(f"[{metrics['timestamp']}] CPU: {metrics['cpu_percent']}% | RAM: {metrics['memory_percent']}%")
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("Мониторинг остановлен.")
    except Exception as e:
        logging.exception(f"Ошибка: {e}")

if __name__ == "__main__":
    run_monitor()

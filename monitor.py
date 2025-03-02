import time
import psutil
import GPUtil

def monitor_system(interval=5):
    """
    Function to monitor system metrics such as CPU and GPU usage.

    :param interval: Time interval in seconds between updates.
    """
    print("Starting system monitoring...")
    try:
        while True:
            # Monitor CPU usage
            cpu_usage = psutil.cpu_percent(interval=1)
            print(f"CPU Usage: {cpu_usage}%")

            # Monitor GPU usage
            gpus = GPUtil.getGPUs()
            for gpu in gpus:
                print(f"GPU {gpu.id}: {gpu.load*100}% usage, Memory Used: {gpu.memoryUsed}MB / {gpu.memoryTotal}MB")

            # Monitor memory usage
            memory_info = psutil.virtual_memory()
            print(f"Memory Usage: {memory_info.percent}%")

            time.sleep(interval)
    except KeyboardInterrupt:
        print("Monitoring stopped.")

if __name__ == "__main__":
    monitor_system()

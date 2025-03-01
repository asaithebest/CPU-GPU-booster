import time
import argparse
import multiprocessing
import psutil

def stress_cpu(duration):
    print("Stressing CPU...")
    start_time = time.time()
    while (time.time() - start_time) < duration:
        [x ** 2 for x in range(10000)]

def monitor_temperatures():
    print("Monitoring temperatures...")
    while True:
        cpu_temp = psutil.sensors_temperatures()['coretemp'][0].current
        print(f"CPU Temperature: {cpu_temp}°C")
        time.sleep(5)

def main():
    parser = argparse.ArgumentParser(description="Stress test tool for CPU.")
    parser.add_argument('--cpu', action='store_true', help='Stress test the CPU')
    parser.add_argument('--duration', type=int, default=60, help='Duration of the stress test in seconds')

    args = parser.parse_args()

    if args.cpu:
        cpu_process = multiprocessing.Process(target=stress_cpu, args=(args.duration,))
        cpu_process.start()
        cpu_process.join()

    monitor_process = multiprocessing.Process(target=monitor_temperatures)
    monitor_process.start()

    time.sleep(args.duration)
    monitor_process.terminate()
    monitor_process.join()

if __name__ == "__main__":
    main()

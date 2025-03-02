import time
import argparse
import multiprocessing
import psutil
import GPUtil
import pyopencl as cl
import numpy as np

# Function to stress the CPU with load control
def stress_cpu(duration, load_percentage):
    print(f"Stressing CPU at {load_percentage}% load...")
    start_time = time.time()
    while (time.time() - start_time) < duration:
        # Calculate the time to sleep based on the desired load percentage
        work_time = load_percentage / 100.0
        sleep_time = max(0, 1 - work_time)  # Ensure sleep_time is non-negative

        # Perform computation
        [x ** 2 for x in range(10000)]  # Useless calculation to stress the CPU

        # Sleep to reduce CPU usage
        time.sleep(sleep_time)

# Function to stress the GPU
def stress_gpu(duration):
    print("Stressing GPU...")
    # Initialize OpenCL
    platforms = cl.get_platforms()
    gpu_devices = [device for platform in platforms for device in platform.get_devices() if device.type == cl.device_type.GPU]

    if not gpu_devices:
        print("No GPU device found.")
        return

    gpu = gpu_devices[0]
    ctx = cl.Context([gpu])
    queue = cl.CommandQueue(ctx)

    # Create a large array to perform calculations on
    a = np.random.rand(1000000).astype(np.float32)
    b = np.random.rand(1000000).astype(np.float32)

    a_g = cl.Buffer(ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=a)
    b_g = cl.Buffer(ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=b)
    dest_g = cl.Buffer(ctx, cl.mem_flags.WRITE_ONLY, b.nbytes)

    program = cl.Program(ctx, """
    __kernel void sum(__global const float *a, __global const float *b, __global float *c) {
        int gid = get_global_id(0);
        c[gid] = a[gid] + b[gid];
    }
    """).build()

    start_time = time.time()
    while (time.time() - start_time) < duration:
        program.sum(queue, a.shape, None, a_g, b_g, dest_g)

    # Clean up
    a_g.release()
    b_g.release()
    dest_g.release()

# Function to monitor system metrics
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

def main():
    parser = argparse.ArgumentParser(description="Stress test tool for CPU and GPU.")
    parser.add_argument('--cpu', action='store_true', help='Stress test the CPU')
    parser.add_argument('--gpu', action='store_true', help='Stress test the GPU')
    parser.add_argument('--duration', type=int, default=60, help='Duration of the stress test in seconds')
    parser.add_argument('--load', type=int, default=100, help='CPU load percentage (1-100)')

    args = parser.parse_args()

    if args.cpu:
        num_cores = multiprocessing.cpu_count()
        processes = []

        for _ in range(num_cores):
            p = multiprocessing.Process(target=stress_cpu, args=(args.duration, args.load))
            processes.append(p)
            p.start()

        for p in processes:
            p.join()

    if args.gpu:
        gpu_process = multiprocessing.Process(target=stress_gpu, args=(args.duration,))
        gpu_process.start()
        gpu_process.join()

    # Start system monitoring in a separate process
    monitor_process = multiprocessing.Process(target=monitor_system)
    monitor_process.start()

    # Wait for the stress test to finish
    time.sleep(args.duration)
    monitor_process.terminate()
    monitor_process.join()

if __name__ == "__main__":
    main()

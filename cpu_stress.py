import time
import multiprocessing

def stress_cpu(duration):
    """
    Function to stress the CPU by performing intensive calculations.

    :param duration: Duration in seconds for which the CPU will be stressed.
    """
    print("Stressing CPU...")
    start_time = time.time()
    while (time.time() - start_time) < duration:
        [x ** 2 for x in range(10000)]

def main(duration):
    num_cores = multiprocessing.cpu_count()
    processes = []

    for _ in range(num_cores):
        p = multiprocessing.Process(target=stress_cpu, args=(duration,))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

if __name__ == "__main__":
    test_duration = 60
    main(test_duration)

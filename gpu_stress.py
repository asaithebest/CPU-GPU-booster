import time
import pyopencl as cl
import numpy as np

def stress_gpu(duration):
    """
    Function to stress the GPU by performing intensive calculations.

    :param duration: Duration in seconds for which the GPU will be stressed.
    """
    print("Stressing GPU...")
    platforms = cl.get_platforms()
    gpu_devices = [device for platform in platforms for device in platform.get_devices() if device.type == cl.device_type.GPU]

    if not gpu_devices:
        print("No GPU device found.")
        return

    gpu = gpu_devices[0]
    ctx = cl.Context([gpu])
    queue = cl.CommandQueue(ctx)

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

    a_g.release()
    b_g.release()
    dest_g.release()

if __name__ == "__main__":
    test_duration = 60
    stress_gpu(test_duration)

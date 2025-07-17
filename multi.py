import multiprocessing

def heavy_computation(x):
    # CPU-heavy function here
    return x*x

with multiprocessing.Pool(processes=4) as pool:
    results = pool.map(heavy_computation, range(10))
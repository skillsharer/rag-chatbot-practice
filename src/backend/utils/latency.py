import time

TIMINGS = []

def measure(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        TIMINGS.append(
                    {
                        "module": func.__name__,
                        "latency": elapsed,
                    }
                )
        
        print(f"{func.__name__} took {elapsed:.4f} seconds")
        return result
    return wrapper

def reset_timings():
    TIMINGS.clear()

def get_timings():
    return TIMINGS.copy()
def timer(func):
    def wrapper(*args, **kwargs):
        import time
        
        start = time.time()
        val = func(*args, **kwargs)
        end = time.time()
        
        print(f"time took to run function {func.__name__} : {end-start:.4f}")
        
        return val
    
    return wrapper
        
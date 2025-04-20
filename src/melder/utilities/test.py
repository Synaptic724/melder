import time
from datetime import datetime

print(time.time())         # Wall clock (seconds)
print(time.time_ns())      # Wall clock (nanoseconds)

print(time.monotonic())    # Monotonic clock (seconds)
print(time.monotonic_ns()) # Monotonic clock (nanoseconds)

print(datetime.now())      # Full human-readable date + time
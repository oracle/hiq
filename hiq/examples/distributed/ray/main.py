import time
import ray
from timeit import default_timer as timer


def f1():
    time.sleep(1)


@ray.remote
def f2():
    time.sleep(1)


t1 = timer()
# The following takes ten seconds.
[f1() for _ in range(10)]
t2 = timer()
print(t2 - t1)

# The following takes one second (assuming the system has at least ten CPUs).
t1 = timer()
ray.get([f2.remote() for _ in range(10)])
t2 = timer()
print(t2 - t1)

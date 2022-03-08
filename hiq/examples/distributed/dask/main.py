# https://examples.dask.org/delayed.html
import dask
from dask.bag import from_sequence
import dask.config
from dask.distributed import Client


def multiply(x, y=7):
    return x * y


def add(x, y):
    return x + y


def main_computation():
    bag = from_sequence([1, 2, 3])
    bag = bag.map(multiply).fold(add)
    return dask.compute(bag)


def main():
    # Start three worker processes on the local machine:
    client = Client(n_workers=3, threads_per_worker=1)
    # Run the Dask computation in the worker processes:
    result = main_computation()
    print("Result:", result)


if __name__ == "__main__":
    main()

# https://en.wikipedia.org/wiki/Quadratic_function
import time


def add(x, y):
    time.sleep(0.05)
    return x + y


def multiply(x, y):
    time.sleep(0.1)
    return x * y


def square(x):
    return multiply(x, x)


def quadratic(a, b, c, x):
    tmp = add(multiply(a, square(x)), multiply(b, x))
    return add(tmp, c)


def main():
    for x in range(-3, 2):
        print(quadratic(1, 2, 1, x))


if __name__ == "__main__":
    main()

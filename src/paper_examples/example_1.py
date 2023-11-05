def decorator(func):
    def wrapper():
        print("Running wrapper().")

    return wrapper


@decorator
def decorated():
    print("Running decorated().")


decorated()

def hello(name):
    return f"Hello, {name}!"

def goodbye(name):
    return hello(name) + " Goodbye!"

class Greeter:
    def greet(self):
        return hello("World")

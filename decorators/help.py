# Decorator that assigns a help category to a function
def Category(category, unpack=False):
    def decorator(func):
        setattr(func, "category", category)
        setattr(func, "unpack", unpack)
        return func
    return decorator

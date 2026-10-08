import time
from prompt import string

def log_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()

        result = func(*args, **kwargs)

        end_time = time.time()
        elapsed_time = end_time - start_time

        print(
            f"Функция {func.__name__} "
            f"выполнена за {elapsed_time:.6f} секунд."
        )

        return result
    
    if hasattr(func, "clear_cache"):
        wrapper.clear_cache = func.clear_cache

    return wrapper


def confirm_action(func):
    def wrapper(*args, **kwargs):
        answer = string("Вы уверены? (y/n): ")

        if answer.lower() != "y":
            print("Операция отменена.")
            return None

        return func(*args, **kwargs)

    return wrapper


def cache(func):
    cache_data = {}

    def wrapper(*args, **kwargs):
        table_name = args[1]
        where = args[3] if len(args) > 3 else None

        key = (table_name, where)

        if key in cache_data:
            print("Результат взят из кэша.")
            return cache_data[key]

        result = func(*args, **kwargs)
        cache_data[key] = result

        return result

    wrapper.cache_data = cache_data
    wrapper.clear_cache = cache_data.clear

    return wrapper
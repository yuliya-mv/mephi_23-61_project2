
import time

from prompt import string


def handle_db_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as error:
            print(f"Ошибка базы данных: {error}")
        except ValueError as error:
            print(f"Ошибка значения: {error}")
        except FileNotFoundError as error:
            print(f"Файл не найден: {error}")

        return None

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


def confirm_action(action_name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            answer = string(
                f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            )

            if answer.lower() != "y":
                print("Операция отменена.")
                return None

            return func(*args, **kwargs)

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper

    return decorator


def log_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        elapsed_time = time.monotonic() - start_time

        print(
            f"Функция {func.__name__} выполнилась за "
            f"{elapsed_time:.3f} секунд"
        )

        return result

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__

    if hasattr(func, "clear_cache"):
        wrapper.clear_cache = func.clear_cache

    return wrapper


def create_cacher():
    cache_data = {}

    def cache_result(key, value_func):
        if key in cache_data:
            print("Результат взят из кэша.")
            return cache_data[key]

        result = value_func()
        cache_data[key] = result
        return result

    cache_result.clear = cache_data.clear
    return cache_result

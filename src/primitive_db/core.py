import os

from decorators import cache, confirm_action, log_time


def create_table(metadata, table_name, columns):
    allowed = (
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789_"
    )

    if not table_name or any(char not in allowed for char in table_name):
        print(f"Некорректное значение: {table_name}. Попробуйте снова.")
        return metadata

    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    os.makedirs("data", exist_ok=True)

    valid_types = {"int", "str", "bool"}
    parsed_columns = []

    for column in columns:
        parts = column.split(":", 1)

        if len(parts) != 2 or not parts[0] or not parts[1]:
            print(
                f"Некорректное значение: {column}. "
                "Столбец должен содержать имя и тип. Попробуйте снова."
            )
            return metadata

        column_name, column_type = parts

        if column_type not in valid_types:
            print(
                f"Некорректное значение: {column_type}. "
                "Попробуйте снова."
            )
            return metadata

        if column_name.lower() == "id":
            column_name = "ID"

        parsed_columns.append((column_name, column_type))

    id_column = None
    other_columns = []

    for column_name, column_type in parsed_columns:
        if column_name == "ID":
            id_column = ("ID", column_type)
        else:
            other_columns.append((column_name, column_type))

    if id_column is None:
        id_column = ("ID", "int")

    parsed_columns = [id_column] + other_columns

    columns = [
        f"{column_name}:{column_type}"
        for column_name, column_type in parsed_columns
    ]

    metadata[table_name] = columns

    print(
        f'Таблица "{table_name}" успешно создана '
        f'со столбцами: {", ".join(columns)}'
    )

    return metadata


def list_tables(metadata):
    if not metadata:
        print("В базе данных нет таблиц.")
        return

    for table_name in metadata:
        print(f"- {table_name}")

def info_table(metadata, table_name, table_data):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return

    columns = metadata[table_name]

    print(f"Таблица: {table_name}")
    print(f"Столбцы: {', '.join(columns)}")
    print(f"Количество записей: {len(table_data)}")


def drop_table(metadata, table_name):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]

    filepath = f"data/{table_name}.json"

    if os.path.exists(filepath):
        os.remove(filepath)

    print(f'Таблица "{table_name}" успешно удалена.')

    select.clear_cache()

    return metadata

@log_time
def insert(metadata, table_name, table_data, values):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return table_data

    columns = metadata[table_name]

    if len(values) != len(columns) - 1:
        print(
            f"Некорректное количество значений. "
            f"Ожидается: {len(columns) - 1}. Попробуйте снова."
        )
        return table_data

    new_id = 1

    if table_data:
        new_id = max(record["ID"] for record in table_data) + 1

    record = {"ID": new_id}

    for column, value in zip(columns[1:], values):
        column_name, column_type = column.split(":")

        if column_type == "int" and not isinstance(value, int):
            print(f"Некорректное значение: {value}. Попробуйте снова.")
            return table_data

        if column_type == "str" and not isinstance(value, str):
            print(f"Некорректное значение: {value}. Попробуйте снова.")
            return table_data

        if column_type == "bool" and not isinstance(value, bool):
            print(f"Некорректное значение: {value}. Попробуйте снова.")
            return table_data

        record[column_name] = value

    new_table_data = table_data + [record]

    select.clear_cache()

    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')

    return new_table_data

@log_time
@cache
def select(metadata, table_name, table_data, where=None):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return []

    if where is None:
        return table_data

    column_name, expected_value = where

    if column_name not in [column.split(":")[0] for column in metadata[table_name]]:
        print(
            f"Некорректное значение: {column_name}. "
            "Попробуйте снова."
        )
        return []

    return [
        record
        for record in table_data
        if record.get(column_name) == expected_value
    ]

@log_time
def update(metadata, table_name, table_data, column_name, new_value, where):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return table_data

    columns = metadata[table_name]
    column_names = [column.split(":")[0] for column in columns]

    if column_name not in column_names:
        print(
            f"Некорректное значение: {column_name}. "
            "Попробуйте снова."
        )
        return table_data

    if column_name == "ID":
        print("Нельзя изменять ID. Попробуйте снова.")
        return table_data

    column_type = next(
        column.split(":")[1]
        for column in columns
        if column.split(":")[0] == column_name
    )

    if column_type == "int" and not isinstance(new_value, int):
        print(f"Некорректное значение: {new_value}. Попробуйте снова.")
        return table_data

    if column_type == "str" and not isinstance(new_value, str):
        print(f"Некорректное значение: {new_value}. Попробуйте снова.")
        return table_data

    if column_type == "bool" and not isinstance(new_value, bool):
        print(f"Некорректное значение: {new_value}. Попробуйте снова.")
        return table_data

    where_column, where_value = where

    new_table_data = []
    updated_id = None

    for record in table_data:
        new_record = record.copy()

        if new_record.get(where_column) == where_value:
            new_record[column_name] = new_value
            updated_id = new_record["ID"]

        new_table_data.append(new_record)

    if updated_id is None:
        print("Запись не найдена. Попробуйте снова.")
        return table_data

    print(
    f'Запись с ID={updated_id} в таблице "{table_name}" успешно обновлена.')

    select.clear_cache()

    return new_table_data

@confirm_action
def delete(metadata, table_name, table_data, where):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return table_data

    where_column, where_value = where

    columns = metadata[table_name]
    column_names = [column.split(":")[0] for column in columns]

    if where_column not in column_names:
        print(
            f"Некорректное значение: {where_column}. Попробуйте снова."
        )
        return table_data

    deleted_id = None

    for record in table_data:
        if record.get(where_column) == where_value:
            deleted_id = record["ID"]
            break

    new_table_data = [
        record
        for record in table_data
        if record.get(where_column) != where_value
    ]

    if len(new_table_data) == len(table_data):
        print("Запись не найдена. Попробуйте снова.")
        return table_data

    print(f'Запись с ID={deleted_id} успешно удалена из таблицы "{table_name}".')

    select.clear_cache()

    return new_table_data
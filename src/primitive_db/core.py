import os

from primitive_db.constants import DATA_DIR, VALID_TYPES
from primitive_db.decorators import (
    confirm_action,
    create_cacher,
    handle_db_errors,
    log_time,
)

cache_result = create_cacher()


def get_column_info(metadata, table_name):
    columns = []

    for column in metadata[table_name]:
        column_name, column_type = column.split(":", 1)
        columns.append((column_name, column_type))

    return columns


def is_valid_type(value, column_type):
    if column_type == "int":
        return type(value) is int

    if column_type == "str":
        return type(value) is str

    if column_type == "bool":
        return type(value) is bool

    return False


def validate_condition(metadata, table_name, where):
    if where is None:
        return True

    column_name, value = where
    columns = get_column_info(metadata, table_name)

    for name, column_type in columns:
        if name == column_name:
            if not is_valid_type(value, column_type):
                print(
                    f"Некорректное значение: {value}. "
                    "Попробуйте снова."
                )
                return False

            return True

    print(
        f"Некорректное значение: {column_name}. "
        "Попробуйте снова."
    )
    return False


def filter_records(table_data, where):
    if where is None:
        return table_data.copy()

    column_name, expected_value = where

    return [
        record
        for record in table_data
        if record.get(column_name) == expected_value
    ]


@handle_db_errors
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

    parsed_columns = []
    column_names = []

    for column in columns:
        parts = column.split(":", 1)

        if len(parts) != 2 or not parts[0] or not parts[1]:
            print(
                f"Некорректное значение: {column}. "
                "Столбец должен содержать имя и тип. "
                "Попробуйте снова."
            )
            return metadata

        column_name, column_type = parts

        if not column_name.replace("_", "a").isalnum():
            print(
                f"Некорректное значение: {column_name}. "
                "Попробуйте снова."
            )
            return metadata

        if column_type not in VALID_TYPES:
            print(
                f"Некорректное значение: {column_type}. "
                "Попробуйте снова."
            )
            return metadata

        if column_name.lower() == "id":
            column_name = "ID"

            if column_type != "int":
                print(
                    "Столбец ID должен иметь тип int. "
                    "Попробуйте снова."
                )
                return metadata

        if column_name in column_names:
            print(
                f"Некорректное значение: {column_name}. "
                "Попробуйте снова."
            )
            return metadata

        column_names.append(column_name)
        parsed_columns.append((column_name, column_type))

    other_columns = [
        (name, column_type)
        for name, column_type in parsed_columns
        if name != "ID"
    ]

    parsed_columns = [("ID", "int")] + other_columns

    columns = [
        f"{column_name}:{column_type}"
        for column_name, column_type in parsed_columns
    ]

    os.makedirs(DATA_DIR, exist_ok=True)

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


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]

    filepath = os.path.join(DATA_DIR, f"{table_name}.json")

    if os.path.exists(filepath):
        os.remove(filepath)

    cache_result.clear()

    print(f'Таблица "{table_name}" успешно удалена.')

    return metadata


@handle_db_errors
@log_time
def insert(metadata, table_name, table_data, values):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return table_data

    columns = get_column_info(metadata, table_name)

    if len(values) != len(columns) - 1:
        print(
            "Некорректное количество значений. "
            f"Ожидается: {len(columns) - 1}. Попробуйте снова."
        )
        return table_data

    record = {}
    value_index = 0

    for column_name, column_type in columns:
        if column_name == "ID":
            continue

        value = values[value_index]
        value_index += 1

        if not is_valid_type(value, column_type):
            print(
                f"Некорректное значение: {value}. "
                "Попробуйте снова."
            )
            return table_data

        record[column_name] = value

    new_id = max(
        (record["ID"] for record in table_data),
        default=0,
    ) + 1

    record = {"ID": new_id, **record}
    new_table_data = table_data + [record]

    cache_result.clear()

    print(
        f'Запись с ID={new_id} успешно добавлена '
        f'в таблицу "{table_name}".'
    )

    return new_table_data


@handle_db_errors
@log_time
def select(metadata, table_name, table_data, where=None):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return []

    if not validate_condition(metadata, table_name, where):
        return []

    if where is None:
        cache_where = None
    else:
        column_name, value = where
        cache_where = (column_name, type(value).__name__, value)

    key = (table_name, cache_where)

    return cache_result(
        key,
        lambda: filter_records(table_data, where),
    )


@handle_db_errors
@log_time
def update(
    metadata,
    table_name,
    table_data,
    column_name,
    new_value,
    where,
):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return table_data

    columns = get_column_info(metadata, table_name)
    column_types = dict(columns)

    if column_name not in column_types:
        print(
            f"Некорректное значение: {column_name}. "
            "Попробуйте снова."
        )
        return table_data

    if column_name == "ID":
        print("Нельзя изменять ID. Попробуйте снова.")
        return table_data

    if not is_valid_type(new_value, column_types[column_name]):
        print(
            f"Некорректное значение: {new_value}. "
            "Попробуйте снова."
        )
        return table_data

    if not validate_condition(metadata, table_name, where):
        return table_data

    where_column, where_value = where
    updated_ids = []
    new_table_data = []

    for record in table_data:
        new_record = record.copy()

        if new_record.get(where_column) == where_value:
            new_record[column_name] = new_value
            updated_ids.append(new_record["ID"])

        new_table_data.append(new_record)

    if not updated_ids:
        print("Запись не найдена. Попробуйте снова.")
        return table_data

    for record_id in updated_ids:
        print(
            f'Запись с ID={record_id} в таблице '
            f'"{table_name}" успешно обновлена.'
        )

    cache_result.clear()

    return new_table_data


@handle_db_errors
@confirm_action("удаление записи")
def delete(metadata, table_name, table_data, where):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return table_data

    if not validate_condition(metadata, table_name, where):
        return table_data

    where_column, where_value = where

    deleted_ids = [
        record["ID"]
        for record in table_data
        if record.get(where_column) == where_value
    ]

    if not deleted_ids:
        print("Запись не найдена. Попробуйте снова.")
        return table_data

    new_table_data = [
        record
        for record in table_data
        if record.get(where_column) != where_value
    ]

    for record_id in deleted_ids:
        print(
            f'Запись с ID={record_id} успешно удалена '
            f'из таблицы "{table_name}".'
        )

    cache_result.clear()

    return new_table_data
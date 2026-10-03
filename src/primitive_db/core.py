def create_table(metadata, table_name, columns):
    if not table_name.replace("_", "").isalnum():
        print(f"Некорректное значение: {table_name}. Попробуйте снова.")
        return metadata

    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    valid_types = {"int", "str", "bool"}

    for column in columns:
        column_name, column_type = column.split(":")

        if column_type not in valid_types:
            print(f"Некорректное значение: {column_type}. Попробуйте снова.")
            return metadata

    columns = ["ID:int"] + columns
    metadata[table_name] = columns

    return metadata


def drop_table(metadata, table_name):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]

    return metadata
def create_table(metadata, table_name, columns):
    if not table_name.replace("_", "").isalnum():
        print(f"Некорректное значение: {table_name}. Попробуйте снова.")
        return metadata

    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

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
                f"Некорректное значение: {column_type}. Попробуйте снова."
            )
            return metadata

        parsed_columns.append((column_name, column_type))

    if not any(column_name.lower() == "id" for column_name, _ in parsed_columns):
        parsed_columns.insert(0, ("ID", "int"))

    columns = [f"{column_name}:{column_type}" for column_name, column_type in parsed_columns]

    metadata[table_name] = columns
    
    print(f'Таблица "{table_name}" успешно создана '
    f'со столбцами: {", ".join(columns)}')

    return metadata


def list_tables(metadata):
    if not metadata:
        print("В базе данных нет таблиц.")
        return

    for table_name in metadata:
        print(f"- {table_name}")


def drop_table(metadata, table_name):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')

    return metadata
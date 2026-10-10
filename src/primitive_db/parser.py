
def parse_value(value):
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]

    if value.lower() == "true":
        return True

    if value.lower() == "false":
        return False

    try:
        return int(value)
    except ValueError:
        raise ValueError(f"Некорректное значение: {value}")


def split_values(values_text):
    values = []
    current_value = []
    inside_quotes = False

    for char in values_text:
        if char == '"':
            inside_quotes = not inside_quotes
            current_value.append(char)
        elif char == "," and not inside_quotes:
            values.append("".join(current_value).strip())
            current_value = []
        else:
            current_value.append(char)

    if inside_quotes:
        raise ValueError("Незакрытые кавычки.")

    values.append("".join(current_value).strip())

    if any(not value for value in values):
        raise ValueError("Некорректный список значений.")

    return values


def parse_insert(parts):
    if len(parts) < 5:
        raise ValueError("Некорректная команда insert.")

    if parts[0] != "insert" or parts[1] != "into":
        raise ValueError("Некорректная команда insert.")

    table_name = parts[2]

    if parts[3] != "values":
        raise ValueError("Ожидается ключевое слово values.")

    values_text = " ".join(parts[4:]).strip()

    if not values_text.startswith("(") or not values_text.endswith(")"):
        raise ValueError("Значения должны быть заключены в скобки.")

    values_text = values_text[1:-1].strip()

    if not values_text:
        raise ValueError("Список значений не может быть пустым.")

    raw_values = split_values(values_text)

    for value in raw_values:
        if "(" in value or ")" in value:
            raise ValueError("Некорректная структура команды insert.")

    values = [parse_value(value) for value in raw_values]

    return table_name, values


def parse_select(parts):
    if len(parts) < 3:
        raise ValueError("Некорректная команда select.")

    if parts[0] != "select" or parts[1] != "from":
        raise ValueError("Некорректная команда select.")

    table_name = parts[2]

    if len(parts) == 3:
        return table_name, None

    if len(parts) != 7:
        raise ValueError("Некорректное условие select.")

    if parts[3] != "where" or parts[5] != "=":
        raise ValueError("Некорректное условие select.")

    column_name = parts[4]
    value = parse_value(parts[6])

    return table_name, (column_name, value)


def parse_update(parts):
    if len(parts) != 10:
        raise ValueError("Некорректная команда update.")

    if parts[0] != "update" or parts[2] != "set":
        raise ValueError("Некорректная команда update.")

    if parts[4] != "=" or parts[6] != "where" or parts[8] != "=":
        raise ValueError("Некорректная команда update.")

    table_name = parts[1]
    column_name = parts[3]
    new_value = parse_value(parts[5])
    where_column = parts[7]
    where_value = parse_value(parts[9])

    return (
        table_name,
        column_name,
        new_value,
        (where_column, where_value),
    )


def parse_delete(parts):
    if len(parts) != 7:
        raise ValueError("Некорректная команда delete.")

    if parts[0] != "delete" or parts[1] != "from":
        raise ValueError("Некорректная команда delete.")

    if parts[3] != "where" or parts[5] != "=":
        raise ValueError("Некорректная команда delete.")

    table_name = parts[2]
    column_name = parts[4]
    value = parse_value(parts[6])

    return table_name, (column_name, value)

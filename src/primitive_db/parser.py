def parse_value(value):
    if value == "true":
        return True

    if value == "false":
        return False

    try:
        return int(value)
    except ValueError:
        pass

    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]

    raise ValueError(value)

def parse_insert(parts):
    if len(parts) < 5:
        raise ValueError("Некорректный синтаксис")

    if parts[0] != "insert":
        raise ValueError("Некорректная команда")

    if parts[1] != "into":
        raise ValueError("Ожидалось into")

    table_name = parts[2]

    if parts[3] != "values":
        raise ValueError("Ожидалось values")

    values_text = " ".join(parts[4:])

    if not values_text.startswith("(") or not values_text.endswith(")"):
        raise ValueError("Значения должны быть в скобках")

    values_text = values_text[1:-1].strip()

    if not values_text:
        raise ValueError("Пустой список значений")

    raw_values = []
    current_value = ""
    inside_quotes = False

    for char in values_text:
        if char == '"':
            inside_quotes = not inside_quotes
            current_value += char
        elif char == "," and not inside_quotes:
            raw_values.append(current_value.strip())
            current_value = ""
        else:
            current_value += char

    if inside_quotes:
        raise ValueError("Незакрытая строка")

    raw_values.append(current_value.strip())

    values = [parse_value(value) for value in raw_values]

    return table_name, values

def parse_select(parts):
    if len(parts) < 3:
        raise ValueError("Некорректный синтаксис")

    if parts[0] != "select":
        raise ValueError("Некорректная команда")

    if parts[1] != "from":
        raise ValueError("Ожидалось from")

    table_name = parts[2]

    if len(parts) == 3:
        return table_name, None

    if len(parts) != 7:
        raise ValueError("Некорректный синтаксис")

    if parts[3] != "where":
        raise ValueError("Ожидалось where")

    if parts[5] != "=":
        raise ValueError("Ожидался знак =")

    column_name = parts[4]
    value = parse_value(parts[6])

    return table_name, (column_name, value)

def parse_update(parts):
    if len(parts) != 10:
        raise ValueError("Некорректный синтаксис")

    if parts[0] != "update":
        raise ValueError("Некорректная команда")

    table_name = parts[1]

    if parts[2] != "set":
        raise ValueError("Ожидалось set")

    if parts[4] != "=":
        raise ValueError("Ожидался знак =")

    if parts[6] != "where":
        raise ValueError("Ожидалось where")

    if parts[8] != "=":
        raise ValueError("Ожидался знак =")

    column_name = parts[3]
    new_value = parse_value(parts[5])

    where_column = parts[7]
    where_value = parse_value(parts[9])

    return table_name, column_name, new_value, (where_column, where_value)

def parse_delete(parts):
    if len(parts) != 7:
        raise ValueError("Некорректный синтаксис")

    if parts[0] != "delete":
        raise ValueError("Некорректная команда")

    if parts[1] != "from":
        raise ValueError("Ожидалось from")

    table_name = parts[2]

    if parts[3] != "where":
        raise ValueError("Ожидалось where")

    if parts[5] != "=":
        raise ValueError("Ожидался знак =")

    column_name = parts[4]
    value = parse_value(parts[6])

    return table_name, (column_name, value)
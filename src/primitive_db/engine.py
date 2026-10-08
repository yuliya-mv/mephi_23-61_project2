import shlex

from prettytable import PrettyTable

from primitive_db.core import (
    create_table,
    delete,
    drop_table,
    info_table,
    insert,
    list_tables,
    select,
    update,
)
from primitive_db.parser import (
    parse_delete,
    parse_insert,
    parse_select,
    parse_update,
)
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def run():
    while True:
        metadata = load_metadata("db_meta.json")
        command = input("Введите команду: ")

        parts = shlex.split(command, posix=False)

        if not parts:
            continue

        if parts[0] == "exit":
            break

        elif parts[0] == "help":
            show_help()

        elif parts[0] == "create_table":
            if len(parts) < 2:
                print(
                    "Для функции create_table нет имени таблицы. " \
                    "Попробуйте снова."
                )
                continue

            if len(parts) < 3:
                print(
                    "Для функции create_table не хватает столбцов. " \
                    "Попробуйте снова."
                )
                continue

            table_name = parts[1]
            columns = parts[2:]
            metadata = create_table(metadata, table_name, columns)
            save_metadata("db_meta.json", metadata)

        elif parts[0] == "list_tables":
            list_tables(metadata)

        elif parts[0] == "info":
            if len(parts) < 2:
                print(
                    "Для функции info не хватает имени таблицы. Попробуйте снова."
                )
                continue

            table_name = parts[1]

            table_data = load_table_data(
                f"data/{table_name}.json"
            )

            info_table(
                metadata,
                table_name,
                table_data,
            )

        elif parts[0] == "insert":
            try:
                table_name, values = parse_insert(parts)

                if table_name not in metadata:
                    print(f'Ошибка: Таблица "{table_name}" не существует.')
                    continue

                table_data = load_table_data(
                    f"data/{table_name}.json"
                )

                table_data = insert(
                    metadata,
                    table_name,
                    table_data,
                    values,
                )

                save_table_data(
                    f"data/{table_name}.json",
                    table_data,
                )

            except ValueError:
                print(
                    "Некорректное значение. Попробуйте снова."
                )

        elif parts[0] == "select":
            try:
                table_name, where = parse_select(parts)

                table_data = load_table_data(
                    f"data/{table_name}.json"
                )

                result = select(
                    metadata,
                    table_name,
                    table_data,
                    where,
                )

                table = PrettyTable()

                if result:
                    table.field_names = result[0].keys()

                    for record in result:
                        table.add_row(record.values())

                    print(table)

            except ValueError:
                print(
                    "Некорректное val. "
                    "Попробуйте снова."
                )

        elif parts[0] == "update":
            try:
                (
                    table_name,
                    column_name,
                    new_value,
                    where,
                ) = parse_update(parts)

                if table_name not in metadata:
                    print(f'Ошибка: Таблица "{table_name}" не существует.')
                    continue

                table_data = load_table_data(
                    f"data/{table_name}.json"
                )

                new_table_data = update(
                    metadata,
                    table_name,
                    table_data,
                    column_name,
                    new_value,
                    where,
                )

                if new_table_data != table_data:
                    save_table_data(
                        f"data/{table_name}.json",
                        new_table_data,
                    )
            except ValueError:
                print(
                    "Некорректное val. "
                    "Попробуйте снова."
                )

        elif parts[0] == "delete":
            try:
                table_name, where = parse_delete(parts)

                if table_name not in metadata:
                    print(f'Ошибка: Таблица "{table_name}" не существует.')
                    continue

                table_data = load_table_data(
                    f"data/{table_name}.json"
                )

                new_table_data = delete(
                    metadata,
                    table_name,
                    table_data,
                    where,
                )

                if new_table_data is not None and new_table_data != table_data:
                    save_table_data(
                        f"data/{table_name}.json",
                        new_table_data,
                    )

            except ValueError:
                print(
                    "Некорректное val. "
                    "Попробуйте снова."
                )

        elif parts[0] == "drop_table":
            if len(parts) < 2:
                print(
                    "Для функции drop_table не хватает имени таблицы. "
                    "Попробуйте снова."
                )
                continue

            table_name = parts[1]
            metadata = drop_table(metadata, table_name)
            save_metadata("db_meta.json", metadata)

        else:
            print(
                f"Функции {parts[0]} нет. "
                "Попробуйте снова."
            )

def show_help():
    print(
        "<cmd> create_table <имя_таблицы> <Col1:type> <Col2:type> - создать таблицу\n"
        "<cmd> list_tables - показать список всех таблиц\n"
        "<cmd> drop_table <имя_таблицы> - удалить таблицу\n\n"
        "<cmd> insert into <имя_таблицы> values (<val1>, <val2>, ..) - создать запись\n"
        "<cmd> select from <имя_таблицы> where <Col> = <val>"
        "- найти записи по условию\n"
        "<cmd> select from <имя_таблицы> - прочитать все записи\n"
        "<cmd> update <имя_таблицы> set <Col1> = <новое_val1> "
        "where <Col_условия> = <val_условия> - обновить запись\n"
        "<cmd> delete from <имя_таблицы> where <Col> = <val> - удалить запись\n\n"
        "<cmd> info <имя_таблицы> - вывести информацию о таблице\n"
        "<cmd> exit - выход из программы\n"
        "<cmd> help - справочная информация"
    )
import shlex
from prettytable import PrettyTable
from prompt import string

from primitive_db.core import (
    create_table,
    drop_table,
    list_tables,
    insert,
    select,
    update,
    delete,
)
from primitive_db.parser import (
    parse_insert,
    parse_select,
    parse_update,
    parse_delete,
)
from primitive_db.utils import (
    load_metadata,
    save_metadata,
    load_table_data,
    save_table_data,
)


def welcome():
    print(
        "project\n\n"
        "Первая попытка запустить проект!\n\n"
        "***\n"
        "<command> exit - выйти из программы\n"
        "<command> help - справочная информация"
    )

    command = string("Введите команду: ")

    while command != "exit":
        if command == "help":
            print(
                "\n"
                "<command> exit - выйти из программы\n"
                "<command> help - справочная информация"
            )

        command = string("Введите команду: ")

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
                    "Для функции create_table не хватает имени таблицы. "
                    "Попробуйте снова."
                )
                continue

            if len(parts) < 3:
                print(
                    "Для функции create_table не хватает столбцов. "
                    "Попробуйте снова."
                )
                continue

            table_name = parts[1]
            columns = parts[2:]
            metadata = create_table(metadata, table_name, columns)
            save_metadata("db_meta.json", metadata)

        elif parts[0] == "list_tables":
            list_tables(metadata)

        elif parts[0] == "insert":
            try:
                table_name, values = parse_insert(parts)

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
                    "Некорректное значение. "
                    "Попробуйте снова."
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
                    "Некорректное значение. "
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

                table_data = load_table_data(
                    f"data/{table_name}.json"
                )

                table_data = update(
                    metadata,
                    table_name,
                    table_data,
                    column_name,
                    new_value,
                    where,
                )

                save_table_data(
                    f"data/{table_name}.json",
                    table_data,
                )

            except ValueError:
                print(
                    "Некорректное значение. "
                    "Попробуйте снова."
                )

        elif parts[0] == "delete":
            try:
                table_name, where = parse_delete(parts)

                table_data = load_table_data(
                    f"data/{table_name}.json"
                )

                table_data = delete(
                    metadata,
                    table_name,
                    table_data,
                    where,
                )

                save_table_data(
                    f"data/{table_name}.json",
                    table_data,
                )

            except ValueError:
                print(
                    "Некорректное значение. "
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
        "<cmd> drop_table <имя_таблицы> - удалить таблицу\n"
        "<cmd> exit - выход из программы\n"
        "<cmd> help - справочная информация"
    )
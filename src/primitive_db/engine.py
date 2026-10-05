import shlex

from prompt import string

from primitive_db.core import create_table, drop_table, list_tables
from primitive_db.utils import load_metadata, save_metadata


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

        parts = shlex.split(command)

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
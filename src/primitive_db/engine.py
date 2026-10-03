import shlex

from prompt import string

from primitive_db.core import create_table, drop_table
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

        if parts[0] == "create_table":
            table_name = parts[1]
            columns = parts[2:]
            metadata = create_table(metadata, table_name, columns)
            save_metadata("db_meta.json", metadata)

        elif parts[0] == "drop_table":
            table_name = parts[1]
            metadata = drop_table(metadata, table_name)
            save_metadata("db_meta.json", metadata)

        else:
            print(f"Некорректное значение: {parts[0]}. Попробуйте снова.")
from prompt import string


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
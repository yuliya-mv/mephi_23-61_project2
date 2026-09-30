from prompt import string


def welcome():
    print("***")
    print("<command> exit - выйти из программы")
    print("<command> help - справочная информация")

    command = string("Введите команду: ")

    while command != "exit":
        if command == "help":
            print("<command> exit - выйти из программы")
            print("<command> help - справочная информация")

        command = string("Введите команду: ")
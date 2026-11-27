# Rodrigo Ferreira de Queiroz Souza / Yasmim Aparecida Ramos Siqueira / Lucas Vieira Nascimento
# Projeto final de PBC

# Arquivo para inicializar o programa
import sys
import tkinter as tk

from admin_app import AdminConsole
from gui import ComicApp
from backend import DataBase


if __name__ == "__main__":
    database = DataBase()
    admin_arguments = {"admin", "--admin", "-a"}
    if len(sys.argv) > 1 and sys.argv[1].casefold() in admin_arguments:
        AdminConsole(database).run()
    else:
        root = tk.Tk()
        app = ComicApp(root, database)
        root.mainloop()

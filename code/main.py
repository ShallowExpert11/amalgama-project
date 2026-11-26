# Rodrigo Ferreira de Queiroz Souza / Yasmim Aparecida Ramos Siqueira / Lucas Vieira Nascimento
# Projeto final de PBC

# Módulo principal do programa
from console_app import AdminConsole
from database import DataBase


if __name__ == "__main__":
    AdminConsole(DataBase()).run()

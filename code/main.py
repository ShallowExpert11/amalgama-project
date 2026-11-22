# Rodrigo Ferreira de Queiroz Souza / Yasmim Aparecida Ramos Siqueira / Lucas Vieira Nascimento
# Projeto final de PBC

# Módulo principal do programa
from database import DataBase

database = DataBase()
comics = database.load_comics()

print(comics)
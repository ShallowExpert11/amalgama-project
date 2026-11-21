#AMALGAMA COMIX - Qualidade e excelênca em quadrinhos raros
#Rodrigo F Q. Souza / Yasmim A. R. Siqueira / Lucas Vieira

#Importação de todas as bibliotecas necessárias
import json
import os
import tkinter as tk
from time import sleep as loading


#Estabelecendo as classes necessárias para o funcionamento do sistema


class DataBase:#Classe que define o banco de dados do sistema

    def __init__(self):#Atributos do BD
        self.data_folder = "data"
        self.file_path = os.path.join(self.data_folder, "comics.json")

    def initialize(self):#Método que inicializa o BD
        os.makedirs(self.data_folder, exist_ok=True)

        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as file:
                json.dump([], file, indent=4)

    def load(self):#Método que carrega os dados do BD
        with open(self.file_path, "r") as file:
            return json.load(file)

    def save(self, data):#Método que salva os dados no BD
        with open(self.file_path, "w") as file:
            json.dump(data, file, indent=4)


class comic: #Classe que define os atributos de uma HQ
    
    def __init__ (self, id, title_eng, title_pt, author, artist, data, qualty, price):
        self.id = id
        self.title_eng = title_eng
        self.title_pt = title_pt
        self.author = author
        self.artist = artist
        self.data = data
        self.qualty = qualty
        self.price = price


class user:#Classe que define os atributos de um usuário
    
    def __init__ (self, name, username, password):
        self.name = name
        self.email = username
        self.password = password


class admin:#Classe que define os atributos de um administrador
    
    def __init__ (self, name, username, password):
        self.name = name
        self.email = username
        self.password = password


class comicApp:#Classe que define os atributos do sistema
    
    def __init__(self):#Atributos do sistema
       self.root = tk.Tk()
       self.root.title("AMALGAMA COMIX")
       self.root.geometry("1920x1080")

    def welcome(self):#Método que exibe a tela de boas-vindas
        self.root.configure(bg="black")
        welcome_label = tk.Label(self.root, text="Bem-vindo à Amalgama Comix!", font=("Arial", 24), fg="white", bg="black")
        welcome_label.pack(pady=20)
        loading(2)
        self.root.destroy()


if __name__ == "__main__":
    app = comicApp()
    app.welcome()

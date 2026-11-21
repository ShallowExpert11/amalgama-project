#Rodrigo F Q. Souza / Yasmim A. R. Siqueira / Lucas Vieira

#Importação de todas as bibliotecas necessárias
import json
import os
import tkinter as tk
from time import sleep as loading


#Estabelecendo as classes necessárias para o funcionamento do sistema

class comic: #Classe que define os atributos de uma HQ
    def __init__ (self, id, title_eng, title_pt, author, artist, data, price):
        self.id = id
        self.title_eng = title_eng
        self.title_pt = title_pt
        self.author = author
        self.artist = artist
        self.data = data
        self.price = price
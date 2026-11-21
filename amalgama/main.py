
# AMALGAMA COMIX - Qualidade e excelencia em quadrinhos raros
# Rodrigo F Q. Souza / Yasmim A. R. Siqueira / Lucas Vieira


# Importação de todas as bibliotecas necessarias

import json
import os
import tkinter as tk
import hashlib
import secrets
import shutil
import uuid

from tkinter import filedialog, messagebox


# Info de login do administrador

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Amalgama123"

# Cores da interface do programa

BACKGROUND = "#071A36"
SECONDARY = "#102B50"
CARD = "#153963"
BLUE = "#0878D1"
LIGHT_BLUE = "#55A9F5"
YELLOW = "#F5C542"
WHITE = "#FFFFFF"
GRAY = "#B8C9DD"
RED = "#E85D5D"


# Classe que define o BD

class DataBase:

    # Inicializa os caminhos dos arquivos
    def __init__(self):

        self.data_folder = "data"

        self.file_path = os.path.join(
            self.data_folder,
            "comics.json"
        )

        self.users_path = os.path.join(
            self.data_folder,
            "users.json"
        )

        self.images_folder = os.path.join(
            self.data_folder,
            "images"
        )

    # Cria as pastas e os arquivos necessarios
    def initialize(self):

        os.makedirs(self.data_folder, exist_ok=True)
        os.makedirs(self.images_folder, exist_ok=True)

        if not os.path.exists(self.file_path):

            with open(self.file_path, "w", encoding="utf-8") as file:
                json.dump([], file, indent=4)

        if not os.path.exists(self.users_path):

            with open(self.users_path, "w", encoding="utf-8") as file:
                json.dump([], file, indent=4)

        self.createAdmin()

    # Carrega os quadrinhos do JSON
    def load(self):

        with open(self.file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    # Salva os quadrinhos no JSON
    def save(self, data):

        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    # Carrega os usuarios do JSON
    def load_users(self):

        with open(self.users_path, "r", encoding="utf-8") as file:
            return json.load(file)

    # Salva os usuarios no JSON
    def save_users(self, users):

        with open(self.users_path, "w", encoding="utf-8") as file:
            json.dump(users, file, indent=4, ensure_ascii=False)

    # Verifica se determinado nome de usuario ja existe
    def userExists(self, username):

        users = self.load_users()

        for user in users:

            if user["username"].lower() == username.lower():
                return True

        return False

    # Protege a senha utilizando hash e salt
    def hashPassword(self, password):

        salt = secrets.token_hex(16)

        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            600000
        ).hex()

        return salt, password_hash

    # Verifica se a senha digitada corresponde ao hash armazenado
    def verifyPassword(self, password, salt, password_hash):

        test_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            600000
        ).hex()

        return secrets.compare_digest(test_hash, password_hash)

    # Adiciona um novo usuario comum
    def addUser(self, name, username, password):

        users = self.load_users()

        salt, password_hash = self.hashPassword(password)

        new_user = {
            "name": name,
            "username": username,
            "salt": salt,
            "password_hash": password_hash,
            "role": "user"
        }

        users.append(new_user)

        self.save_users(users)

    # Cria a conta administrativa separadamente
    def createAdmin(self):

        users = self.load_users()

        for user in users:

            if user["username"].lower() == ADMIN_USERNAME.lower():

                if user.get("role") == "admin":
                    return

                raise ValueError(
                    "O nome de usuario reservado para o administrador "
                    "ja esta sendo utilizado."
                )

        salt, password_hash = self.hashPassword(ADMIN_PASSWORD)

        new_admin = {
            "name": "Administrador",
            "username": ADMIN_USERNAME,
            "salt": salt,
            "password_hash": password_hash,
            "role": "admin"
        }

        users.append(new_admin)

        self.save_users(users)

    # Verifica as credenciais do login
    def checkLogin(self, username, password):

        users = self.load_users()

        for user in users:

            if user["username"].lower() == username.lower():

                if self.verifyPassword(
                    password,
                    user["salt"],
                    user["password_hash"]
                ):
                    return user

                return None

        return None

    # Gera um novo ID para o quadrinho
    def nextComicID(self):

        comics = self.load()

        if not comics:
            return 1

        return max(item["id"] for item in comics) + 1

    # Adiciona um quadrinho ao catalogo
    def addComic(self, comic_data):

        comics = self.load()

        comics.append(comic_data)

        self.save(comics)

    # Atualiza as informacoes de um quadrinho
    def updateComic(self, comic_id, updated_data):

        comics = self.load()

        for index, item in enumerate(comics):

            if item["id"] == comic_id:

                comics[index] = updated_data

                self.save(comics)

                return True

        return False

    # Exclui um quadrinho do catalogo
    def deleteComic(self, comic_id):

        comics = self.load()

        updated_comics = [
            item for item in comics
            if item["id"] != comic_id
        ]

        self.save(updated_comics)


# Classe que define as HQs

class comic:

    def __init__(
        self,
        id,
        title_eng,
        title_pt,
        author,
        artist,
        data,
        quality,
        price,
        cover="",
        back_cover=""
    ):

        self.id = id
        self.title_eng = title_eng
        self.title_pt = title_pt
        self.author = author
        self.artist = artist
        self.data = data
        self.quality = quality
        self.price = price
        self.cover = cover
        self.back_cover = back_cover


# Classe que define os usuários comuns

class user:

    def __init__(self, name, username):

        self.name = name
        self.username = username


# Classe que define os usuários administradores

class admin(user):

    def __init__(self, name, username):

        super().__init__(name, username)


# Classe principal do programa

class comicApp:

    # Inicializa a janela e os atributos do programa
    def __init__(self):

        self.root = tk.Tk()

        self.root.title("AMALGAMA COMIX")

        self.root.geometry("1920x1080")

        self.root.minsize(800, 600)

        self.root.configure(bg=BACKGROUND)

        self.db = DataBase()

        self.db.initialize()

        self.current_user = None

        self.cart = {}

        self.selected_cover = ""
        self.selected_back_cover = ""

        self.editing_comic_id = None

        self.image_references = []

    # Limpa todos os elementos da janela
    def clearScreen(self):

        for widget in self.root.winfo_children():
            widget.destroy()

        self.image_references = []

    # Cria um titulo ou texto padronizado
    def createLabel(self, parent, text, size=12, bold=False, color=WHITE):

        font_style = "bold" if bold else "normal"

        return tk.Label(
            parent,
            text=text,
            font=("Arial", size, font_style),
            fg=color,
            bg=parent.cget("bg")
        )

    # Cria um botao personalizado
    def createButton(self, parent, text, command, color=BLUE):

        return tk.Button(
            parent,
            text=text,
            command=command,
            font=("Arial", 11, "bold"),
            bg=color,
            fg=WHITE,
            activebackground=LIGHT_BLUE,
            activeforeground=WHITE,
            relief="flat",
            cursor="hand2",
            width=25,
            pady=9
        )

    # Cria o cabecalho padronizado
    def createHeader(self, title, subtitle=""):

        header = tk.Frame(
            self.root,
            bg=BACKGROUND
        )

        header.pack(fill="x", padx=35, pady=20)

        self.createLabel(
            header,
            "AMALGAMA",
            25,
            True,
            WHITE
        ).pack(side="left")

        tk.Label(
            header,
            text="COMIX",
            font=("Arial", 15, "bold"),
            fg=YELLOW,
            bg=BACKGROUND
        ).pack(side="left", padx=8, pady=8)

        self.createLabel(
            self.root,
            title,
            23,
            True
        ).pack(pady=(15, 5))

        if subtitle:

            self.createLabel(
                self.root,
                subtitle,
                11,
                False,
                GRAY
            ).pack(pady=5)

    # Cria uma area central para organizar os elementos
    def createContent(self):

        content = tk.Frame(
            self.root,
            bg=BACKGROUND
        )

        content.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=20
        )

        return content

    # Tela de boas-vindas
    def welcome(self):

        self.clearScreen()

        self.createHeader(
            "Qualidade e excêlencia no serviço",
            "Uma biblioteca de historias extraordinarias..."
            
        )

        self.createLabel(
            self.root,
            "ENCONTRE QUADRINHOS RAROS E EXCLUSIVOS",
            19,
            True,
            YELLOW
        ).pack(pady=65)

        self.createLabel(
            self.root,
            "Explore uma coleção especial de quadrinhos.",
            12,
            False,
            GRAY
        ).pack(pady=5)

        self.root.after(3555, self.mainMenu)

    # Menu inicial
    def mainMenu(self):

        self.clearScreen()

        self.createHeader(
            "BEM-VINDO!",
            "Entre na sua conta ou crie seu cadastro."
        )

        content = self.createContent()

        tk.Frame(
            content,
            bg=SECONDARY,
            padx=35,
            pady=35
        ).pack(pady=35)

        self.createButton(
            content,
            "CRIAR CONTA",
            self.signUp
        ).pack(pady=10)

        self.createButton(
            content,
            "ENTRAR",
            self.logIn,
            YELLOW
        ).pack(pady=10)

    # Tela de cadastro
    def signUp(self):

        self.clearScreen()

        self.createHeader("CRIAR CONTA")

        content = self.createContent()

        self.error_label = tk.Label(
            content,
            text="",
            fg=RED,
            bg=BACKGROUND
        )

        self.error_label.pack(pady=5)

        self.createLabel(content, "Nome:").pack()

        self.signup_entry1 = tk.Entry(content, width=38)
        self.signup_entry1.pack(pady=6)

        self.createLabel(content, "Nome de usuario:").pack()

        self.signup_entry2 = tk.Entry(content, width=38)
        self.signup_entry2.pack(pady=6)

        self.createLabel(content, "Senha:").pack()

        self.signup_entry3 = tk.Entry(
            content,
            width=38,
            show="*"
        )

        self.signup_entry3.pack(pady=6)

        self.createLabel(content, "Confirmar senha:").pack()

        self.signup_entry4 = tk.Entry(
            content,
            width=38,
            show="*"
        )

        self.signup_entry4.pack(pady=6)

        self.createButton(
            content,
            "CADASTRAR",
            self.submitSignUp
        ).pack(pady=15)

        self.createButton(
            content,
            "VOLTAR",
            self.mainMenu,
            SECONDARY
        ).pack()

    # Verifica se as informacoes do cadastro sao validas
    def credValidation(self, name, username, password, confirm_password):

        if not name.strip():
            return 1

        if not username.strip():
            return 2

        if username.lower() == ADMIN_USERNAME.lower():
            return 5

        if (
            len(password) < 6
            or not any(char.isalpha() for char in password)
            or not any(char.isdigit() for char in password)
        ):
            return 3

        if password != confirm_password:
            return 4

        if self.db.userExists(username):
            return 5

        return 0

    # Finaliza o cadastro do usuario
    def submitSignUp(self):

        name = self.signup_entry1.get().strip()
        username = self.signup_entry2.get().strip()
        password = self.signup_entry3.get()
        confirm_password = self.signup_entry4.get()

        result = self.credValidation(
            name,
            username,
            password,
            confirm_password
        )

        match result:

            case 0:

                self.db.addUser(name, username, password)

                self.error_label.config(
                    text="Cadastro realizado com sucesso!",
                    fg="#50D890"
                )

                self.signup_entry1.delete(0, tk.END)
                self.signup_entry2.delete(0, tk.END)
                self.signup_entry3.delete(0, tk.END)
                self.signup_entry4.delete(0, tk.END)

            case 1:
                self.error_label.config(text="Digite seu nome!", fg=RED)

            case 2:
                self.error_label.config(text="Digite um nome de usuario!", fg=RED)

            case 3:
                self.error_label.config(
                    text="A senha precisa ter 6 caracteres, uma letra e um numero!",
                    fg=RED
                )

            case 4:
                self.error_label.config(text="As senhas nao sao iguais!", fg=RED)

            case 5:
                self.error_label.config(text="Nome de usuario indisponivel!", fg=RED)

    # Tela de login
    def logIn(self):

        self.clearScreen()

        self.createHeader("ENTRAR NA CONTA")

        content = self.createContent()

        self.login_error_label = tk.Label(
            content,
            text="",
            fg=RED,
            bg=BACKGROUND
        )

        self.login_error_label.pack(pady=8)

        self.createLabel(content, "Nome de usuario:").pack()

        self.login_username = tk.Entry(content, width=38)
        self.login_username.pack(pady=6)

        self.createLabel(content, "Senha:").pack()

        self.login_password = tk.Entry(
            content,
            width=38,
            show="*"
        )

        self.login_password.pack(pady=6)

        self.createButton(
            content,
            "ENTRAR",
            self.submitLogin
        ).pack(pady=15)

        self.createButton(
            content,
            "VOLTAR",
            self.mainMenu,
            SECONDARY
        ).pack()

    # Verifica o login e identifica o tipo de usuario
    def submitLogin(self):

        username = self.login_username.get()
        password = self.login_password.get()

        if not username.strip() or not password:

            self.login_error_label.config(
                text="Preencha todos os campos!"
            )

            return

        logged_user = self.db.checkLogin(username, password)

        if logged_user:

            self.current_user = logged_user

            if logged_user.get("role") == "admin":
                self.adminMenu()

            else:
                self.userMenu()

        else:

            self.login_error_label.config(
                text="Usuario ou senha incorretos!"
            )

    # Menu do usuario comum
    def userMenu(self):

        self.clearScreen()

        self.createHeader(
            f"OLÁ, {self.current_user['name'].upper()}!",
            "O que deseja fazer hoje?"
        )

        content = self.createContent()

        self.createButton(
            content,    
            "BUSCAR QUADRINHOS",
            self.searchScreen
        ).pack(pady=12)

        self.createButton(
            content,
            "MEU CARRINHO",
            self.showCart,
            YELLOW
        ).pack(pady=12)

        self.createButton(
            content,
            "SAIR DA CONTA",
            self.logout,
            SECONDARY
        ).pack(pady=12)

    # Tela de pesquisa
    def searchScreen(self):

        self.clearScreen()

        self.createHeader(
            "CATALOGO DE QUADRINHOS",
            "Pesquise por titulo, autor ou artista."
        )

        content = self.createContent()

        self.search_entry = tk.Entry(
            content,
            font=("Arial", 12),
            width=45
        )

        self.search_entry.pack(pady=10)

        self.createButton(
            content,
            "PESQUISAR",
            self.searchComics
        ).pack(pady=5)

        self.results_list = tk.Listbox(
            content,
            width=85,
            height=13,
            bg=SECONDARY,
            fg=WHITE,
            selectbackground=BLUE,
            font=("Arial", 10),
            relief="flat"
        )

        self.results_list.pack(pady=15)

        self.search_results = []

        self.createButton(
            content,
            "VER DETALHES",
            self.selectedComicDetails
        ).pack(pady=5)

        self.createButton(
            content,
            "ADICIONAR AO CARRINHO",
            self.addToCart,
            YELLOW
        ).pack(pady=5)

        self.createButton(
            content,
            "VOLTAR",
            self.userMenu,
            SECONDARY
        ).pack(pady=10)

    # Pesquisa quadrinhos pelo titulo, autor ou artista
    def searchComics(self):

        query = self.search_entry.get().lower().strip()

        comics = self.db.load()

        self.results_list.delete(0, tk.END)

        self.search_results = []

        for comic_data in comics:

            searchable_text = (
                comic_data["title_eng"]
                + " "
                + comic_data["title_pt"]
                + " "
                + comic_data["author"]
                + " "
                + comic_data["artist"]
            ).lower()

            if query in searchable_text:

                self.search_results.append(comic_data)

                self.results_list.insert(
                    tk.END,
                    f"{comic_data['id']} | "
                    f"{comic_data['title_pt']} | "
                    f"{comic_data['author']} | "
                    f"R$ {comic_data['price']:.2f}"
                )

        if not self.search_results:

            self.results_list.insert(
                tk.END,
                "Nenhum quadrinho encontrado."
            )

    # Retorna o quadrinho selecionado na pesquisa
    def getSelectedSearchComic(self):

        selection = self.results_list.curselection()

        if not selection:

            messagebox.showwarning(
                "Atencao",
                "Selecione um quadrinho primeiro!"
            )

            return None

        index = selection[0]

        if index >= len(self.search_results):
            return None

        return self.search_results[index]

    # Abre os detalhes do quadrinho selecionado
    def selectedComicDetails(self):

        selected = self.getSelectedSearchComic()

        if selected:
            self.showComicDetails(selected)

    # Exibe as informacoes e as imagens do quadrinho
    def showComicDetails(self, comic_data):

        window = tk.Toplevel(self.root)

        window.title(comic_data["title_pt"])

        window.geometry("650x650")

        window.configure(bg=BACKGROUND)

        tk.Label(
            window,
            text=comic_data["title_pt"],
            font=("Arial", 22, "bold"),
            fg=WHITE,
            bg=BACKGROUND
        ).pack(pady=15)

        details = (
            f"Titulo original: {comic_data['title_eng']}\n"
            f"Autor: {comic_data['author']}\n"
            f"Artista: {comic_data['artist']}\n"
            f"Data: {comic_data['data']}\n"
            f"Qualidade: {comic_data['quality']}\n"
            f"Preco: R$ {comic_data['price']:.2f}"
        )

        tk.Label(
            window,
            text=details,
            font=("Arial", 11),
            fg=WHITE,
            bg=BACKGROUND,
            justify="left"
        ).pack(pady=10)

        image_frame = tk.Frame(
            window,
            bg=BACKGROUND
        )

        image_frame.pack(pady=15)

        # Percorre a capa e a contracapa
        for image_path, image_name in [
            (comic_data.get("cover", ""), "Capa"),
            (comic_data.get("back_cover", ""), "Contracapa")
        ]:

            if image_path and os.path.exists(image_path):

                try:

                    # Carrega a imagem utilizando o proprio Tkinter
                    img = tk.PhotoImage(file=image_path)

                    # Reduz a imagem para caber na janela
                    img = img.subsample(
                        max(1, (img.width() + 219) // 220),
                        max(1, (img.height() + 299) // 300)
                    )

                    image_container = tk.Frame(
                        image_frame,
                        bg=BACKGROUND
                    )

                    image_container.pack(
                        side="left",
                        padx=12
                    )

                    image_label = tk.Label(
                        image_container,
                        image=img,
                        bg=BACKGROUND
                    )

                    # Mantem uma referencia para a imagem nao desaparecer
                    image_label.image = img

                    image_label.pack()

                    tk.Label(
                        image_container,
                        text=image_name,
                        fg=YELLOW,
                        bg=BACKGROUND
                    ).pack(pady=5)

                except tk.TclError:

                    tk.Label(
                        image_frame,
                        text=f"Nao foi possivel carregar {image_name}.",
                        fg=RED,
                        bg=BACKGROUND
                    ).pack()

        self.createWindowButton(
            window,
            "ADICIONAR AO CARRINHO",
            lambda: self.addComicToCart(comic_data)
        ).pack(pady=15)

    # Cria botoes personalizados em janelas secundarias
    def createWindowButton(self, parent, text, command):

        return tk.Button(
            parent,
            text=text,
            command=command,
            font=("Arial", 10, "bold"),
            bg=BLUE,
            fg=WHITE,
            activebackground=LIGHT_BLUE,
            relief="flat",
            cursor="hand2",
            padx=15,
            pady=8
        )

    # Adiciona um quadrinho ao carrinho
    def addToCart(self):

        selected = self.getSelectedSearchComic()

        if selected:
            self.addComicToCart(selected)

    # Registra o quadrinho no carrinho
    def addComicToCart(self, comic_data):

        comic_id = str(comic_data["id"])

        if comic_id in self.cart:
            self.cart[comic_id] += 1

        else:
            self.cart[comic_id] = 1

        messagebox.showinfo(
            "Carrinho",
            f"{comic_data['title_pt']} foi adicionado ao carrinho!"
        )

    # Mostra os itens do carrinho
    def showCart(self):

        self.clearScreen()

        self.createHeader(
            "MEU CARRINHO",
            "Confira os quadrinhos que voce selecionou."
        )

        content = self.createContent()

        self.cart_list = tk.Listbox(
            content,
            width=85,
            height=15,
            bg=SECONDARY,
            fg=WHITE,
            selectbackground=BLUE,
            font=("Arial", 10),
            relief="flat"
        )

        self.cart_list.pack(pady=15)

        comics = self.db.load()

        total = 0

        self.cart_ids = []

        for comic_id, quantity in self.cart.items():

            for comic_data in comics:

                if str(comic_data["id"]) == comic_id:

                    subtotal = comic_data["price"] * quantity

                    total += subtotal

                    self.cart_ids.append(comic_id)

                    self.cart_list.insert(
                        tk.END,
                        f"{comic_data['title_pt']} | "
                        f"Quantidade: {quantity} | "
                        f"Subtotal: R$ {subtotal:.2f}"
                    )

                    break

        self.createLabel(
            content,
            f"TOTAL: R$ {total:.2f}",
            17,
            True,
            YELLOW
        ).pack(pady=10)

        self.createButton(
            content,
            "REMOVER ITEM",
            self.removeFromCart,
            RED
        ).pack(pady=5)

        self.createButton(
            content,
            "VOLTAR",
            self.userMenu,
            SECONDARY
        ).pack(pady=10)

    # Remove um item do carrinho
    def removeFromCart(self):

        selection = self.cart_list.curselection()

        if not selection:

            messagebox.showwarning(
                "Atencao",
                "Selecione um item!"
            )

            return

        index = selection[0]

        comic_id = self.cart_ids[index]

        if self.cart[comic_id] > 1:
            self.cart[comic_id] -= 1

        else:
            del self.cart[comic_id]

        self.showCart()

    # Menu administrativo
    def adminMenu(self):

        self.clearScreen()

        self.createHeader(
            "PAINEL ADMINISTRATIVO",
            f"Bem-vindo, {self.current_user['name']}!"
        )

        content = self.createContent()

        self.createButton(
            content,
            "CADASTRAR QUADRINHOS",
            self.comicForm
        ).pack(pady=12)

        self.createButton(
            content,
            "GERENCIAR CATALOGO",
            self.manageCatalog,
            YELLOW
        ).pack(pady=12)

        self.createButton(
            content,
            "SAIR DA CONTA",
            self.logout,
            SECONDARY
        ).pack(pady=12)

    # Abre a janela para selecionar uma imagem
    def selectImage(self, image_type):

        path = filedialog.askopenfilename(
            title="Selecionar imagem",
            filetypes=[
                ("Imagens PNG e GIF", "*.png *.gif"),
                ("Imagens PNG", "*.png"),
                ("Imagens GIF", "*.gif")
            ]
        )

        if not path:
            return

        # Guarda o caminho da capa
        if image_type == "cover":

            self.selected_cover = path

            self.cover_label.config(
                text=os.path.basename(path)
            )

        # Guarda o caminho da contracapa
        else:

            self.selected_back_cover = path

            self.back_cover_label.config(
                text=os.path.basename(path)
            )

    # Copia a imagem selecionada para a pasta do projeto
    def saveImage(self, source_path):

        if not source_path:
            return ""

        extension = os.path.splitext(source_path)[1].lower()

        if extension not in [".png", ".gif"]:
            raise ValueError("Selecione uma imagem PNG ou GIF.")

        filename = str(uuid.uuid4()) + extension

        destination = os.path.join(
            self.db.images_folder,
            filename
        )

        shutil.copy2(source_path, destination)

        return destination

    # Formulario de cadastro e edicao de quadrinhos
    def comicForm(self, comic_data=None):

        self.clearScreen()

        self.editing_comic_id = None

        self.selected_cover = ""
        self.selected_back_cover = ""

        if comic_data:

            self.editing_comic_id = comic_data["id"]

            self.selected_cover = comic_data.get("cover", "")
            self.selected_back_cover = comic_data.get("back_cover", "")

        self.createHeader(
            "CADASTRAR QUADRINHO" if not comic_data else "EDITAR QUADRINHO",
            "Preencha as informacoes da publicacao."
        )

        content = self.createContent()

        self.form_entries = {}

        fields = [
            ("Titulo original", "title_eng"),
            ("Titulo em portugues", "title_pt"),
            ("Autor", "author"),
            ("Artista", "artist"),
            ("Data de publicacao", "data"),
            ("Qualidade", "quality"),
            ("Preco", "price")
        ]

        # Cria os campos do formulario
        for field_name, field_key in fields:

            self.createLabel(content, field_name).pack()

            entry = tk.Entry(
                content,
                width=40,
                font=("Arial", 10)
            )

            entry.pack(pady=3)

            if comic_data:
                entry.insert(0, str(comic_data[field_key]))

            self.form_entries[field_key] = entry

        # Botao para selecionar a capa
        self.createButton(
            content,
            "SELECIONAR CAPA",
            lambda: self.selectImage("cover")
        ).pack(pady=5)

        self.cover_label = tk.Label(
            content,
            text=os.path.basename(self.selected_cover) if self.selected_cover else "Nenhuma capa selecionada",
            fg=GRAY,
            bg=BACKGROUND
        )

        self.cover_label.pack()

        # Botao para selecionar a contracapa
        self.createButton(
            content,
            "SELECIONAR CONTRACAPA",
            lambda: self.selectImage("back_cover")
        ).pack(pady=5)

        self.back_cover_label = tk.Label(
            content,
            text=os.path.basename(self.selected_back_cover) if self.selected_back_cover else "Nenhuma contracapa selecionada",
            fg=GRAY,
            bg=BACKGROUND
        )

        self.back_cover_label.pack()

        self.createButton(
            content,
            "SALVAR QUADRINHO",
            self.saveComic,
            YELLOW
        ).pack(pady=12)

        self.createButton(
            content,
            "VOLTAR",
            self.adminMenu,
            SECONDARY
        ).pack()

    # Salva um novo quadrinho ou atualiza um existente
    def saveComic(self):

        data = {}

        for field_key, entry in self.form_entries.items():

            data[field_key] = entry.get().strip()

        # Verifica se todos os campos foram preenchidos
        for field in [
            "title_eng",
            "title_pt",
            "author",
            "artist",
            "data",
            "quality",
            "price"
        ]:

            if not data[field]:

                messagebox.showwarning(
                    "Atencao",
                    "Preencha todos os campos!"
                )

                return

        # Verifica se o preco e valido
        try:

            data["price"] = float(
                data["price"].replace(",", ".")
            )

            if data["price"] < 0:
                raise ValueError

        except ValueError:

            messagebox.showerror(
                "Erro",
                "Digite um preco valido!"
            )

            return

        try:

            # Define o ID e as imagens de um novo quadrinho
            if self.editing_comic_id is None:

                comic_id = self.db.nextComicID()

                cover = self.saveImage(self.selected_cover)

                back_cover = self.saveImage(self.selected_back_cover)

            # Recupera os dados antigos durante uma edicao
            else:

                comic_id = self.editing_comic_id

                old_comic = next(
                    (
                        item for item in self.db.load()
                        if item["id"] == comic_id
                    ),
                    None
                )

                if old_comic is None:

                    messagebox.showerror(
                        "Erro",
                        "Quadrinho nao encontrado!"
                    )

                    return

                cover = old_comic.get("cover", "")
                back_cover = old_comic.get("back_cover", "")

                # Atualiza somente as imagens que foram substituidas
                if self.selected_cover and self.selected_cover != cover:
                    cover = self.saveImage(self.selected_cover)

                if self.selected_back_cover and self.selected_back_cover != back_cover:
                    back_cover = self.saveImage(self.selected_back_cover)

            # Organiza as informacoes do quadrinho
            comic_data = {
                "id": comic_id,
                "title_eng": data["title_eng"],
                "title_pt": data["title_pt"],
                "author": data["author"],
                "artist": data["artist"],
                "data": data["data"],
                "quality": data["quality"],
                "price": data["price"],
                "cover": cover,
                "back_cover": back_cover
            }

            # Salva ou atualiza o quadrinho no banco
            if self.editing_comic_id is None:

                self.db.addComic(comic_data)

                messagebox.showinfo(
                    "Sucesso",
                    "Quadrinho cadastrado com sucesso!"
                )

            else:

                self.db.updateComic(
                    self.editing_comic_id,
                    comic_data
                )

                messagebox.showinfo(
                    "Sucesso",
                    "Quadrinho atualizado com sucesso!"
                )

            self.adminMenu()

        except (OSError, ValueError, tk.TclError) as error:

            messagebox.showerror(
                "Erro",
                f"Nao foi possivel salvar o quadrinho:\n{error}"
            )

    # Exibe todos os quadrinhos cadastrados
    def manageCatalog(self):

        self.clearScreen()

        self.createHeader(
            "GERENCIAR CATALOGO",
            "Edite ou remova publicacoes."
        )

        content = self.createContent()

        self.catalog_list = tk.Listbox(
            content,
            width=85,
            height=16,
            bg=SECONDARY,
            fg=WHITE,
            selectbackground=BLUE,
            font=("Arial", 10),
            relief="flat"
        )

        self.catalog_list.pack(pady=15)

        self.catalog_comics = self.db.load()

        for comic_data in self.catalog_comics:

            self.catalog_list.insert(
                tk.END,
                f"{comic_data['id']} | "
                f"{comic_data['title_pt']} | "
                f"{comic_data['author']} | "
                f"R$ {comic_data['price']:.2f}"
            )

        self.createButton(
            content,
            "EDITAR QUADRINHO",
            self.editSelectedComic
        ).pack(pady=5)

        self.createButton(
            content,
            "EXCLUIR QUADRINHO",
            self.deleteSelectedComic,
            RED
        ).pack(pady=5)

        self.createButton(
            content,
            "VOLTAR",
            self.adminMenu,
            SECONDARY
        ).pack(pady=10)

    # Abre o formulario de edicao do quadrinho selecionado
    def editSelectedComic(self):

        selection = self.catalog_list.curselection()

        if not selection:

            messagebox.showwarning(
                "Atencao",
                "Selecione um quadrinho!"
            )

            return

        index = selection[0]

        selected_comic = self.catalog_comics[index]

        self.comicForm(selected_comic)

    # Exclui o quadrinho selecionado
    def deleteSelectedComic(self):

        selection = self.catalog_list.curselection()

        if not selection:

            messagebox.showwarning(
                "Atencao",
                "Selecione um quadrinho!"
            )

            return

        index = selection[0]

        selected_comic = self.catalog_comics[index]

        confirmation = messagebox.askyesno(
            "Confirmar exclusao",
            f"Deseja excluir {selected_comic['title_pt']}?"
        )

        if confirmation:

            self.db.deleteComic(selected_comic["id"])

            messagebox.showinfo(
                "Sucesso",
                "Quadrinho excluido!"
            )

            self.manageCatalog()

    # Encerra a sessao e retorna ao menu inicial
    def logout(self):

        self.current_user = None

        self.cart = {}

        self.mainMenu()

    # Inicia a janela principal
    def run(self):

        self.root.mainloop()


# EXECUTAR A APLICACAO

if __name__ == "__main__":

    app = comicApp()

    app.welcome()

    app.run()

# AMALGAMA COMIX - Qualidade e excelencia em quadrinhos raros
# Rodrigo F Q. Souza / Yasmim A. R. Siqueira / Lucas Vieira
# Importação de todas as bibliotecas necessarias
import hashlib
import json
import os
import secrets
import shutil
import tkinter as tk
import unicodedata
import uuid
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

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

        # Cria as pastas do sistema caso ainda nao existam
        os.makedirs(self.data_folder, exist_ok=True)
        os.makedirs(self.images_folder, exist_ok=True)

        # Carrega a lista inicial de quadrinhos
        initial_comics = self.initialComics()

        # Cria o arquivo ou adiciona os quadrinhos iniciais que ainda nao existem
        if not os.path.exists(self.file_path):
            self.save(initial_comics)
        else:
            current_comics = self.load()
            initial_by_id = {
                comic_data["id"]: comic_data
                for comic_data in initial_comics
            }
            existing_ids = {comic.get("id") for comic in current_comics}

            # Preenche os caminhos das imagens dos quadrinhos iniciais antigos
            for comic_data in current_comics:
                initial_data = initial_by_id.get(comic_data.get("id"))

                # So associa a imagem se o registro ainda for o quadrinho inicial
                if initial_data and comic_data.get("title_eng") == initial_data["title_eng"]:
                    if not comic_data.get("cover"):
                        comic_data["cover"] = initial_data["cover"]
                    if not comic_data.get("back_cover"):
                        comic_data["back_cover"] = initial_data["back_cover"]

            # Mantem os dados existentes e acrescenta somente os IDs que faltam
            for comic_data in initial_comics:
                if comic_data["id"] not in existing_ids:
                    current_comics.append(comic_data)

            self.save(current_comics)

        # Cria o arquivo de usuarios caso ainda nao exista
        if not os.path.exists(self.users_path):
            with open(self.users_path, "w", encoding="utf-8") as file:
                json.dump([], file, indent=4)

        # Cria a conta administrativa
        self.createAdmin()

    # Retorna a lista inicial de quadrinhos do catalogo

    def initialComics(self):
        # Os nomes das imagens ficam definidos, mas voce adiciona os arquivos depois
        initial_comics = []

        # Dados dos quadrinhos: titulo, autor, artista, editora, saga, data e precos
        comic_records = [
            ("Batman: Year One", "Batman: Ano Um", "Frank Miller", "David Mazzucchelli", "DC Comics", "Batman", "1987", 15, 75, "batman_ano_um"),
            ("Superman: Red Son", "Superman: Entre a Foice e o Martelo", "Mark Millar", "Dave Johnson", "DC Comics", "Superman", "2003", 20, 100, "superman_entre_a_foice_e_o_martelo"),
            ("Watchmen", "Watchmen", "Alan Moore", "Dave Gibbons", "DC Comics", "Watchmen", "1986", 25, 125, "watchmen"),
            ("The Sandman: Preludes & Nocturnes", "Sandman: Preludios e Noturnos", "Neil Gaiman", "Sam Kieth; Mike Dringenberg; Malcolm Jones III", "Vertigo", "Sandman", "1989", 22, 110, "sandman_preludios_e_noturnos"),
            ("The Dark Knight Returns", "O Cavaleiro das Trevas", "Frank Miller", "Frank Miller; Klaus Janson", "DC Comics", "Batman", "1986", 24, 120, "o_cavaleiro_das_trevas"),
            ("Batman: The Killing Joke", "Batman: A Piada Mortal", "Alan Moore", "Brian Bolland", "DC Comics", "Batman", "1988", 18, 90, "batman_a_piada_mortal"),
            ("Batman: Hush", "Batman: Silencio", "Jeph Loeb", "Jim Lee; Scott Williams", "DC Comics", "Batman", "2002", 23, 115, "batman_silencio"),
            ("Batman: The Long Halloween", "Batman: O Longo Dia das Bruxas", "Jeph Loeb", "Tim Sale", "DC Comics", "Batman", "1996", 25, 125, "batman_o_longo_dia_das_bruxas"),
            ("All-Star Superman", "Grandes Astros: Superman", "Grant Morrison", "Frank Quitely", "DC Comics", "Superman", "2005", 22, 110, "grandes_astros_superman"),
            ("Kingdom Come", "Reino do Amanhã", "Mark Waid", "Alex Ross", "DC Comics", "Universo DC", "1996", 24, 120, "reino_do_amanha"),
            ("V for Vendetta", "V de Vingança", "Alan Moore", "David Lloyd", "Vertigo", "V de Vingança", "1982", 23, 115, "v_de_vinganca"),
            ("The League of Extraordinary Gentlemen: Volume One", "A Liga Extraordinária: Volume Um", "Alan Moore", "Kevin O'Neill", "America's Best Comics", "Liga Extraordinaria", "1999", 20, 100, "liga_extraordinaria_volume_um"),
            ("Maus", "Maus", "Art Spiegelman", "Art Spiegelman", "Pantheon Books", "Maus", "1980", 22, 110, "maus"),
            ("Persepolis", "Persépolis", "Marjane Satrapi", "Marjane Satrapi", "L'Association", "Persepolis", "2000", 20, 100, "persepolis"),
            ("Bone: Out from Boneville", "Bone: A Jornada Começa", "Jeff Smith", "Jeff Smith", "Cartoon Books", "Bone", "1991", 18, 90, "bone_a_jornada_comeca"),
            ("Hellboy: Seed of Destruction", "Hellboy: Sementes da Destruição", "Mike Mignola; John Byrne", "Mike Mignola", "Dark Horse Comics", "Hellboy", "1994", 20, 100, "hellboy_sementes_da_destruicao"),
            ("Sin City: The Hard Goodbye", "Sin City: A Cidade do Pecado", "Frank Miller", "Frank Miller", "Dark Horse Comics", "Sin City", "1991", 21, 105, "sin_city_a_cidade_do_pecado"),
            ("300", "300", "Frank Miller", "Frank Miller; Lynn Varley", "Dark Horse Comics", "300", "1998", 19, 95, "300"),
            ("From Hell", "Do Inferno", "Alan Moore", "Eddie Campbell", "Top Shelf Productions", "Do Inferno", "1989", 27, 135, "do_inferno"),
            ("Pride of Baghdad", "Orgulho de Bagdá", "Brian K. Vaughan", "Niko Henrichon", "Vertigo", "Orgulho de Bagda", "2006", 18, 90, "orgulho_de_bagda"),
            ("Y: The Last Man, Vol. 1", "Y: O Último Homem, Volume 1", "Brian K. Vaughan", "Pia Guerra", "Vertigo", "Y: O Ultimo Homem", "2002", 20, 100, "y_o_ultimo_homem_volume_1"),
            ("Saga, Vol. 1", "Saga, Volume 1", "Brian K. Vaughan", "Fiona Staples", "Image Comics", "Saga", "2012", 20, 100, "saga_volume_1"),
            ("Paper Girls, Vol. 1", "Paper Girls, Volume 1", "Brian K. Vaughan", "Cliff Chiang", "Image Comics", "Paper Girls", "2015", 18, 90, "paper_girls_volume_1"),
            ("Monstress, Vol. 1", "Monstress, Volume 1", "Marjorie Liu", "Sana Takeda", "Image Comics", "Monstress", "2015", 21, 105, "monstress_volume_1"),
            ("The Walking Dead, Vol. 1", "The Walking Dead, Volume 1", "Robert Kirkman", "Tony Moore", "Image Comics", "The Walking Dead", "2003", 18, 90, "the_walking_dead_volume_1"),
            ("Invincible, Vol. 1", "Invencível, Volume 1", "Robert Kirkman", "Cory Walker; Ryan Ottley", "Image Comics", "Invencivel", "2003", 19, 95, "invencivel_volume_1"),
            ("Spawn: Origins, Vol. 1", "Spawn: Origens, Volume 1", "Todd McFarlane", "Todd McFarlane", "Image Comics", "Spawn", "1992", 18, 90, "spawn_origens_volume_1"),
            ("The Wicked + The Divine, Vol. 1", "The Wicked + The Divine, Volume 1", "Kieron Gillen", "Jamie McKelvie", "Image Comics", "The Wicked + The Divine", "2014", 19, 95, "the_wicked_the_divine_volume_1"),
            ("Black Science, Vol. 1", "Black Science, Volume 1", "Rick Remender", "Matteo Scalera", "Image Comics", "Black Science", "2013", 19, 95, "black_science_volume_1"),
            ("Descender, Vol. 1", "Descender, Volume 1", "Jeff Lemire", "Dustin Nguyen", "Image Comics", "Descender", "2015", 18, 90, "descender_volume_1"),
            ("Daredevil: Born Again", "Demolidor: A Queda de Murdock", "Frank Miller; David Mazzucchelli", "David Mazzucchelli", "Marvel Comics", "Demolidor", "1986", 22, 110, "demolidor_a_queda_de_murdock"),
            ("Daredevil: The Man Without Fear", "Demolidor: O Homem Sem Medo", "Frank Miller", "John Romita Jr.", "Marvel Comics", "Demolidor", "1993", 20, 100, "demolidor_o_homem_sem_medo"),
            ("Marvels", "Marvels", "Kurt Busiek", "Alex Ross", "Marvel Comics", "Universo Marvel", "1994", 23, 115, "marvels"),
            ("Spider-Man: Kraven's Last Hunt", "A Última Caçada de Kraven", "J. M. DeMatteis", "Mike Zeck", "Marvel Comics", "Homem-Aranha", "1987", 21, 105, "a_ultima_cacada_de_kraven"),
            ("Spider-Man: Blue", "Homem-Aranha: Azul", "Jeph Loeb", "Tim Sale", "Marvel Comics", "Homem-Aranha", "2002", 20, 100, "homem_aranha_azul"),
            ("Hawkeye: My Life as a Weapon", "Gavião Arqueiro: Minha Vida como uma Arma", "Matt Fraction", "David Aja", "Marvel Comics", "Gaviao Arqueiro", "2012", 20, 100, "gaviao_arqueiro_minha_vida_como_uma_arma"),
            ("Ms. Marvel: No Normal", "Ms. Marvel: Nada Normal", "G. Willow Wilson", "Adrian Alphona", "Marvel Comics", "Ms. Marvel", "2014", 18, 90, "ms_marvel_nada_normal"),
            ("Vision: Little Worse Than a Man", "Visão: Um Pouco Pior que um Homem", "Tom King", "Gabriel Hernandez Walta", "Marvel Comics", "Visao", "2015", 20, 100, "visao_um_pouco_pior_que_um_homem"),
            ("Moon Knight: From the Dead", "Cavaleiro da Lua: Das Cinzas", "Warren Ellis", "Declan Shalvey", "Marvel Comics", "Cavaleiro da Lua", "2014", 19, 95, "cavaleiro_da_lua_das_cinzas"),
            ("Planet Hulk", "Planeta Hulk", "Greg Pak", "Carlo Pagulayan", "Marvel Comics", "Hulk", "2006", 24, 120, "planeta_hulk"),
            ("Civil War", "Guerra Civil", "Mark Millar", "Steve McNiven", "Marvel Comics", "Universo Marvel", "2006", 25, 125, "guerra_civil"),
            ("House of X / Powers of X", "Dinastia X / Potências de X", "Jonathan Hickman", "Pepe Larraz; R. B. Silva", "Marvel Comics", "X-Men", "2019", 26, 130, "dinastia_x_potencias_de_x"),
            ("God Loves, Man Kills", "Deus Ama, o Homem Mata", "Chris Claremont", "Brent Anderson", "Marvel Comics", "X-Men", "1982", 18, 90, "deus_ama_o_homem_mata"),
            ("Old Man Logan", "Velho Logan", "Mark Millar", "Steve McNiven", "Marvel Comics", "Wolverine", "2008", 22, 110, "velho_logan"),
            ("The Infinity Gauntlet", "Desafio Infinito", "Jim Starlin", "George Pérez; Ron Lim", "Marvel Comics", "Universo Marvel", "1991", 24, 120, "desafio_infinito"),
            ("Annihilation", "Aniquilação", "Keith Giffen", "Andrea Di Vito", "Marvel Comics", "Aniquilacao", "2006", 24, 120, "aniquilacao"),
            ("Secret Wars", "Guerras Secretas", "Jonathan Hickman", "Esad Ribic", "Marvel Comics", "Universo Marvel", "2015", 25, 125, "guerras_secretas"),
            ("The Vision, Vol. 1", "A Visão, Volume 1", "Tom King", "Gabriel Hernandez Walta", "Marvel Comics", "Visao", "2015", 19, 95, "a_visao_volume_1"),
            ("Batman: Earth One", "Batman: Terra Um", "Geoff Johns", "Gary Frank", "DC Comics", "Batman: Terra Um", "2012", 20, 100, "batman_terra_um"),
            ("Superman: Birthright", "Superman: Legado das Estrelas", "Mark Waid", "Leinil Francis Yu", "DC Comics", "Superman", "2003", 21, 105, "superman_legado_das_estrelas"),
            ("Green Lantern: Rebirth", "Lanterna Verde: Renascimento", "Geoff Johns", "Ethan Van Sciver", "DC Comics", "Lanterna Verde", "2004", 20, 100, "lanterna_verde_renascimento"),
            ("Green Lantern: Sinestro Corps War", "Lanterna Verde: A Guerra dos Lanternas", "Geoff Johns; Dave Gibbons", "Ivan Reis; Patrick Gleason", "DC Comics", "Lanterna Verde", "2007", 24, 120, "a_guerra_dos_lanternas"),
            ("Wonder Woman: The Hiketeia", "Mulher-Maravilha: O Hiketeia", "Greg Rucka", "J. G. Jones", "DC Comics", "Mulher-Maravilha", "2002", 18, 90, "mulher_maravilha_o_hiketeia"),
            ("Wonder Woman: Year One", "Mulher-Maravilha: Ano Um", "Greg Rucka", "Nicola Scott", "DC Comics", "Mulher-Maravilha", "2016", 20, 100, "mulher_maravilha_ano_um"),
            ("Flashpoint", "Ponto de Ignição", "Geoff Johns", "Andy Kubert", "DC Comics", "Flash", "2011", 22, 110, "ponto_de_ignicao"),
            ("JLA: Tower of Babel", "Liga da Justiça: Torre de Babel", "Mark Waid", "Howard Porter", "DC Comics", "Liga da Justica", "2000", 19, 95, "liga_da_justica_torre_de_babel"),
            ("JLA: Earth 2", "Liga da Justiça: Terra 2", "Grant Morrison", "Frank Quitely", "DC Comics", "Liga da Justica", "2000", 18, 90, "liga_da_justica_terra_2"),
            ("Mister Miracle", "Senhor Milagre", "Tom King", "Mitch Gerads", "DC Comics", "Quarto Mundo", "2017", 22, 110, "senhor_milagre"),
            ("The New Frontier", "DC: A Nova Fronteira", "Darwyn Cooke", "Darwyn Cooke", "DC Comics", "Universo DC", "2004", 24, 120, "dc_a_nova_fronteira"),
            ("Gotham Central: In the Line of Duty", "Gotham City Contra o Crime", "Ed Brubaker; Greg Rucka", "Michael Lark", "DC Comics", "Gotham Central", "2002", 22, 110, "gotham_city_contra_o_crime"),
            ("The Omega Men", "Os Homens Ômega", "Tom King", "Barnaby Bagenda", "DC Comics", "Homens Omega", "2015", 20, 100, "os_homens_omega"),
            ("Animal Man: The Hunt", "Homem-Animal: A Caçada", "Grant Morrison", "Chas Truog", "DC Comics", "Homem-Animal", "1988", 18, 90, "homem_animal_a_cacada"),
            ("Swamp Thing: Saga of the Swamp Thing", "Monstro do Pântano: A Saga", "Alan Moore", "Steve Bissette; John Totleben", "DC Comics", "Monstro do Pantano", "1984", 24, 120, "monstro_do_pantano_a_saga"),
            ("Preacher: Gone to Texas", "Preacher: A Caminho do Texas", "Garth Ennis", "Steve Dillon", "Vertigo", "Preacher", "1995", 22, 110, "preacher_a_caminho_do_texas"),
            ("Fables: Legends in Exile", "Fábulas: Lendas no Exílio", "Bill Willingham", "Lan Medina", "Vertigo", "Fabulas", "2002", 20, 100, "fabulas_lendas_no_exilio"),
            ("100 Bullets: First Shot, Last Call", "100 Balas: Primeiro Tiro, Última Chamada", "Brian Azzarello", "Eduardo Risso", "Vertigo", "100 Balas", "1999", 20, 100, "100_balas_primeiro_tiro_ultima_chamada"),
            ("Transmetropolitan: Back on the Street", "Transmetropolitan: De Volta às Ruas", "Warren Ellis", "Darick Robertson", "Vertigo", "Transmetropolitan", "1997", 20, 100, "transmetropolitan_de_volta_as_ruas"),
            ("Lucifer: Devil in the Gateway", "Lúcifer: O Diabo à Porta", "Mike Carey", "Scott Hampton", "Vertigo", "Lucifer", "2000", 19, 95, "lucifer_o_diabo_a_porta"),
            ("The Books of Magic", "Os Livros da Magia", "Neil Gaiman", "John Bolton; Scott Hampton; Charles Vess; Paul Johnson", "Vertigo", "Livros da Magia", "1990", 20, 100, "os_livros_da_magia"),
            ("Locke & Key: Welcome to Lovecraft", "Locke & Key: Bem-vindo a Lovecraft", "Joe Hill", "Gabriel Rodriguez", "IDW Publishing", "Locke & Key", "2008", 21, 105, "locke_key_bem_vindo_a_lovecraft"),
            ("Nimona", "Nimona", "ND Stevenson", "ND Stevenson", "HarperCollins", "Nimona", "2015", 18, 90, "nimona"),
            ("The Arrival", "A Chegada", "Shaun Tan", "Shaun Tan", "Scholastic", "A Chegada", "2006", 19, 95, "a_chegada"),
            ("Blankets", "Retalhos", "Craig Thompson", "Craig Thompson", "Top Shelf Productions", "Retalhos", "2003", 23, 115, "retalhos"),
            ("Daytripper", "Daytripper", "Fábio Moon; Gabriel Bá", "Fábio Moon; Gabriel Bá", "Vertigo", "Daytripper", "2010", 22, 110, "daytripper"),
            ("Asterios Polyp", "Asterios Polyp", "David Mazzucchelli", "David Mazzucchelli", "Pantheon Books", "Asterios Polyp", "2009", 22, 110, "asterios_polyp"),
            ("Understanding Comics", "Desvendando os Quadrinhos", "Scott McCloud", "Scott McCloud", "HarperCollins", "Teoria dos Quadrinhos", "1993", 20, 100, "desvendando_os_quadrinhos"),
            ("Scott Pilgrim's Precious Little Life", "Scott Pilgrim Contra o Mundo", "Bryan Lee O'Malley", "Bryan Lee O'Malley", "Oni Press", "Scott Pilgrim", "2004", 18, 90, "scott_pilgrim_contra_o_mundo"),
            ("The Umbrella Academy: Apocalypse Suite", "The Umbrella Academy: Suíte do Apocalipse", "Gerard Way", "Gabriel Bá", "Dark Horse Comics", "The Umbrella Academy", "2007", 20, 100, "umbrella_academy_suite_do_apocalipse"),
            ("Black Hole", "Black Hole", "Charles Burns", "Charles Burns", "Pantheon Books", "Black Hole", "1995", 23, 115, "black_hole"),
            ("Ghost World", "Mundo Fantasma", "Daniel Clowes", "Daniel Clowes", "Fantagraphics", "Mundo Fantasma", "1993", 19, 95, "mundo_fantasma"),
        ]

        # Monta cada registro no mesmo formato usado pelo restante do sistema
        for comic_id, record in enumerate(comic_records, start=1):
            (title_eng, title_pt, author, artist, publisher, saga, data, price_usd, price_brl, image_name) = record
            initial_comics.append({
                "id": comic_id,
                "title_eng": title_eng,
                "title_pt": title_pt,
                "author": author,
                "artist": artist,
                "publisher": publisher,
                "saga": saga,
                "data": data,
                "quality": "VF",
                "price_usd": float(price_usd),
                "price_brl": float(price_brl),
                "price": float(price_brl),
                "cover": os.path.join(self.images_folder, image_name + ".png"),
                "back_cover": os.path.join(self.images_folder, image_name + "_contracapa.png")
            })

        return initial_comics

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
            "role": "user",
            "cart": {},
            "purchases": []
        }
        users.append(new_user)
        self.save_users(users)

    # Atualiza informacoes de um usuario existente

    def updateUser(self, username, updated_data):
        users = self.load_users()
        for index, user_data in enumerate(users):
            if user_data["username"].lower() == username.lower():
                users[index].update(updated_data)
                self.save_users(users)
                return True
        return False

    # Exclui uma conta comum sem permitir a exclusao do administrador

    def deleteUser(self, username):
        users = self.load_users()
        updated_users = [
            user_data for user_data in users
            if not (
                user_data["username"].lower() == username.lower()
                and user_data.get("role") == "user"
            )
        ]
        if len(updated_users) == len(users):
            return False
        self.save_users(updated_users)
        return True

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
        back_cover="",
        publisher="",
        saga="",
        price_usd=0.0,
        price_brl=None
    ):
        self.id = id
        self.title_eng = title_eng
        self.title_pt = title_pt
        self.author = author
        self.artist = artist
        self.data = data
        self.quality = quality
        self.price = price if price_brl is None else price_brl
        self.price_brl = self.price
        self.price_usd = price_usd
        self.publisher = publisher
        self.saga = saga
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

        # Ajusta o tamanho da janela de acordo com a resolucao da tela
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = int(screen_width * 0.9)
        window_height = int(screen_height * 0.9)
        self.root.geometry(f"{window_width}x{window_height}")
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

    def createHeader(self, title, subtitle="", back_command=None):
        header = tk.Frame(
            self.root,
            bg=BACKGROUND
        )
        header.pack(fill="x", padx=35, pady=20)

        # Cria a opcao de voltar no canto superior esquerdo
        if back_command:
            tk.Button(
                header,
                text="← VOLTAR",
                command=back_command,
                font=("Arial", 10, "bold"),
                bg=SECONDARY,
                fg=WHITE,
                activebackground=BLUE,
                activeforeground=WHITE,
                relief="flat",
                cursor="hand2",
                padx=12,
                pady=7
            ).pack(side="left", padx=(0, 25))
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
        self.createHeader("CRIAR CONTA", back_command=self.mainMenu)
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

        # Pega os dados digitados pelo usuario
        name = self.signup_entry1.get().strip()
        username = self.signup_entry2.get().strip()
        password = self.signup_entry3.get()
        confirm_password = self.signup_entry4.get()

        # Verifica se as informacoes do cadastro sao validas
        validation = self.credValidation(
            name,
            username,
            password,
            confirm_password
        )

        # Verifica se ocorreu algum erro na validacao
        if validation != 0:

            # Define as mensagens de erro
            errors = {
                1: "Digite seu nome!",
                2: "Digite um nome de usuario!",
                3: "A senha precisa ter pelo menos 6 caracteres, uma letra e um numero!",
                4: "As senhas nao correspondem!",
                5: "Nome de usuario indisponivel!"
            }

            # Exibe a mensagem correspondente
            self.error_label.config(text=errors[validation])
            return

        # Realiza o cadastro no banco de dados
        self.db.addUser(name, username, password)

        # Faz o login automaticamente
        self.current_user = self.db.checkLogin(username, password)

        # Abre o menu do usuario
        if self.current_user:
            self.cart = {}
            self.current_user.setdefault("purchases", [])
            self.persistCurrentUserData()
            self.userMenu()

    # Tela de login

    def logIn(self):
        self.clearScreen()
        self.createHeader("ENTRAR NA CONTA", back_command=self.mainMenu)
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
            self.cart = dict(logged_user.get("cart", {}))
            self.current_user.setdefault("purchases", [])
            if logged_user.get("role") == "admin":
                self.adminMenu()
            else:
                self.persistCurrentUserData()
                self.userMenu()
        else:
            self.login_error_label.config(
                text="Usuario ou senha incorretos!"
            )

    # Salva o carrinho e o historico do usuario conectado

    def persistCurrentUserData(self):
        if not self.current_user:
            return
        if self.current_user.get("role") != "user":
            return
        self.current_user["cart"] = dict(self.cart)
        self.current_user.setdefault("purchases", [])
        self.db.updateUser(
            self.current_user["username"],
            {
                "cart": self.current_user["cart"],
                "purchases": self.current_user["purchases"]
            }
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

    # Padroniza textos para pesquisar sem diferenciar maiusculas ou acentos

    def normalizeSearchText(self, text):
        normalized = unicodedata.normalize("NFKD", str(text))
        normalized = "".join(
            char for char in normalized
            if not unicodedata.combining(char)
        )
        return normalized.casefold().strip()

    # Recupera o preco em reais, inclusive de cadastros antigos

    def getComicPriceBRL(self, comic_data):
        return float(comic_data.get("price_brl", comic_data.get("price", 0)) or 0)

    # Recupera o preco em dolares

    def getComicPriceUSD(self, comic_data):
        return float(comic_data.get("price_usd", 0) or 0)

    # Tela de pesquisa

    def searchScreen(self):
        self.clearScreen()
        self.createHeader(
            "CATALOGO DE QUADRINHOS",
            "Pesquise por titulo, autor, artista, editora, data de publicacao ou saga.",
            self.userMenu
        )
        content = self.createContent()
        self.search_entry = tk.Entry(
            content,
            font=("Arial", 12),
            width=55
        )
        self.search_entry.pack(pady=10)
        self.search_entry.bind("<Return>", lambda event: self.searchComics())
        self.createButton(
            content,
            "PESQUISAR",
            self.searchComics
        ).pack(pady=5)
        self.results_list = tk.Listbox(
            content,
            width=110,
            height=13,
            bg=SECONDARY,
            fg=WHITE,
            selectbackground=BLUE,
            font=("Arial", 10),
            relief="flat"
        )
        self.results_list.pack(pady=15, fill="x", padx=35)
        self.search_results = []

        # Atualiza os resultados conforme o usuario digita
        self.search_entry.bind(
            "<KeyRelease>",
            lambda event: self.searchComics()
        )

        # Exibe todos os quadrinhos ao abrir o catalogo
        self.searchComics()

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

    # Pesquisa quadrinhos pelo titulo, autor ou artista

    def searchComics(self):
        query = self.normalizeSearchText(self.search_entry.get())
        search_terms = query.split()
        comics = self.db.load()
        self.results_list.delete(0, tk.END)
        self.search_results = []
        for comic_data in comics:

            # Reune os campos que podem ser utilizados na pesquisa
            searchable_fields = [
                comic_data.get("title_eng", ""),
                comic_data.get("title_pt", ""),
                comic_data.get("author", ""),
                comic_data.get("artist", ""),
                comic_data.get("publisher", ""),
                comic_data.get("saga", ""),
                comic_data.get("data", ""),
                comic_data.get("quality", "")
            ]
            searchable_text = self.normalizeSearchText(
                " ".join(str(value) for value in searchable_fields if value is not None)
            )

            # Cada palavra digitada deve aparecer em algum campo pesquisavel
            if not search_terms or all(term in searchable_text for term in search_terms):
                self.search_results.append(comic_data)
                self.results_list.insert(
                    tk.END,
                    f"{comic_data.get('title_pt', 'Sem titulo')} | "
                    f"{comic_data.get('publisher', 'Editora nao informada')} | "
                    f"{comic_data.get('author', 'Autor nao informado')} | "
                    f"{comic_data.get('data', 'Data n/i')}"
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
        tk.Button(
            window,
            text="← VOLTAR",
            command=window.destroy,
            font=("Arial", 10, "bold"),
            bg=SECONDARY,
            fg=WHITE,
            activebackground=BLUE,
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=7
        ).pack(anchor="w", padx=18, pady=(12, 0))
        tk.Label(
            window,
            text=comic_data["title_pt"],
            font=("Arial", 22, "bold"),
            fg=WHITE,
            bg=BACKGROUND
        ).pack(pady=15)
        details = (
            f"Titulo original: {comic_data.get('title_eng', 'Nao informado')}\n"
            f"Autor: {comic_data.get('author', 'Nao informado')}\n"
            f"Artista: {comic_data.get('artist', 'Nao informado')}\n"
            f"Editora: {comic_data.get('publisher', 'Nao informada')}\n"
            f"Saga: {comic_data.get('saga', 'Nao informada')}\n"
            f"Data de publicacao: {comic_data.get('data', 'Nao informada')}\n"
            f"Conservacao: {comic_data.get('quality', 'Nao informada')}\n"
            f"Preco: R$ {self.getComicPriceBRL(comic_data):.2f} | "
            f"US$ {self.getComicPriceUSD(comic_data):.2f}"
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
        self.persistCurrentUserData()
        messagebox.showinfo(
            "Carrinho",
            f"{comic_data['title_pt']} foi adicionado ao carrinho!"
        )

    # Mostra os itens do carrinho

    def showCart(self):
        self.clearScreen()
        self.createHeader(
            "MEU CARRINHO",
            "Confira os quadrinhos que voce selecionou.",
            self.userMenu
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
        total_brl = 0
        total_usd = 0
        self.cart_ids = []
        for comic_id, quantity in self.cart.items():
            for comic_data in comics:
                if str(comic_data["id"]) == comic_id:
                    subtotal_brl = self.getComicPriceBRL(comic_data) * quantity
                    subtotal_usd = self.getComicPriceUSD(comic_data) * quantity
                    total_brl += subtotal_brl
                    total_usd += subtotal_usd
                    self.cart_ids.append(comic_id)
                    self.cart_list.insert(
                        tk.END,
                        f"{comic_data['title_pt']} | "
                        f"Quantidade: {quantity} | "
                        f"R$ {subtotal_brl:.2f} | US$ {subtotal_usd:.2f}"
                    )
                    break
        self.createLabel(
            content,
            f"TOTAL: R$ {total_brl:.2f} | US$ {total_usd:.2f}",
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
            "REGISTRAR COMPRA",
            self.checkoutCart,
            YELLOW
        ).pack(pady=5)

    # Registra uma compra no historico da conta

    def checkoutCart(self):
        if not self.cart:
            messagebox.showwarning(
                "Carrinho vazio",
                "Adicione quadrinhos antes de registrar uma compra."
            )
            return
        confirmation = messagebox.askyesno(
            "Confirmar compra",
            "Deseja registrar este pedido como uma compra?\n\n"
            "Esta acao apenas registra o pedido no sistema; "
            "nao realiza pagamento real."
        )
        if not confirmation:
            return
        comics = self.db.load()
        purchase_items = []
        total_brl = 0.0
        total_usd = 0.0
        for comic_id, quantity in self.cart.items():
            comic_data = next(
                (item for item in comics if str(item["id"]) == str(comic_id)),
                None
            )
            if comic_data is None:
                continue
            price_brl = self.getComicPriceBRL(comic_data)
            price_usd = self.getComicPriceUSD(comic_data)
            purchase_items.append({
                "comic_id": comic_data["id"],
                "title": comic_data.get("title_pt", "Quadrinho sem titulo"),
                "quantity": quantity,
                "price_brl": price_brl,
                "price_usd": price_usd
            })
            total_brl += price_brl * quantity
            total_usd += price_usd * quantity
        if not purchase_items:
            messagebox.showwarning(
                "Carrinho indisponivel",
                "Os quadrinhos do carrinho nao estao mais no catalogo."
            )
            self.cart = {}
            self.persistCurrentUserData()
            self.showCart()
            return
        purchase = {
            "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "items": purchase_items,
            "total_brl": total_brl,
            "total_usd": total_usd
        }
        self.current_user.setdefault("purchases", []).append(purchase)
        self.cart = {}
        self.persistCurrentUserData()
        messagebox.showinfo(
            "Compra registrada",
            "Pedido registrado no historico da conta!\n\n"
            f"Total: R$ {total_brl:.2f} | US$ {total_usd:.2f}\n\n"
            "Nenhum pagamento foi processado."
        )
        self.showCart()

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
        self.persistCurrentUserData()
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
        ).pack(pady=8)
        self.createButton(
            content,
            "GERENCIAR CATALOGO",
            self.manageCatalog,
            YELLOW
        ).pack(pady=8)
        self.createButton(
            content,
            "GERENCIAR USUARIOS",
            self.manageUsers
        ).pack(pady=8)
        self.createButton(
            content,
            "SAIR DA CONTA",
            self.logout,
            SECONDARY
        ).pack(pady=8)

    # Exibe as contas comuns cadastradas no sistema

    def manageUsers(self):
        self.clearScreen()
        self.createHeader(
            "GERENCIAR USUARIOS",
            "Consulte contas, carrinhos e compras registradas.",
            self.adminMenu
        )
        content = self.createContent()
        self.managed_users = [
            user_data for user_data in self.db.load_users()
            if user_data.get("role") == "user"
        ]
        self.users_list = tk.Listbox(
            content,
            width=85,
            height=15,
            bg=SECONDARY,
            fg=WHITE,
            selectbackground=BLUE,
            font=("Arial", 10),
            relief="flat"
        )
        self.users_list.pack(pady=15)
        for user_data in self.managed_users:
            self.users_list.insert(
                tk.END,
                f"{user_data.get('name', 'Sem nome')} "
                f"(@{user_data.get('username', 'sem usuario')})"
            )
        if not self.managed_users:
            self.users_list.insert(tk.END, "Nenhum usuario cadastrado.")
        self.createButton(
            content,
            "VER DETALHES DA CONTA",
            self.showManagedUserDetails
        ).pack(pady=5)
        self.createButton(
            content,
            "EXCLUIR CONTA",
            self.deleteManagedUser,
            RED
        ).pack(pady=5)

    # Retorna a conta selecionada na lista administrativa

    def getSelectedManagedUser(self):
        selection = self.users_list.curselection()
        if not selection:
            messagebox.showwarning(
                "Atencao",
                "Selecione um usuario primeiro!"
            )
            return None
        index = selection[0]
        if index >= len(self.managed_users):
            return None
        username = self.managed_users[index]["username"]
        return next(
            (
                user_data for user_data in self.db.load_users()
                if user_data.get("username", "").lower() == username.lower()
                and user_data.get("role") == "user"
            ),
            None
        )

    # Exibe o carrinho e o historico de compras de uma conta

    def showManagedUserDetails(self):
        selected_user = self.getSelectedManagedUser()
        if not selected_user:
            return
        self.clearScreen()
        self.createHeader(
            "DETALHES DO USUARIO",
            f"{selected_user.get('name', 'Sem nome')} "
            f"(@{selected_user.get('username', '')})",
            self.manageUsers
        )
        content = self.createContent()
        comics = self.db.load()
        comics_by_id = {str(item["id"]): item for item in comics}
        self.createLabel(
            content,
            "QUADRINHOS NO CARRINHO",
            13,
            True,
            YELLOW
        ).pack(anchor="w", padx=35, pady=(5, 3))
        cart_list = tk.Listbox(
            content,
            width=100,
            height=6,
            bg=SECONDARY,
            fg=WHITE,
            selectbackground=BLUE,
            font=("Arial", 9),
            relief="flat"
        )
        cart_list.pack(fill="x", padx=35, pady=(0, 12))
        user_cart = selected_user.get("cart", {}) or {}
        cart_count = 0
        for comic_id, quantity in user_cart.items():
            comic_data = comics_by_id.get(str(comic_id))
            title = (
                comic_data.get("title_pt", "Sem titulo")
                if comic_data else f"Quadrinho removido do catalogo (ID {comic_id})"
            )
            cart_list.insert(tk.END, f"{title} | Quantidade: {quantity}")
            cart_count += 1
        if cart_count == 0:
            cart_list.insert(tk.END, "Nenhum quadrinho no carrinho.")
        self.createLabel(
            content,
            "COMPRAS REGISTRADAS",
            13,
            True,
            YELLOW
        ).pack(anchor="w", padx=35, pady=(5, 3))
        purchases_list = tk.Listbox(
            content,
            width=100,
            height=8,
            bg=SECONDARY,
            fg=WHITE,
            selectbackground=BLUE,
            font=("Arial", 9),
            relief="flat"
        )
        purchases_list.pack(fill="x", padx=35, pady=(0, 10))
        purchases = selected_user.get("purchases", []) or []
        purchase_count = 0
        for purchase in purchases:
            purchase_date = purchase.get("date", "Data nao informada")
            for item in purchase.get("items", []):
                purchases_list.insert(
                    tk.END,
                    f"{purchase_date} | {item.get('title', 'Sem titulo')} | "
                    f"Quantidade: {item.get('quantity', 1)}"
                )
                purchase_count += 1
        if purchase_count == 0:
            purchases_list.insert(tk.END, "Nenhuma compra registrada.")

    # Exclui a conta selecionada pelo administrador

    def deleteManagedUser(self):
        selected_user = self.getSelectedManagedUser()
        if not selected_user:
            return
        confirmation = messagebox.askyesno(
            "Confirmar exclusao",
            "Deseja realmente excluir a conta de "
            f"{selected_user.get('name', selected_user['username'])}?\n\n"
            "O carrinho e o historico de compras dessa conta tambem serao excluidos."
        )
        if not confirmation:
            return
        if self.db.deleteUser(selected_user["username"]):
            messagebox.showinfo(
                "Sucesso",
                "Conta excluida com sucesso!"
            )
            self.manageUsers()
        else:
            messagebox.showerror(
                "Erro",
                "Nao foi possivel excluir essa conta."
            )

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
            "Preencha as informacoes da publicacao.",
            self.adminMenu
        )
        content = self.createContent()
        self.form_entries = {}

        # Organiza os campos em duas colunas para aproveitar melhor a tela
        fields_frame = tk.Frame(content, bg=BACKGROUND)
        fields_frame.pack(fill="x", padx=45, pady=5)
        fields_frame.grid_columnconfigure(0, weight=1)
        fields_frame.grid_columnconfigure(1, weight=1)
        fields = [
            ("Titulo original (ingles)", "title_eng"),
            ("Titulo em portugues", "title_pt"),
            ("Autor", "author"),
            ("Artista", "artist"),
            ("Editora", "publisher"),
            ("Saga", "saga"),
            ("Data de publicacao", "data"),
            ("Preco em dolar (USD)", "price_usd"),
            ("Preco em real (BRL)", "price_brl")
        ]

        # Cria os campos do formulario
        for index, (field_name, field_key) in enumerate(fields):
            row = index // 2
            column = index % 2
            field_frame = tk.Frame(fields_frame, bg=BACKGROUND)
            field_frame.grid(
                row=row,
                column=column,
                sticky="ew",
                padx=12,
                pady=4
            )
            self.createLabel(
                field_frame,
                field_name,
                10,
                True,
                GRAY
            ).pack(anchor="w")
            entry = tk.Entry(
                field_frame,
                font=("Arial", 10)
            )
            entry.pack(fill="x", pady=(3, 0), ipady=4)
            if comic_data:
                if field_key == "price_brl":
                    value = self.getComicPriceBRL(comic_data)
                elif field_key == "price_usd":
                    value = self.getComicPriceUSD(comic_data)
                else:
                    value = comic_data.get(field_key, "")
                entry.insert(0, str(value))
            self.form_entries[field_key] = entry

        # Cria a lista de classificacoes internacionais de conservacao
        quality_frame = tk.Frame(fields_frame, bg=BACKGROUND)
        quality_frame.grid(
            row=5,
            column=0,
            sticky="ew",
            padx=12,
            pady=4
        )
        self.createLabel(
            quality_frame,
            "Conservacao (padrao internacional)",
            10,
            True,
            GRAY
        ).pack(anchor="w")
        quality_options = [
            "NM", "NM-", "VF+", "VF", "VF-",
            "FN+", "FN", "FN-", "VG+", "VG", "VG-",
            "GD+", "GD", "GD-", "FR", "PR"
        ]
        quality_entry = ttk.Combobox(
            quality_frame,
            values=quality_options,
            state="readonly",
            font=("Arial", 10)
        )
        quality_entry.pack(fill="x", pady=(3, 0), ipady=2)
        quality_entry.set(
            comic_data.get("quality", "VF") if comic_data else "VF"
        )
        self.form_entries["quality"] = quality_entry
        self.createLabel(
            quality_frame,
            "NM: Near Mint | VF: Very Fine | FN: Fine | VG: Very Good | GD: Good | FR: Fair | PR: Poor",
            8,
            False,
            GRAY
        ).pack(anchor="w", pady=(3, 0))

        # Cria a area para selecionar as imagens
        images_frame = tk.Frame(content, bg=BACKGROUND)
        images_frame.pack(pady=8)
        cover_frame = tk.Frame(images_frame, bg=BACKGROUND)
        cover_frame.pack(side="left", padx=18)
        back_cover_frame = tk.Frame(images_frame, bg=BACKGROUND)
        back_cover_frame.pack(side="left", padx=18)

        # Botao para selecionar a capa
        self.createButton(
            cover_frame,
            "SELECIONAR CAPA",
            lambda: self.selectImage("cover")
        ).pack(pady=3)
        self.cover_label = tk.Label(
            cover_frame,
            text=os.path.basename(self.selected_cover) if self.selected_cover else "Nenhuma capa selecionada",
            fg=GRAY,
            bg=BACKGROUND
        )
        self.cover_label.pack()

        # Botao para selecionar a contracapa
        self.createButton(
            back_cover_frame,
            "SELECIONAR CONTRACAPA",
            lambda: self.selectImage("back_cover")
        ).pack(pady=3)
        self.back_cover_label = tk.Label(
            back_cover_frame,
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
        ).pack(pady=8)

    # Salva um novo quadrinho ou atualiza um existente

    def saveComic(self):
        data = {}
        for field_key, entry in self.form_entries.items():
            data[field_key] = entry.get().strip()

        # Verifica se todos os campos foram preenchidos
        required_fields = [
            "title_eng", "title_pt", "author", "artist",
            "publisher", "saga", "data",
            "quality", "price_usd", "price_brl"
        ]
        for field in required_fields:
            if not data.get(field):
                messagebox.showwarning(
                    "Atencao",
                    "Preencha todos os campos!"
                )
                return

        # Verifica se o preco e valido
        # Verifica se os dois precos sao validos
        try:
            data["price_usd"] = float(data["price_usd"].replace(",", "."))
            data["price_brl"] = float(data["price_brl"].replace(",", "."))
            if data["price_usd"] < 0 or data["price_brl"] < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Erro",
                "Digite valores validos e nao negativos para os precos!"
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
                "publisher": data["publisher"],
                "saga": data["saga"],
                "data": data["data"],
                "quality": data["quality"],
                "price_usd": data["price_usd"],
                "price_brl": data["price_brl"],
                "price": data["price_brl"],
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
            "Edite ou remova publicacoes.",
            self.adminMenu
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
                f"{comic_data.get('publisher', 'Editora n/i')} | "
                f"{comic_data.get('data', 'Data n/i')} | "
                f"R$ {self.getComicPriceBRL(comic_data):.2f} | "
                f"US$ {self.getComicPriceUSD(comic_data):.2f}"
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
        self.persistCurrentUserData()
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

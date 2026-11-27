# Arquivo das funções de Admin
import math
from getpass import getpass

from backend import AdminManager, DataBase
from modules import Admin, Comic, ComicVariation


class AdminConsole:
    def __init__(self, database: DataBase):
        self._database = database
        self._manager: AdminManager | None = None

    def run(self) -> None:
        try:
            self._create_first_admin_if_needed()
        except (OSError, ValueError) as error:
            print(f"Não foi possível configurar o administrador: {error}")
            return

        if not self._login():
            return

        actions = {
            "1": self._list_comics,
            "2": self._search_comics,
            "3": self._add_comic,
            "4": self._edit_comic,
            "5": self._delete_comic,
            "6": self._adjust_stock,
            "7": self._list_users,
            "8": self._delete_user,
            "9": self._change_password,
        }

        while True:
            self._show_menu()
            choice = input("Escolha uma opção: ").strip()
            if choice == "0":
                return

            action = actions.get(choice)
            if action is None:
                print("Escolha uma das opções exibidas.")
                continue

            try:
                action()
            except (OSError, TypeError, ValueError) as error:
                print(f"A ação falhou: {error}")

    def _create_first_admin_if_needed(self) -> None:
        if self._database.load_admins():
            return

        print("Nenhum administrador cadastrado. Crie a primeira conta admin.")
        name = self._prompt_text("Nome do administrador")
        username = self._prompt_text("Nome de usuário do administrador")
        existing_usernames = {
            user.username.casefold()
            for user in self._database.load_users()
        }
        if username.casefold() in existing_usernames:
            raise ValueError("Esse nome de usuário já está sendo usado.")

        password = getpass("Senha do administrador: ")
        confirmation = getpass("Confirme a senha: ")
        if password != confirmation:
            raise ValueError("As senhas não são iguais.")

        admin = Admin.register(name, username, password)
        admin.permissions = ["manage_comics", "manage_users"]
        self._database.save_admins([admin])
        print("Conta de administrador criada.")

    def _login(self) -> bool:
        for _ in range(3):
            print("Entre com a conta de administrador.")
            username = input("Nome de usuário do administrador: ").strip()
            password = getpass("Senha do administrador: ")
            try:
                self._manager = AdminManager.authenticate(
                    self._database,
                    username,
                    password,
                )
                print("Login realizado com sucesso.")
                return True
            except PermissionError:
                print("Nome de usuário ou senha incorretos.")

        print("Número máximo de tentativas excedido.")
        return False

    @staticmethod
    def _show_menu() -> None:
        print(
            "\n1. Listar quadrinhos\n"
            "2. Pesquisar quadrinhos\n"
            "3. Adicionar quadrinho\n"
            "4. Editar quadrinho\n"
            "5. Remover quadrinho\n"
            "6. Ajustar estoque\n"
            "7. Listar usuários\n"
            "8. Remover usuário\n"
            "9. Alterar senha do administrador\n"
            "0. Sair"
        )

    def _list_comics(self) -> None:
        comics = self._admin_manager.list_comics()
        if not comics:
            print("Não há quadrinhos no catálogo.")
            return

        for index, comic in enumerate(comics, start=1):
            print(f"\n{index}.")
            self._display_comic(comic)

    def _search_comics(self) -> None:
        query = input("Título para pesquisar: ")
        comics = self._admin_manager.find_comics(query)
        if not comics:
            print("Nenhum quadrinho corresponde à pesquisa.")
            return

        for comic in comics:
            print()
            self._display_comic(comic)

    def _add_comic(self) -> None:
        comic = self._prompt_comic()
        self._admin_manager.add_comic(comic)
        print("Quadrinho adicionado.")

    def _edit_comic(self) -> None:
        current = self._select_comic()
        replacement = self._prompt_comic(current)
        self._admin_manager.edit_comic(current, replacement)
        print("Quadrinho atualizado.")

    def _delete_comic(self) -> None:
        comic = self._select_comic()
        confirmation = input(
            f"Remover {comic.title_eng!r}? Digite 'sim' para confirmar: "
        ).strip().casefold()
        if confirmation in {"sim", "s"}:
            self._admin_manager.delete_comic(comic)
            print("Quadrinho removido.")
        else:
            print("Remoção cancelada.")

    def _adjust_stock(self) -> None:
        comic = self._select_comic()
        if not comic.variations:
            print("Este quadrinho não possui edições.")
            return

        for index, variation in enumerate(comic.variations, start=1):
            print(f"{index}. {variation.state}: estoque {variation.stock}")

        variation_index = self._prompt_integer(
            "Número da edição",
            minimum=1,
        ) - 1
        amount = self._prompt_signed_integer(
            "Alteração do estoque (positivo para adicionar, negativo para remover)"
        )
        self._admin_manager.adjust_stock(comic, variation_index, amount)
        print("Estoque atualizado.")

    def _list_users(self) -> None:
        users = self._admin_manager.list_users()
        if not users:
            print("Não há usuários cadastrados.")
            return

        for user in users:
            print(f"{user['name']} (@{user['username']})")

    def _delete_user(self) -> None:
        username = input("Nome de usuário para remover: ").strip()
        confirmation = input(
            f"Remover o usuário {username!r}? Digite 'sim' para confirmar: "
        ).strip().casefold()
        if confirmation in {"sim", "s"}:
            self._admin_manager.delete_user(username)
            print("Usuário removido.")
        else:
            print("Remoção cancelada.")

    def _change_password(self) -> None:
        current_password = getpass("Senha atual: ")
        new_password = getpass("Nova senha: ")
        confirmation = getpass("Confirme a nova senha: ")
        if new_password != confirmation:
            raise ValueError("As senhas não são iguais.")

        self._admin_manager.change_password(current_password, new_password)
        print("Senha alterada.")

    def _select_comic(self) -> Comic:
        comics = self._admin_manager.list_comics()
        if not comics:
            raise ValueError("O catálogo está vazio.")

        for index, comic in enumerate(comics, start=1):
            print(f"{index}. {comic.title_eng}")

        selection = self._prompt_integer("Número do quadrinho", minimum=1)
        if selection > len(comics):
            raise ValueError("Não existe quadrinho com esse número.")
        return comics[selection - 1]

    @staticmethod
    def _display_comic(comic: Comic) -> None:
        print(f"Título: {comic.title_eng}")
        if comic.title_pt is not None:
            print(f"Título em português: {comic.title_pt}")
        print(f"Série: {comic.saga_eng}")
        print(f"Editora: {comic.publisher} / {comic.imprint}")
        print(f"Data: {comic.date}")
        print(f"Gênero: {comic.genre}")
        print(f"Subgêneros: {', '.join(comic.sub_genre)}")
        print(
            f"Roteiro: {comic.writing}; desenho: {comic.penciling}; "
            f"arte-final: {comic.inking}; cores: {comic.colors}; "
            f"letras: {comic.letters}"
        )
        for variation in comic.variations:
            print(
                f"  {variation.state}: USD {variation.price_usd:.2f}, "
                f"BRL {variation.price_brl:.2f}, estoque {variation.stock}"
            )

    def _prompt_comic(self, current: Comic | None = None) -> Comic:
        title_eng = self._prompt_text(
            "Título em inglês",
            current.title_eng if current else None,
            has_current=current is not None,
        )
        title_pt = self._prompt_optional_text(
            "Título em português (use '-' para deixar vazio)",
            current.title_pt if current else None,
            has_current=current is not None,
        )
        saga_eng = self._prompt_text(
            "Série em inglês",
            current.saga_eng if current else None,
            has_current=current is not None,
        )
        saga_pt = self._prompt_optional_text(
            "Série em português (use '-' para deixar vazio)",
            current.saga_pt if current else None,
            has_current=current is not None,
        )
        publisher = self._prompt_text(
            "Editora",
            current.publisher if current else None,
            has_current=current is not None,
        )
        imprint = self._prompt_text(
            "Selo",
            current.imprint if current else None,
            has_current=current is not None,
        )
        date = self._prompt_text(
            "Data",
            current.date if current else None,
            has_current=current is not None,
        )
        genre = self._prompt_text(
            "Gênero",
            current.genre if current else None,
            has_current=current is not None,
        )
        sub_genre = self._prompt_subgenres(
            current.sub_genre if current else None
        )
        writing = self._prompt_text(
            "Roteirista",
            current.writing if current else None,
            has_current=current is not None,
        )
        penciling = self._prompt_text(
            "Desenhista",
            current.penciling if current else None,
            has_current=current is not None,
        )
        inking = self._prompt_text(
            "Arte-finalista",
            current.inking if current else None,
            has_current=current is not None,
        )
        colors = self._prompt_text(
            "Colorista",
            current.colors if current else None,
            has_current=current is not None,
        )
        letters = self._prompt_text(
            "Letrista",
            current.letters if current else None,
            has_current=current is not None,
        )
        variations = self._prompt_variations(
            current.variations if current else None
        )

        comic = Comic(
            title_eng=title_eng,
            title_pt=title_pt,
            saga_eng=saga_eng,
            saga_pt=saga_pt,
            publisher=publisher,
            imprint=imprint,
            date=date,
            genre=genre,
            sub_genre=sub_genre,
            writing=writing,
            penciling=penciling,
            inking=inking,
            colors=colors,
            letters=letters,
        )
        comic.variations = variations
        return comic

    def _prompt_variations(
            self,
            current: list[ComicVariation] | None,
    ) -> list[ComicVariation]:
        if current is not None:
            answer = input("Editar a lista de edições? [s/N]: ").strip().casefold()
            if answer not in {"s", "sim"}:
                return [
                    ComicVariation.from_dict(variation.to_dict())
                    for variation in current
                ]

        count = self._prompt_integer("Número de edições", minimum=0)
        variations = []
        for index in range(count):
            print(f"Edição {index + 1}")
            state = self._prompt_text("Estado/condição")
            price_usd = self._prompt_nonnegative_float("Preço em USD")
            price_brl = self._prompt_nonnegative_float("Preço em BRL")
            stock = self._prompt_integer("Estoque", minimum=0)
            variations.append(
                ComicVariation(state, price_usd, price_brl, stock)
            )
        return variations

    @staticmethod
    def _prompt_text(
            label: str,
            current: str | None = None,
            has_current: bool = False,
    ) -> str:
        while True:
            if has_current:
                answer = input(f"{label} [{current}]: ").strip()
                if not answer:
                    if current is None:
                        raise ValueError(f"{label} não pode ficar vazio.")
                    return current
            else:
                answer = input(f"{label}: ").strip()

            if answer:
                return answer
            print("Este campo é obrigatório.")

    @staticmethod
    def _prompt_optional_text(
            label: str,
            current: str | None = None,
            has_current: bool = False,
    ) -> str | None:
        if has_current:
            answer = input(
                f"{label} [{current if current is not None else 'nenhum'}] "
                "(deixe em branco para manter, '-' para limpar): "
            ).strip()
            if not answer:
                return current
        else:
            answer = input(f"{label} (opcional): ").strip()

        return None if answer == "-" or not answer else answer

    @staticmethod
    def _prompt_subgenres(current: list[str] | None) -> list[str]:
        while True:
            if current is None:
                answer = input("Subgêneros (separados por vírgula): ").strip()
            else:
                existing = ", ".join(current)
                answer = input(
                    f"Subgêneros [{existing}] (separados por vírgula): "
                ).strip()
                if not answer:
                    return current.copy()

            subgenres = [item.strip() for item in answer.split(",") if item.strip()]
            if subgenres:
                return subgenres
            print("Informe pelo menos um subgênero.")

    @staticmethod
    def _prompt_integer(label: str, minimum: int) -> int:
        while True:
            try:
                value = int(input(f"{label}: "))
                if value < minimum:
                    print(f"Informe um número maior ou igual a {minimum}.")
                    continue
                return value
            except ValueError:
                print("Informe um número inteiro.")

    @staticmethod
    def _prompt_signed_integer(label: str) -> int:
        while True:
            try:
                return int(input(f"{label}: "))
            except ValueError:
                print("Informe um número inteiro.")

    @staticmethod
    def _prompt_nonnegative_float(label: str) -> float:
        while True:
            try:
                value = float(input(f"{label}: "))
                if not math.isfinite(value) or value < 0:
                    print("Informe um valor finito e não negativo.")
                    continue
                return value
            except ValueError:
                print("Informe um número válido.")

    @property
    def _admin_manager(self) -> AdminManager:
        if self._manager is None:
            raise RuntimeError("O administrador ainda não fez login.")
        return self._manager

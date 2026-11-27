# Arquivo das classes básicas
import hashlib
import hmac
import math
import secrets

class Comic:
    def __init__(
            self,
            title_eng: str,
            title_pt: str | None,
            saga_eng: str,
            saga_pt: str | None,
            publisher: str,
            imprint: str,
            date: str,
            genre: str,
            sub_genre: list[str],
            writing: str,
            penciling: str,
            inking: str,
            colors: str,
            letters: str,
    ):
        required_fields = {
            "O título em inglês": title_eng,
            "A série em inglês": saga_eng,
            "A editora": publisher,
            "O selo": imprint,
            "A data": date,
            "O gênero": genre,
            "O roteirista": writing,
            "O desenhista": penciling,
            "O arte-finalista": inking,
            "O colorista": colors,
            "O letrista": letters,
        }
        for label, value in required_fields.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{label} não pode ficar vazio.")

        for label, value in (
            ("O título em português", title_pt),
            ("A série em português", saga_pt),
        ):
            if value is not None and (
                not isinstance(value, str) or not value.strip()
            ):
                raise ValueError(f"{label} deve ser um texto ou não informado.")

        if not isinstance(sub_genre, list) or not sub_genre:
            raise ValueError("Informe pelo menos um subgênero.")
        if any(not isinstance(item, str) or not item.strip() for item in sub_genre):
            raise ValueError("Os subgêneros não podem ficar vazios.")

        self.title_eng = title_eng
        self.title_pt = title_pt
        self.saga_eng = saga_eng
        self.saga_pt = saga_pt
        self.publisher = publisher
        self.imprint = imprint
        self.date = date
        self.genre = genre
        self.sub_genre = sub_genre
        self.writing = writing
        self.penciling = penciling
        self.inking = inking
        self.colors = colors
        self.letters = letters
        self.variations = []

    def to_dict(self) -> dict:
        return {
            "title_eng": self.title_eng,
            "title_pt": self.title_pt,
            "saga_eng": self.saga_eng,
            "saga_pt": self.saga_pt,
            "publisher": self.publisher,
            "imprint": self.imprint,
            "date": self.date,
            "genre": self.genre,
            "sub_genre": self.sub_genre,
            "writing": self.writing,
            "penciling": self.penciling,
            "inking": self.inking,
            "colors": self.colors,
            "letters": self.letters,
            "variations": [
                variation.to_dict()
                for variation in self.variations
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Comic":
        comic = cls(
            title_eng=data["title_eng"],
            title_pt=data["title_pt"],
            saga_eng=data["saga_eng"],
            saga_pt=data["saga_pt"],
            publisher=data["publisher"],
            imprint=data["imprint"],
            date=data["date"],
            genre=data["genre"],
            sub_genre=data["sub_genre"],
            writing=data["writing"],
            penciling=data["penciling"],
            inking=data["inking"],
            colors=data["colors"],
            letters=data["letters"]
        )

        comic.variations = [
            ComicVariation.from_dict(variation)
            for variation in data.get("variations", [])
        ]

        return comic

class ComicVariation:
    def __init__(
            self,
            state: str,
            price_usd: float,
            price_brl: float,
            stock: int
    ):
        if not state.strip():
            raise ValueError("A edição/condição do quadrinho não pode ficar vazia.")
        if not isinstance(stock, int) or isinstance(stock, bool):
            raise TypeError("O estoque deve ser um número inteiro.")
        if stock < 0:
            raise ValueError("O estoque não pode ser negativo.")
        for price in (price_usd, price_brl):
            if not isinstance(price, (int, float)) or isinstance(price, bool):
                raise TypeError("Os preços devem ser números.")
            if not math.isfinite(price) or price < 0:
                raise ValueError("Os preços devem ser valores finitos e não negativos.")

        self.state = state
        self.price_usd = price_usd
        self.price_brl = price_brl
        self.stock = stock

    def adjust_stock(self, amount: int) -> None:
        if not isinstance(amount, int) or isinstance(amount, bool):
            raise TypeError("O ajuste de estoque deve ser um número inteiro.")

        updated_stock = self.stock + amount
        if updated_stock < 0:
            raise ValueError("O estoque não pode ser negativo.")

        self.stock = updated_stock

    def to_dict(self) -> dict:
        return {
            "state": self.state,
            "price_usd": self.price_usd,
            "price_brl": self.price_brl,
            "stock": self.stock,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ComicVariation":
        return cls(
            state = data["state"],
            price_usd = data["price_usd"],
            price_brl = data["price_brl"],
            stock = data.get("stock", 0)
        )

class ComicCatalog:
    def __init__(self, comics: list[Comic]) -> None:
        self.comics = comics

    def find_by_title(self, partial_name: str) -> list[Comic]:
        query = partial_name.strip().casefold()
        if not query:
            return []

        matches: list[Comic] = []

        for comic in self.comics:
            english_matches = query in comic.title_eng.casefold()
            portuguese_matches = (
                comic.title_pt is not None
                and query in comic.title_pt.casefold()
            )

            if english_matches or portuguese_matches:
                matches.append(comic)

        return matches

    def add_comic(self, comic: Comic) -> None:
        if any(
            existing.title_eng.casefold() == comic.title_eng.casefold()
            for existing in self.comics
        ):
            raise ValueError("Já existe um quadrinho com esse título em inglês.")

        self.comics.append(comic)

    def edit_comic(self, current: Comic, replacement: Comic) -> None:
        try:
            index = self.comics.index(current)
        except ValueError as error:
            raise ValueError("O quadrinho não está neste catálogo.") from error

        self.comics[index] = replacement

    def delete_comic(self, comic: Comic) -> None:
        try:
            self.comics.remove(comic)
        except ValueError as error:
            raise ValueError("O quadrinho não está neste catálogo.") from error


class User:
    _PASSWORD_ITERATIONS = 600_000
    _MIN_PASSWORD_LENGTH = 6

    def __init__(
            self,
            name: str,
            username: str,
            password_hash: str,
            password_salt: str,
    ):
        self.name = name
        self.username = username
        self.password_hash = password_hash
        self.password_salt = password_salt
        self.role = "user"

    @classmethod
    def register(cls, name: str, username: str, password: str) -> "User":
        password_hash, password_salt = cls._make_password_credentials(password)
        return cls(name, username, password_hash, password_salt)

    @classmethod
    def _make_password_credentials(cls, password: str) -> tuple[str, str]:
        if len(password) < cls._MIN_PASSWORD_LENGTH:
            raise ValueError(
                f"A senha deve ter pelo menos "
                f"{cls._MIN_PASSWORD_LENGTH} caracteres."
            )

        salt = secrets.token_bytes(16)
        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            cls._PASSWORD_ITERATIONS,
        )
        return password_hash.hex(), salt.hex()

    def verify_password(self, password: str) -> bool:
        salt = bytes.fromhex(self.password_salt)
        attempted_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            self._PASSWORD_ITERATIONS,
        )
        return hmac.compare_digest(attempted_hash.hex(), self.password_hash)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "username": self.username,
            "password_hash": self.password_hash,
            "password_salt": self.password_salt,
            "role": self.role,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(
            name=data["name"],
            username=data["username"],
            password_hash=data["password_hash"],
            password_salt=data["password_salt"],
        )


class Admin(User):
    def __init__(
            self,
            name: str,
            username: str,
            password_hash: str,
            password_salt: str,
            permissions: list[str] | None = None,
    ):
        super().__init__(name, username, password_hash, password_salt)
        self.role = "admin"
        self.permissions = permissions if permissions is not None else []

    @classmethod
    def register(
            cls,
            name: str,
            username: str,
            password: str,
            permissions: list[str] | None = None,
    ) -> "Admin":
        password_hash, password_salt = cls._make_password_credentials(password)
        return cls(
            name,
            username,
            password_hash,
            password_salt,
            permissions,
        )

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["permissions"] = self.permissions
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Admin":
        return cls(
            name=data["name"],
            username=data["username"],
            password_hash=data["password_hash"],
            password_salt=data["password_salt"],
            permissions=data.get("permissions"),
        )
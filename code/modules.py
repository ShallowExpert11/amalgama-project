import hashlib
import hmac
import secrets


# Módulo que detém os modelos essenciais para o funcionamento do código
class Comic:
    def __init__(
            self,
            title_eng: str,
            title_pt: str | None,
            saga_eng: str,
            saga_pt: str,
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
        self.state = state
        self.price_usd = price_usd
        self.price_brl = price_brl
        self.stock = stock

    def adjust_stock(self, amount: int) -> None:
        if not isinstance(amount, int) or isinstance(amount, bool):
            raise TypeError("Stock adjustment must be an integer.")

        updated_stock = self.stock + amount
        if updated_stock < 0:
            raise ValueError("Stock cannot be negative.")

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
        if comic in self.comics:
            raise ValueError("This comic is already in the catalog.")

        self.comics.append(comic)

    def edit_comic(self, current: Comic, replacement: Comic) -> None:
        try:
            index = self.comics.index(current)
        except ValueError as error:
            raise ValueError("The comic is not in this catalog.") from error

        self.comics[index] = replacement

    def delete_comic(self, comic: Comic) -> None:
        try:
            self.comics.remove(comic)
        except ValueError as error:
            raise ValueError("The comic is not in this catalog.") from error


class User:
    _PASSWORD_ITERATIONS = 600_000

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
        if not password:
            raise ValueError("Password cannot be empty.")

        salt = secrets.token_bytes(16)
        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            cls._PASSWORD_ITERATIONS,
        )

        return cls(name, username, password_hash.hex(), salt.hex())

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
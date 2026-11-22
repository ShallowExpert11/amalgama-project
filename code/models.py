#Módulo responsável pelos modelos utilizados no código
class Comic:
    def __init__(
            self,
            title_eng: str,
            title_pt: str,
            saga_eng: str,
            saga_pt: str,
            publisher: str,
            imprint: str,
            date: str,
            genre: str,
            writer: str,
            artist: str,
            cover_artist: str,
            painting: str,
            colors: str,
            letterer: str,
    ):
        self.title_eng = title_eng
        self.title_pt = title_pt
        self.saga_eng = saga_eng
        self.saga_pt = saga_pt
        self.publisher = publisher
        self.imprint = imprint
        self.date = date
        self.genre = genre
        self.writer = writer
        self.artist = artist
        self.cover_artist = cover_artist
        self.painting = painting
        self.colors = colors
        self.letterer = letterer
        self.versions = []

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
            writer=data["writer"],
            artist=data["artist"],
            cover_artist=data["cover_artist"],
            painting=data.get("painting", ""),
            colors=data.get("colors", data.get("colorist", "")),
            letterer=data["letterer"]
        )

        comic.versions = [
            ComicEdition.from_dict(edition)
            for edition in data.get("editions", [])
        ]

        return comic

class ComicEdition:
    def __init__(
            self,
            quality_level: str,
            price_usd: float,
            price_brl: float,
            stock: int
    ):
        self.quality_level = quality_level
        self.price_usd = price_usd
        self.price_brl = price_brl
        self.stock = stock

    @classmethod
    def from_dict(cls, data: dict) -> "ComicEdition":
        return cls(
            quality_level=data["quality_level"],
            price_usd=data["price_usd"],
            price_brl=data["price_brl"],
            stock=data.get("stock", 0),
        )

class User:
    def __init__(
            self,
            name: str,
            username: str,
            password: str,
            password_salt: str = "",
            role: str = "user",
    ):
        self.name = name
        self.username = username
        self.password_hash = password
        self.password_salt = password_salt
        self.role = role

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(
            name=data["name"],
            username=data["username"],
            password=data.get("password_hash", data.get("password", "")),
            password_salt=data.get("password_salt", ""),
            role=data.get("role", "user"),
        )

class Admin(User):
    def __init__(
            self,
            name: str,
            username: str,
            password: str,
            password_salt: str = "",
            permissions: list[str] = None,
    ):
        super().__init__(name, username, password, password_salt, "admin")
        self.permissions = permissions if permissions is not None else []

    @classmethod
    def from_dict(cls, data: dict) -> "Admin":
        return cls(
            name=data["name"],
            username=data["username"],
            password=data["password_hash"],
            password_salt=data.get("password_salt", ""),
            permissions=data.get("permissions", []),
        )

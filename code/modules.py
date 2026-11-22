# Módulo que detém os modelos essenciais para o funcionamento do código
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
            sub_genre: str,
            writing: str,
            art: str,
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
        self.art = art
        self.colors = colors
        self.letters = letters
        self.variations = []

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
            art=data["art"],
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

    @classmethod
    def from_dict(cls, data: dict) -> "ComicVariation":
        return cls(
            state = data(["state"]),
            price_usd = data["price_usd"],
            price_brl = data["price_brl"],
            stock = data.get("stock", 0)
        )


class User: 
    def __init__(
            self,
            name: str,
            username: str,
            password: str
    ):
        self.name = name
        self.username = username
        self.password = password
        self.role = "user"

class Admin(User):
    def __init__(
            self,
            name: str,
            username: str,
            password: str,
            permissions: list[str] = None,
    ):
        super().__init__(name, username, password)
        self.role = "admin"
        self.permissions = permissions if permissions is not None else []
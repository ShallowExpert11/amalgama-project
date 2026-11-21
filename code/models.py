#Módulo responsável pelos modelos utilizados no código
class Comic:
    def __init__(
            self,
            title_eng: str,
            title_pt: str,
            saga_eng: str,
            saga_pt: str,
            publisher: str,
            date: str,
            genre: str,
            writer: str,
            artist: str,
            cover_artists: str,
            painting: str,
            colors: str,
            letterer: str,
            imprint: str,
    ):
        self.title_eng = title_eng
        self.title_pt = title_pt
        self.saga_eng = saga_eng
        self.saga_pt = saga_pt
        self.publisher = publisher
        self.date = date
        self.genre = genre
        self.writter = writer
        self.artist = artist
        self.cover_artists = cover_artists
        self.painting = painting
        self.colors = colors
        self,letterer = letterer
        self.imprint = imprint
        self.versions = []
# Módulo contendo as funcionalidades do banco de dados
import json
from pathlib import Path

class DataBase:
    def __init__(self):
        self.store_path = Path(__file__).resolve().with_name("comics_data.json")

    def load_data(self):
        with self.store_path.open("r", encoding = "utf-8") as file:
            data = json.load(file)

        return data

    def load_comics(self):
        from modules import Comic

        return [
            Comic.from_dict(comic_data)
            for comic_data in self.load_data()
        ]
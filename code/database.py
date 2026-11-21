#Módulo responsável pelo BD
import json
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().with_name("store.json")

DEFAULT_COMICS = [
    {
        "title_eng": "Kingdom Come #1 - Strange Visitor"
        "title_pt": "Reino Do Amanhã"
        ""
    }
]
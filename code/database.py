#Módulo responsável pelo BD
import hashlib
import hmac
import json
from pathlib import Path

try:
    from .models import Admin, Comic, User
except ImportError:
    from models import Admin, Comic, User


class PasswordHasher:
    ITERATIONS = 600_000

    @classmethod
    def verify(cls, password: str, salt: str, stored_hash: str) -> bool:
        calculated_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            cls.ITERATIONS,
        ).hex()

        return hmac.compare_digest(calculated_hash, stored_hash)


class JsonDatabase:
    def __init__(
        self,
        comics_path: Path | None = None,
        users_path: Path | None = None,
    ):
        code_directory = Path(__file__).resolve().parent
        self.comics_path = comics_path or code_directory / "store.json"
        self.users_path = users_path or code_directory / "users.json"
        self.password_hasher = PasswordHasher

    def _load_json(self, path: Path) -> list[dict]:
        if not path.exists() or path.stat().st_size == 0:
            return []

        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            raise ValueError(f"{path.name} must contain a JSON list")

        return data

    def _save_json(self, path: Path, data: list[dict]) -> None:
        with path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def initialize(self) -> None:
        if not self.comics_path.exists():
            self._save_json(self.comics_path, [])

        if not self.users_path.exists():
            self._save_json(self.users_path, [])

    def get_comics(self) -> list[Comic]:
        return [
            Comic.from_dict(comic_data)
            for comic_data in self._load_json(self.comics_path)
        ]

    def get_users(self) -> list[User]:
        users = []

        for user_data in self._load_json(self.users_path):
            if user_data.get("role") == "admin":
                users.append(Admin.from_dict(user_data))
            else:
                users.append(User.from_dict(user_data))

        return users

    def save_comics(self, comics: list[Comic]) -> None:
        comic_data = []

        for comic in comics:
            editions = [
                {
                    "quality_level": edition.quality_level,
                    "price_usd": edition.price_usd,
                    "price_brl": edition.price_brl,
                    "stock": edition.stock,
                }
                for edition in comic.versions
            ]

            comic_data.append({
                "title_eng": comic.title_eng,
                "title_pt": comic.title_pt,
                "saga_eng": comic.saga_eng,
                "saga_pt": comic.saga_pt,
                "publisher": comic.publisher,
                "imprint": comic.imprint,
                "date": comic.date,
                "genre": comic.genre,
                "writer": comic.writer,
                "artist": comic.artist,
                "cover_artist": comic.cover_artist,
                "painting": comic.painting,
                "colors": comic.colors,
                "letterer": comic.letterer,
                "editions": editions,
            })

        self._save_json(self.comics_path, comic_data)

    def save_users(self, users: list[User]) -> None:
        user_data = []

        for user in users:
            data = {
                "name": user.name,
                "username": user.username,
                "password_hash": user.password_hash,
                "password_salt": user.password_salt,
                "role": user.role,
            }

            if isinstance(user, Admin):
                data["permissions"] = user.permissions

            user_data.append(data)

        self._save_json(self.users_path, user_data)

    def authenticate(self, username: str, password: str) -> Admin | User | None:
        for user in self.get_users():
            if user.username != username:
                continue

            if self.password_hasher.verify(
                password,
                user.password_salt,
                user.password_hash,
            ):
                return user

        return None
database = JsonDatabase()

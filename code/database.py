# Módulo contendo as funcionalidades do banco de dados
import json
from pathlib import Path

from modules import Admin, Comic, User


class DataBase:
    def __init__(self, data_directory: Path | None = None):
        self.data_directory = (
            data_directory
            if data_directory is not None
            else Path(__file__).resolve().parent
        )
        self.data_directory.mkdir(parents=True, exist_ok=True)
        self.store_path = self.data_directory / "comics_data.json"
        self.users_path = self.data_directory / "users_data.json"
        self.admins_path = self.data_directory / "admin_data.json"

        for account_path in (self.users_path, self.admins_path):
            if not account_path.exists():
                self._save_records(account_path, [])

    def _load_records(self, path: Path) -> list[dict]:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            raise ValueError(f"{path.name} must contain a JSON array.")

        return data

    def _save_records(self, path: Path, records: list[dict]) -> None:
        temporary_path = path.with_name(path.name + ".tmp")
        with temporary_path.open("w", encoding="utf-8") as file:
            json.dump(records, file, ensure_ascii=False, indent=4)
        temporary_path.replace(path)

    def load_data(self) -> list[dict]:
        return self._load_records(self.store_path)

    def save_data(self, data: list[dict]) -> None:
        self._save_records(self.store_path, data)

    def load_comics(self) -> list[Comic]:
        return [
            Comic.from_dict(comic_data)
            for comic_data in self.load_data()
        ]

    def save_comics(self, comics: list[Comic]) -> None:
        self.save_data([comic.to_dict() for comic in comics])

    def load_users(self) -> list[User]:
        return [
            User.from_dict(user_data)
            for user_data in self._load_records(self.users_path)
        ]

    def save_users(self, users: list[User]) -> None:
        self._save_records(
            self.users_path,
            [user.to_dict() for user in users],
        )

    def load_admins(self) -> list[Admin]:
        return [
            Admin.from_dict(admin_data)
            for admin_data in self._load_records(self.admins_path)
        ]

    def save_admins(self, admins: list[Admin]) -> None:
        self._save_records(
            self.admins_path,
            [admin.to_dict() for admin in admins],
        )
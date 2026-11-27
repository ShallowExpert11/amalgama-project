# Arquivo para mexer no BD
import json
from pathlib import Path

from modules import Admin, Comic, ComicCatalog, User


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
            raise ValueError(f"O arquivo {path.name} deve conter uma lista JSON.")

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


class AdminManager:
    def __init__(
            self,
            database: DataBase,
            admin: Admin,
            catalog: ComicCatalog,
    ):
        if not isinstance(admin, Admin):
            raise PermissionError("É necessário usar uma conta de administrador.")

        self._database = database
        self._admin = admin
        self._catalog = catalog

    @classmethod
    def authenticate(
            cls,
            database: DataBase,
            username: str,
            password: str,
    ) -> "AdminManager":
        normalized_username = username.strip().casefold()

        for admin in database.load_admins():
            if (
                admin.username.casefold() == normalized_username
                and admin.verify_password(password)
            ):
                return cls(
                    database,
                    admin,
                    ComicCatalog(database.load_comics()),
                )

        raise PermissionError("Nome de usuário ou senha de administrador incorretos.")

    def list_comics(self) -> list[Comic]:
        self._require_permission("manage_comics")
        return self._catalog.comics.copy()

    def find_comics(self, partial_name: str) -> list[Comic]:
        self._require_permission("manage_comics")
        return self._catalog.find_by_title(partial_name)

    def add_comic(self, comic: Comic) -> None:
        self._require_permission("manage_comics")
        updated_catalog = ComicCatalog(self._catalog.comics.copy())
        updated_catalog.add_comic(comic)
        self._database.save_comics(updated_catalog.comics)
        self._catalog.comics = updated_catalog.comics

    def edit_comic(self, current: Comic, replacement: Comic) -> None:
        self._require_permission("manage_comics")
        updated_catalog = ComicCatalog(self._catalog.comics.copy())
        updated_catalog.edit_comic(current, replacement)
        self._database.save_comics(updated_catalog.comics)
        self._catalog.comics = updated_catalog.comics

    def delete_comic(self, comic: Comic) -> None:
        self._require_permission("manage_comics")
        updated_catalog = ComicCatalog(self._catalog.comics.copy())
        updated_catalog.delete_comic(comic)
        self._database.save_comics(updated_catalog.comics)
        self._catalog.comics = updated_catalog.comics

    def adjust_stock(
            self,
            comic: Comic,
            variation_index: int,
            amount: int,
    ) -> None:
        self._require_permission("manage_comics")
        if (
            not isinstance(variation_index, int)
            or isinstance(variation_index, bool)
            or variation_index < 0
        ):
            raise ValueError("O índice da edição deve ser um inteiro não negativo.")

        try:
            comic_index = self._catalog.comics.index(comic)
            variation = comic.variations[variation_index]
        except (ValueError, IndexError) as error:
            raise ValueError("O quadrinho ou a edição não foi encontrado.") from error

        updated_comics = [
            Comic.from_dict(existing.to_dict())
            for existing in self._catalog.comics
        ]
        updated_variation = updated_comics[comic_index].variations[variation_index]
        updated_variation.adjust_stock(amount)
        self._database.save_comics(updated_comics)
        variation.stock = updated_variation.stock

    def list_users(self) -> list[dict[str, str]]:
        self._require_permission("manage_users")
        return [
            {
                "name": user.name,
                "username": user.username,
                "role": user.role,
            }
            for user in self._database.load_users()
        ]

    def delete_user(self, username: str) -> None:
        self._require_permission("manage_users")
        normalized_username = username.strip().casefold()
        users = self._database.load_users()
        matches = [
            user for user in users
            if user.username.casefold() == normalized_username
        ]

        if not matches:
            raise ValueError("A conta de usuário não foi encontrada.")
        if len(matches) > 1:
            raise ValueError("Há mais de uma conta com esse nome de usuário.")

        user_to_delete = matches[0]
        updated_users = [user for user in users if user is not user_to_delete]
        self._database.save_users(updated_users)

    def change_password(self, current_password: str, new_password: str) -> None:
        if not self._admin.verify_password(current_password):
            raise PermissionError("A senha atual está incorreta.")
        if not new_password:
            raise ValueError("A nova senha não pode ficar vazia.")

        updated_admin = Admin.register(
            name=self._admin.name,
            username=self._admin.username,
            password=new_password,
            permissions=self._admin.permissions,
        )
        admins = self._database.load_admins()
        matching_admins = [
            index
            for index, admin in enumerate(admins)
            if admin.username.casefold() == self._admin.username.casefold()
        ]
        if len(matching_admins) != 1:
            raise ValueError(
                "Não foi possível identificar uma única conta de administrador."
            )

        admins[matching_admins[0]] = updated_admin
        self._database.save_admins(admins)
        self._admin = updated_admin

    def _require_permission(self, permission: str) -> None:
        if permission not in self._admin.permissions:
            raise PermissionError("O administrador não tem essa permissão.")


class UserManager:
    def __init__(self, database: DataBase):
        self._database = database

    def register(
            self,
            name: str,
            username: str,
            password: str,
    ) -> User:
        normalized_name = name.strip()
        normalized_username = username.strip()

        if not normalized_name:
            raise ValueError("O nome não pode ficar vazio.")
        if not normalized_username:
            raise ValueError("O nome de usuário não pode ficar vazio.")

        users = self._database.load_users()
        all_usernames = {user.username.casefold() for user in users}
        all_usernames.update(
            admin.username.casefold()
            for admin in self._database.load_admins()
        )
        if normalized_username.casefold() in all_usernames:
            raise ValueError("Esse nome de usuário já está sendo usado.")

        user = User.register(normalized_name, normalized_username, password)
        users.append(user)
        self._database.save_users(users)
        return user

    def authenticate(self, username: str, password: str) -> User:
        normalized_username = username.strip().casefold()

        for user in self._database.load_users():
            if (
                user.username.casefold() == normalized_username
                and user.verify_password(password)
            ):
                return user

        raise PermissionError("Nome de usuário ou senha incorretos.")

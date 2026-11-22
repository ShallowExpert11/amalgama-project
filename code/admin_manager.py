from database import DataBase
from modules import Admin, Comic, ComicCatalog


class AdminManager:
    def __init__(
            self,
            database: DataBase,
            admin: Admin,
            catalog: ComicCatalog,
    ):
        if not isinstance(admin, Admin):
            raise PermissionError("An administrator account is required.")

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

        raise PermissionError("Invalid administrator username or password.")

    def list_comics(self) -> list[Comic]:
        return self._catalog.comics.copy()

    def find_comics(self, partial_name: str) -> list[Comic]:
        return self._catalog.find_by_title(partial_name)

    def add_comic(self, comic: Comic) -> None:
        updated_catalog = ComicCatalog(self._catalog.comics.copy())
        updated_catalog.add_comic(comic)
        self._database.save_comics(updated_catalog.comics)
        self._catalog.comics = updated_catalog.comics

    def edit_comic(self, current: Comic, replacement: Comic) -> None:
        updated_catalog = ComicCatalog(self._catalog.comics.copy())
        updated_catalog.edit_comic(current, replacement)
        self._database.save_comics(updated_catalog.comics)
        self._catalog.comics = updated_catalog.comics

    def delete_comic(self, comic: Comic) -> None:
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
        try:
            comic_index = self._catalog.comics.index(comic)
            variation = comic.variations[variation_index]
        except (ValueError, IndexError) as error:
            raise ValueError("The comic or variation was not found.") from error

        updated_comics = [
            Comic.from_dict(existing.to_dict())
            for existing in self._catalog.comics
        ]
        updated_variation = updated_comics[comic_index].variations[variation_index]
        updated_variation.adjust_stock(amount)
        self._database.save_comics(updated_comics)
        variation.stock = updated_variation.stock

    def list_users(self) -> list[dict[str, str]]:
        return [
            {
                "name": user.name,
                "username": user.username,
                "role": user.role,
            }
            for user in self._database.load_users()
        ]

    def delete_user(self, username: str) -> None:
        normalized_username = username.strip().casefold()
        users = self._database.load_users()
        matches = [
            user for user in users
            if user.username.casefold() == normalized_username
        ]

        if not matches:
            raise ValueError("The user account was not found.")
        if len(matches) > 1:
            raise ValueError("More than one account has that username.")

        user_to_delete = matches[0]
        updated_users = [user for user in users if user is not user_to_delete]
        self._database.save_users(updated_users)

from database import DataBase
from modules import User


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
            raise ValueError("Name cannot be empty.")
        if not normalized_username:
            raise ValueError("Username cannot be empty.")

        users = self._database.load_users()
        all_usernames = {user.username.casefold() for user in users}
        all_usernames.update(
            admin.username.casefold()
            for admin in self._database.load_admins()
        )
        if normalized_username.casefold() in all_usernames:
            raise ValueError("That username is already in use.")

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

        raise PermissionError("Invalid username or password.")

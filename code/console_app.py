import math
from getpass import getpass

from admin_manager import AdminManager
from database import DataBase
from modules import Admin, Comic, ComicVariation


class AdminConsole:
    def __init__(self, database: DataBase):
        self._database = database
        self._manager: AdminManager | None = None

    def run(self) -> None:
        try:
            self._create_first_admin_if_needed()
        except (OSError, ValueError) as error:
            print(f"Could not set up administrator: {error}")
            return

        if not self._login():
            return

        actions = {
            "1": self._list_comics,
            "2": self._search_comics,
            "3": self._add_comic,
            "4": self._edit_comic,
            "5": self._delete_comic,
            "6": self._adjust_stock,
            "7": self._list_users,
            "8": self._delete_user,
            "9": self._change_password,
        }

        while True:
            self._show_menu()
            choice = input("Choose an option: ").strip()
            if choice == "0":
                return

            action = actions.get(choice)
            if action is None:
                print("Choose a listed option.")
                continue

            try:
                action()
            except (OSError, TypeError, ValueError) as error:
                print(f"Action failed: {error}")

    def _create_first_admin_if_needed(self) -> None:
        if self._database.load_admins():
            return

        print("No administrator exists. Create the first admin account.")
        name = self._prompt_text("Admin name")
        username = self._prompt_text("Admin username")
        existing_usernames = {
            user.username.casefold()
            for user in self._database.load_users()
        }
        if username.casefold() in existing_usernames:
            raise ValueError("That username is already in use.")

        password = getpass("Admin password: ")
        confirmation = getpass("Confirm password: ")
        if password != confirmation:
            raise ValueError("The passwords do not match.")

        admin = Admin.register(name, username, password)
        admin.permissions = ["manage_comics", "manage_users"]
        self._database.save_admins([admin])
        print("Administrator account created.")

    def _login(self) -> bool:
        for _ in range(3):
            username = input("Admin username: ").strip()
            password = getpass("Admin password: ")
            try:
                self._manager = AdminManager.authenticate(
                    self._database,
                    username,
                    password,
                )
                print("Login successful.")
                return True
            except PermissionError:
                print("Invalid username or password.")

        print("Too many failed attempts.")
        return False

    @staticmethod
    def _show_menu() -> None:
        print(
            "\n1. List comics\n"
            "2. Search comics\n"
            "3. Add comic\n"
            "4. Edit comic\n"
            "5. Delete comic\n"
            "6. Adjust stock\n"
            "7. List users\n"
            "8. Delete user\n"
            "9. Change admin password\n"
            "0. Exit"
        )

    def _list_comics(self) -> None:
        comics = self._admin_manager.list_comics()
        if not comics:
            print("There are no comics in the catalog.")
            return

        for index, comic in enumerate(comics, start=1):
            print(f"\n{index}.")
            self._display_comic(comic)

    def _search_comics(self) -> None:
        query = input("Title to search: ")
        comics = self._admin_manager.find_comics(query)
        if not comics:
            print("No comics matched that search.")
            return

        for comic in comics:
            print()
            self._display_comic(comic)

    def _add_comic(self) -> None:
        comic = self._prompt_comic()
        self._admin_manager.add_comic(comic)
        print("Comic added.")

    def _edit_comic(self) -> None:
        current = self._select_comic()
        replacement = self._prompt_comic(current)
        self._admin_manager.edit_comic(current, replacement)
        print("Comic updated.")

    def _delete_comic(self) -> None:
        comic = self._select_comic()
        confirmation = input(
            f"Delete {comic.title_eng!r}? Type 'yes' to confirm: "
        ).strip().casefold()
        if confirmation == "yes":
            self._admin_manager.delete_comic(comic)
            print("Comic deleted.")
        else:
            print("Deletion cancelled.")

    def _adjust_stock(self) -> None:
        comic = self._select_comic()
        if not comic.variations:
            print("This comic has no variations.")
            return

        for index, variation in enumerate(comic.variations, start=1):
            print(f"{index}. {variation.state}: stock {variation.stock}")

        variation_index = self._prompt_integer(
            "Variation number",
            minimum=1,
        ) - 1
        amount = self._prompt_signed_integer(
            "Stock change (positive to add, negative to remove)"
        )
        self._admin_manager.adjust_stock(comic, variation_index, amount)
        print("Stock updated.")

    def _list_users(self) -> None:
        users = self._admin_manager.list_users()
        if not users:
            print("There are no registered users.")
            return

        for user in users:
            print(f"{user['name']} (@{user['username']})")

    def _delete_user(self) -> None:
        username = input("Username to delete: ").strip()
        confirmation = input(
            f"Delete user {username!r}? Type 'yes' to confirm: "
        ).strip().casefold()
        if confirmation == "yes":
            self._admin_manager.delete_user(username)
            print("User deleted.")
        else:
            print("Deletion cancelled.")

    def _change_password(self) -> None:
        current_password = getpass("Current password: ")
        new_password = getpass("New password: ")
        confirmation = getpass("Confirm new password: ")
        if new_password != confirmation:
            raise ValueError("The passwords do not match.")

        self._admin_manager.change_password(current_password, new_password)
        print("Password changed.")

    def _select_comic(self) -> Comic:
        comics = self._admin_manager.list_comics()
        if not comics:
            raise ValueError("The catalog is empty.")

        for index, comic in enumerate(comics, start=1):
            print(f"{index}. {comic.title_eng}")

        selection = self._prompt_integer("Comic number", minimum=1)
        if selection > len(comics):
            raise ValueError("There is no comic with that number.")
        return comics[selection - 1]

    @staticmethod
    def _display_comic(comic: Comic) -> None:
        print(f"Title: {comic.title_eng}")
        if comic.title_pt is not None:
            print(f"Portuguese title: {comic.title_pt}")
        print(f"Series: {comic.saga_eng}")
        print(f"Publisher: {comic.publisher} / {comic.imprint}")
        print(f"Date: {comic.date}")
        print(f"Genre: {comic.genre}")
        print(f"Subgenres: {', '.join(comic.sub_genre)}")
        print(
            f"Writing: {comic.writing}; pencils: {comic.penciling}; "
            f"inks: {comic.inking}; colors: {comic.colors}; "
            f"letters: {comic.letters}"
        )
        for variation in comic.variations:
            print(
                f"  {variation.state}: USD {variation.price_usd:.2f}, "
                f"BRL {variation.price_brl:.2f}, stock {variation.stock}"
            )

    def _prompt_comic(self, current: Comic | None = None) -> Comic:
        title_eng = self._prompt_text(
            "English title",
            current.title_eng if current else None,
            has_current=current is not None,
        )
        title_pt = self._prompt_optional_text(
            "Portuguese title (use '-' for none)",
            current.title_pt if current else None,
            has_current=current is not None,
        )
        saga_eng = self._prompt_text(
            "English series",
            current.saga_eng if current else None,
            has_current=current is not None,
        )
        saga_pt = self._prompt_optional_text(
            "Portuguese series (use '-' for none)",
            current.saga_pt if current else None,
            has_current=current is not None,
        )
        publisher = self._prompt_text(
            "Publisher",
            current.publisher if current else None,
            has_current=current is not None,
        )
        imprint = self._prompt_text(
            "Imprint",
            current.imprint if current else None,
            has_current=current is not None,
        )
        date = self._prompt_text(
            "Date",
            current.date if current else None,
            has_current=current is not None,
        )
        genre = self._prompt_text(
            "Genre",
            current.genre if current else None,
            has_current=current is not None,
        )
        sub_genre = self._prompt_subgenres(
            current.sub_genre if current else None
        )
        writing = self._prompt_text(
            "Writer",
            current.writing if current else None,
            has_current=current is not None,
        )
        penciling = self._prompt_text(
            "Penciler",
            current.penciling if current else None,
            has_current=current is not None,
        )
        inking = self._prompt_text(
            "Inker",
            current.inking if current else None,
            has_current=current is not None,
        )
        colors = self._prompt_text(
            "Colorist",
            current.colors if current else None,
            has_current=current is not None,
        )
        letters = self._prompt_text(
            "Letterer",
            current.letters if current else None,
            has_current=current is not None,
        )
        variations = self._prompt_variations(
            current.variations if current else None
        )

        comic = Comic(
            title_eng=title_eng,
            title_pt=title_pt,
            saga_eng=saga_eng,
            saga_pt=saga_pt,
            publisher=publisher,
            imprint=imprint,
            date=date,
            genre=genre,
            sub_genre=sub_genre,
            writing=writing,
            penciling=penciling,
            inking=inking,
            colors=colors,
            letters=letters,
        )
        comic.variations = variations
        return comic

    def _prompt_variations(
            self,
            current: list[ComicVariation] | None,
    ) -> list[ComicVariation]:
        if current is not None:
            answer = input("Edit variation list? [y/N]: ").strip().casefold()
            if answer not in {"y", "yes"}:
                return [
                    ComicVariation.from_dict(variation.to_dict())
                    for variation in current
                ]

        count = self._prompt_integer("Number of variations", minimum=0)
        variations = []
        for index in range(count):
            print(f"Variation {index + 1}")
            state = self._prompt_text("Condition/state")
            price_usd = self._prompt_nonnegative_float("Price in USD")
            price_brl = self._prompt_nonnegative_float("Price in BRL")
            stock = self._prompt_integer("Stock", minimum=0)
            variations.append(
                ComicVariation(state, price_usd, price_brl, stock)
            )
        return variations

    @staticmethod
    def _prompt_text(
            label: str,
            current: str | None = None,
            has_current: bool = False,
    ) -> str:
        while True:
            if has_current:
                answer = input(f"{label} [{current}]: ").strip()
                if not answer:
                    if current is None:
                        raise ValueError(f"{label} cannot be empty.")
                    return current
            else:
                answer = input(f"{label}: ").strip()

            if answer:
                return answer
            print("A value is required.")

    @staticmethod
    def _prompt_optional_text(
            label: str,
            current: str | None = None,
            has_current: bool = False,
    ) -> str | None:
        if has_current:
            answer = input(
                f"{label} [{current if current is not None else 'none'}] "
                "(blank keeps current, '-' clears): "
            ).strip()
            if not answer:
                return current
        else:
            answer = input(f"{label} (optional): ").strip()

        return None if answer == "-" or not answer else answer

    @staticmethod
    def _prompt_subgenres(current: list[str] | None) -> list[str]:
        while True:
            if current is None:
                answer = input("Subgenres (comma-separated): ").strip()
            else:
                existing = ", ".join(current)
                answer = input(
                    f"Subgenres [{existing}] (comma-separated): "
                ).strip()
                if not answer:
                    return current.copy()

            subgenres = [item.strip() for item in answer.split(",") if item.strip()]
            if subgenres:
                return subgenres
            print("Enter at least one subgenre.")

    @staticmethod
    def _prompt_integer(label: str, minimum: int) -> int:
        while True:
            try:
                value = int(input(f"{label}: "))
                if value < minimum:
                    print(f"Enter a number no smaller than {minimum}.")
                    continue
                return value
            except ValueError:
                print("Enter a whole number.")

    @staticmethod
    def _prompt_signed_integer(label: str) -> int:
        while True:
            try:
                return int(input(f"{label}: "))
            except ValueError:
                print("Enter a whole number.")

    @staticmethod
    def _prompt_nonnegative_float(label: str) -> float:
        while True:
            try:
                value = float(input(f"{label}: "))
                if not math.isfinite(value) or value < 0:
                    print("Enter a finite, non-negative amount.")
                    continue
                return value
            except ValueError:
                print("Enter a valid number.")

    @property
    def _admin_manager(self) -> AdminManager:
        if self._manager is None:
            raise RuntimeError("The administrator has not logged in.")
        return self._manager

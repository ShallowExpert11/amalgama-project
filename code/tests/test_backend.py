from contextlib import redirect_stdout
from io import StringIO
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from admin_manager import AdminManager
from console_app import AdminConsole
from database import DataBase
from modules import Admin, Comic, ComicVariation
from user_manager import UserManager


def make_comic(title: str) -> Comic:
    comic = Comic(
        title_eng=title,
        title_pt=None,
        saga_eng="Test Series",
        saga_pt=None,
        publisher="Test Publisher",
        imprint="Test Imprint",
        date="01/01/2025",
        genre="Test",
        sub_genre=["Test"],
        writing="Test Writer",
        penciling="Test Penciler",
        inking="Test Inker",
        colors="Test Colorist",
        letters="Test Letterer",
    )
    comic.variations = [ComicVariation("VF", 10.0, 50.0, 3)]
    return comic


class BackendTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.database = DataBase(Path(self.temporary_directory.name))
        self.database.save_comics([make_comic("First Comic")])

        admin = Admin.register("Test Admin", "manager", "test-admin-password")
        admin.permissions = ["manage_comics", "manage_users"]
        self.database.save_admins([admin])
        self.manager = AdminManager.authenticate(
            self.database,
            "MANAGER",
            "test-admin-password",
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_account_files_are_initialized_as_json_arrays(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            database = DataBase(Path(directory))
            self.assertEqual(json.loads(database.users_path.read_text()), [])
            self.assertEqual(json.loads(database.admins_path.read_text()), [])

    def test_admin_can_add_edit_delete_and_save_comics(self) -> None:
        added = make_comic("Second Comic")
        self.manager.add_comic(added)
        self.assertEqual(len(self.database.load_comics()), 2)

        replacement = make_comic("Edited Comic")
        self.manager.edit_comic(added, replacement)
        self.assertEqual(
            [comic.title_eng for comic in self.database.load_comics()],
            ["First Comic", "Edited Comic"],
        )

        self.manager.delete_comic(replacement)
        self.assertEqual(
            [comic.title_eng for comic in self.database.load_comics()],
            ["First Comic"],
        )

    def test_partial_title_search_returns_all_matches(self) -> None:
        self.manager.add_comic(make_comic("First Comic: Second Issue"))
        results = self.manager.find_comics("  FIRST COMIC ")

        self.assertEqual(len(results), 2)
        self.assertEqual(self.manager.find_comics("   "), [])

    def test_stock_change_persists_and_cannot_go_below_zero(self) -> None:
        comic = self.manager.list_comics()[0]
        self.manager.adjust_stock(comic, 0, 2)
        self.assertEqual(self.database.load_comics()[0].variations[0].stock, 5)

        with self.assertRaises(ValueError):
            self.manager.adjust_stock(comic, 0, -6)

        self.assertEqual(self.database.load_comics()[0].variations[0].stock, 5)

    def test_models_reject_invalid_titles_and_variation_values(self) -> None:
        comic_data = make_comic("Valid Comic").to_dict()
        comic_data["title_eng"] = " "
        with self.assertRaises(ValueError):
            Comic.from_dict(comic_data)

        with self.assertRaises(ValueError):
            ComicVariation("VF", 10.0, 50.0, -1)

    def test_users_can_register_and_authenticate_with_unique_names(self) -> None:
        user_manager = UserManager(self.database)
        user_manager.register("Reader", "reader", "reader-test-password")

        user = user_manager.authenticate("READER", "reader-test-password")
        self.assertEqual(user.username, "reader")
        with self.assertRaises(PermissionError):
            user_manager.authenticate("reader", "incorrect-password")
        with self.assertRaises(ValueError):
            user_manager.register("Another Reader", "READER", "another-password")

    def test_registration_rejects_short_passwords(self) -> None:
        with self.assertRaises(ValueError):
            UserManager(self.database).register("Reader", "reader", "short")

    def test_admin_can_list_and_delete_users_without_exposing_hashes(self) -> None:
        UserManager(self.database).register(
            "Reader",
            "reader",
            "reader-test-password",
        )

        self.assertEqual(
            self.manager.list_users(),
            [{"name": "Reader", "username": "reader", "role": "user"}],
        )
        self.manager.delete_user("READER")
        self.assertEqual(self.manager.list_users(), [])
        self.assertEqual(len(self.database.load_admins()), 1)

    def test_admin_password_change_invalidates_old_password(self) -> None:
        self.manager.change_password(
            "test-admin-password",
            "new-test-admin-password",
        )
        with self.assertRaises(PermissionError):
            AdminManager.authenticate(
                self.database,
                "manager",
                "test-admin-password",
            )
        authenticated_manager = AdminManager.authenticate(
            self.database,
            "manager",
            "new-test-admin-password",
        )
        self.assertIsInstance(authenticated_manager, AdminManager)

    def test_admin_permissions_are_enforced(self) -> None:
        limited_admin = Admin.register(
            "Limited Admin",
            "limited",
            "limited-admin-password",
            permissions=["manage_comics"],
        )
        self.database.save_admins([limited_admin])
        manager = AdminManager.authenticate(
            self.database,
            "limited",
            "limited-admin-password",
        )

        with self.assertRaises(PermissionError):
            manager.list_users()

    def test_console_login_can_list_comics_and_exit(self) -> None:
        output = StringIO()
        with (
            patch("builtins.input", side_effect=["manager", "1", "0"]),
            patch("console_app.getpass", return_value="test-admin-password"),
            redirect_stdout(output),
        ):
            AdminConsole(self.database).run()

        self.assertIn("Login successful.", output.getvalue())
        self.assertIn("First Comic", output.getvalue())

    def test_console_creates_first_admin_without_echoing_password(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            database = DataBase(Path(directory))
            database.save_comics([make_comic("First Comic")])
            output = StringIO()
            with (
                patch(
                    "builtins.input",
                    side_effect=["Test Admin", "firstadmin", "firstadmin", "0"],
                ),
                patch(
                    "console_app.getpass",
                    side_effect=[
                        "first-admin-password",
                        "first-admin-password",
                        "first-admin-password",
                    ],
                ),
                redirect_stdout(output),
            ):
                AdminConsole(database).run()

            self.assertIn("Administrator account created.", output.getvalue())
            self.assertIn("Login successful.", output.getvalue())
            self.assertNotIn(
                "first-admin-password",
                database.admins_path.read_text(encoding="utf-8"),
            )

    def test_account_storage_never_contains_plain_passwords(self) -> None:
        UserManager(self.database).register(
            "Reader",
            "reader",
            "reader-test-password",
        )
        stored_data = self.database.users_path.read_text(encoding="utf-8")
        self.assertNotIn("reader-test-password", stored_data)
        self.assertIn("password_hash", stored_data)
        self.assertIn("password_salt", stored_data)


if __name__ == "__main__":
    unittest.main()

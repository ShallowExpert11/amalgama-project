# Amalgama Project

A Python comic-store management system built with object-oriented classes.

## Run

From the repository root:

```powershell
python code/main.py
```

The first run asks you to create an administrator if no admin account exists.
The console currently provides the management workflows; a GUI can be added
later using the same managers and models.

## Structure

- `Comic` and `ComicVariation` represent catalog and inventory data.
- `DataBase` reads and writes JSON files.
- `ComicCatalog`, `AdminManager`, and `UserManager` contain catalog and account
  operations.
- `AdminConsole` is the current console interface and delegates work to those
  classes.

## Data and credentials

Comic data is stored in `code/comics_data.json`. User and admin data are stored
in local `code/users_data.json` and `code/admin_data.json` files, which are
ignored by Git. Passwords are stored as salted PBKDF2 hashes, not plaintext.
New passwords must contain at least 12 characters.
This local JSON approach is for learning and is not suitable for production
authentication.

## Tests

From the `code` directory:

```powershell
python -m unittest discover -s tests
```

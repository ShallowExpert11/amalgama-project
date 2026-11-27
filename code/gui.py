# Módulo da interface grafica
import tkinter as tk
from tkinter import messagebox, ttk

from backend import AdminManager, DataBase, UserManager
from modules import Comic, ComicCatalog, ComicVariation

class ComicApp:
    def __init__(self, root: tk.Tk, database: DataBase):
        self.root = root
        self.database = database
        self.user_manager = UserManager(database)
        self.current_user = None
        self.admin_manager: AdminManager | None = None
        self.cart: list[dict] = []
        root.title("Amalgama Comix - Loja de Novels e Quadrinhos")
        root.geometry("900x600")
        root.minsize(700, 500)
        root.configure(bg="#6a6aff")
        self.show_welcome()

    def _clear_screen(self) -> None:
        for widget in self.root.winfo_children():
            widget.destroy()

    def _make_header(self) -> None:
        header = tk.Frame(self.root, bg="#6a6aff", height=56)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Amalgama",
            bg="#6a6aff",
            fg="white",
            borderwidth=0,
            font=("Segoe UI", 18, "bold"),
        ).pack(side="left", padx=24)
        tk.Label(
            header,
            text="Comix",
            bg="#6a6aff",
            fg="#ffb000",
            borderwidth=0,
            font=("Segoe UI", 18, "bold"),
        ).pack(side="left")

    def show_welcome(self) -> None:
        self._clear_screen()
        self._make_header()

        buttons = ttk.Frame(self.root, padding=20)
        buttons.pack(expand=True)

        ttk.Button(
            buttons,
            text="Cadastrar-se",
            width=24,
            command=lambda: self.show_auth("signup"),
        ).pack(pady=8)
        ttk.Button(
            buttons,
            text="Realizar Login",
            width=24,
            command=lambda: self.show_auth("login"),
        ).pack(pady=8)

    def show_auth(self, mode: str) -> None:
        self._clear_screen()
        self._make_header()

        form = ttk.Frame(self.root, padding=24)
        form.pack(expand=True)
        heading = "Criar conta" if mode == "signup" else "Realizar Login"
        ttk.Label(form, text=heading, font=("Segoe UI", 20, "bold")).pack(
            anchor="w", pady=(0, 16),
        )

        fields: dict[str, ttk.Entry] = {}
        if mode == "signup":
            ttk.Label(form, text="Nome").pack(anchor="w")
            fields["name"] = ttk.Entry(form, width=36)
            fields["name"].pack(fill="x", pady=(4, 12))

        ttk.Label(form, text="Usuário").pack(anchor="w")
        fields["username"] = ttk.Entry(form, width=36)
        fields["username"].pack(fill="x", pady=(4, 12))

        ttk.Label(form, text="Senha").pack(anchor="w")
        fields["password"] = ttk.Entry(form, width=36, show="*")
        fields["password"].pack(fill="x", pady=(4, 12))

        if mode == "signup":
            ttk.Label(form, text="Confirmar senha").pack(anchor="w")
            fields["confirmation"] = ttk.Entry(form, width=36, show="*")
            fields["confirmation"].pack(fill="x", pady=(4, 12))

        def submit(_event: tk.Event | None = None) -> None:
            try:
                if mode == "signup":
                    password = fields["password"].get()
                    if password != fields["confirmation"].get():
                        raise ValueError("As senhas não são iguais.")
                    self.user_manager.register(
                        fields["name"].get(),
                        fields["username"].get(),
                        password,
                    )
                    messagebox.showinfo(
                        "Conta criada",
                        "Sua conta foi criada. Agora você pode fazer login.",
                        parent=self.root,
                    )
                    self.show_auth("login")
                    return

                username = fields["username"].get()
                password = fields["password"].get()
                try:
                    self.current_user = self.user_manager.authenticate(
                        username,
                        password,
                    )
                except PermissionError:
                    self.admin_manager = AdminManager.authenticate(
                        self.database,
                        username,
                        password,
                    )
                    self.current_user = next(
                        admin
                        for admin in self.database.load_admins()
                        if admin.username.casefold() == username.strip().casefold()
                    )

                    messagebox.showinfo(
                        "Login administrativo",
                        f"Bem-vindo, {self.current_user.name}!",
                        parent=self.root,
                    )
                    self.show_admin_menu()
                    return

                messagebox.showinfo(
                    "Login realizado",
                    f"Bem-vindo, {self.current_user.name}!",
                    parent=self.root,
                )
                self.show_store()
            except PermissionError:
                messagebox.showerror(
                    "Falha no login",
                    "Usuário ou senha incorretos.",
                    parent=self.root,
                )
            except (OSError, TypeError, ValueError) as error:
                messagebox.showerror(
                    "Não foi possível continuar",
                    str(error),
                    parent=self.root,
                )

        button_text = "Criar conta" if mode == "signup" else "Entrar"
        ttk.Button(
            form,
            text=button_text,
            command=submit,
        ).pack(fill="x", pady=(4, 8))
        ttk.Button(
            form,
            text="Voltar",
            command=self.show_welcome,
        ).pack(fill="x")
        fields["username"].focus_set()

    def show_admin_menu(self) -> None:
        self._clear_screen()
        self._make_header()

        menu = ttk.Frame(self.root, padding=24)
        menu.pack(expand=True)

        ttk.Label(
            menu,
            text=f"Administração - {self.current_user.name}",
            font=("Segoe UI", 18, "bold"),
        ).pack(pady=(0, 16))
        ttk.Button(
            menu,
            text="Ver quadrinhos e estoque",
            width=30,
            command=self.show_admin_inventory,
        ).pack(pady=8)
        ttk.Button(
            menu,
            text="Sair",
            width=30,
            command=self._logout,
        ).pack(pady=8)

    def show_admin_inventory(self) -> None:
        if self.admin_manager is None:
            raise RuntimeError("O administrador ainda não fez login.")

        self._clear_screen()
        self._make_header()

        page = ttk.Frame(self.root, padding=24)
        page.pack(fill="both", expand=True)
        ttk.Label(
            page,
            text="Quadrinhos e estoque",
            font=("Segoe UI", 18, "bold"),
        ).pack(anchor="w")

        comics = self.admin_manager.list_comics()
        toolbar = ttk.Frame(page)
        toolbar.pack(fill="x", pady=12)
        ttk.Button(
            toolbar,
            text="Adicionar quadrinho",
            command=self._open_add_comic,
        ).pack(side="left")

        tree = ttk.Treeview(
            page,
            columns=("series", "publisher", "edition", "price", "stock"),
            show="tree headings",
            selectmode="browse",
        )
        tree.heading("#0", text="Quadrinho")
        tree.heading("series", text="Série")
        tree.heading("publisher", text="Editora")
        tree.heading("edition", text="Edição/condição")
        tree.heading("price", text="Preço (BRL)")
        tree.heading("stock", text="Estoque")
        tree.column("#0", width=250)
        tree.column("series", width=150)
        tree.column("publisher", width=140)
        tree.column("edition", width=130)
        tree.column("price", width=100, anchor="e")
        tree.column("stock", width=80, anchor="e")
        tree.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(page, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.place(in_=tree, relx=1.0, relheight=1.0, anchor="ne")

        comics_by_item: dict[str, Comic] = {}
        for index, comic in enumerate(comics):
            comic_item = f"comic-{index}"
            comics_by_item[comic_item] = comic
            tree.insert(
                "",
                tk.END,
                iid=comic_item,
                text=comic.title_pt or comic.title_eng,
                values=(
                    comic.saga_pt or comic.saga_eng,
                    comic.publisher,
                    "",
                    "",
                    "",
                ),
            )
            for variation_index, variation in enumerate(comic.variations):
                tree.insert(
                    comic_item,
                    tk.END,
                    iid=f"{comic_item}-variation-{variation_index}",
                    text="",
                    values=(
                        "",
                        "",
                        variation.state,
                        f"R$ {variation.price_brl:.2f}",
                        variation.stock,
                    ),
                )

        def remove_selected_comic() -> None:
            selected = tree.selection()
            if not selected:
                messagebox.showwarning(
                    "Nenhum quadrinho selecionado",
                    "Selecione um quadrinho ou uma de suas edições.",
                    parent=self.root,
                )
                return

            item = selected[0]
            while tree.parent(item):
                item = tree.parent(item)
            comic = comics_by_item[item]
            if not messagebox.askyesno(
                "Remover quadrinho",
                f"Remover {comic.title_eng!r} do catálogo?",
                parent=self.root,
            ):
                return

            try:
                self.admin_manager.delete_comic(comic)
                self.show_admin_inventory()
            except (OSError, TypeError, ValueError) as error:
                messagebox.showerror(
                    "Não foi possível remover",
                    str(error),
                    parent=self.root,
                )

        ttk.Button(
            toolbar,
            text="Remover selecionado",
            command=remove_selected_comic,
        ).pack(side="left", padx=8)
        ttk.Button(
            toolbar,
            text="Voltar",
            command=self.show_admin_menu,
        ).pack(side="right")

    def _open_add_comic(self) -> None:
        if self.admin_manager is None:
            raise RuntimeError("O administrador ainda não fez login.")

        dialog = tk.Toplevel(self.root)
        dialog.title("Adicionar quadrinho")
        dialog.geometry("950x660")
        dialog.minsize(850, 600)
        dialog.transient(self.root)
        dialog.grab_set()

        form = ttk.Frame(dialog, padding=20)
        form.pack(fill="both", expand=True)
        ttk.Label(
            form,
            text="Dados do quadrinho e primeira edição",
            font=("Segoe UI", 16, "bold"),
        ).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 16))

        field_specs = (
            ("title_eng", "Título em inglês"),
            ("title_pt", "Título em português"),
            ("saga_eng", "Série em inglês"),
            ("saga_pt", "Série em português"),
            ("publisher", "Editora"),
            ("imprint", "Selo"),
            ("date", "Data"),
            ("genre", "Gênero"),
            ("sub_genre", "Subgêneros (separe por vírgula)"),
            ("writing", "Roteiro"),
            ("penciling", "Desenho"),
            ("inking", "Arte-final"),
            ("colors", "Cores"),
            ("letters", "Letras"),
            ("state", "Edição/condição"),
            ("price_usd", "Preço em USD"),
            ("price_brl", "Preço em BRL"),
            ("stock", "Estoque"),
        )
        fields: dict[str, ttk.Entry] = {}
        for index, (name, label) in enumerate(field_specs):
            row = 1 + index // 2
            column = (index % 2) * 2
            ttk.Label(form, text=label).grid(
                row=row,
                column=column,
                sticky="w",
                padx=(0, 8),
                pady=5,
            )
            entry = ttk.Entry(form, width=30)
            entry.grid(
                row=row,
                column=column + 1,
                sticky="ew",
                padx=(0, 16),
                pady=5,
            )
            fields[name] = entry

        form.columnconfigure(1, weight=1)
        form.columnconfigure(3, weight=1)

        def save_comic() -> None:
            try:
                values = {
                    name: entry.get().strip()
                    for name, entry in fields.items()
                }
                comic = Comic(
                    title_eng=values["title_eng"],
                    title_pt=values["title_pt"] or None,
                    saga_eng=values["saga_eng"],
                    saga_pt=values["saga_pt"] or None,
                    publisher=values["publisher"],
                    imprint=values["imprint"],
                    date=values["date"],
                    genre=values["genre"],
                    sub_genre=[
                        item.strip()
                        for item in values["sub_genre"].split(",")
                        if item.strip()
                    ],
                    writing=values["writing"],
                    penciling=values["penciling"],
                    inking=values["inking"],
                    colors=values["colors"],
                    letters=values["letters"],
                )
                comic.variations.append(
                    ComicVariation(
                        state=values["state"],
                        price_usd=float(values["price_usd"]),
                        price_brl=float(values["price_brl"]),
                        stock=int(values["stock"]),
                    )
                )
                self.admin_manager.add_comic(comic)
            except (OSError, TypeError, ValueError) as error:
                messagebox.showerror(
                    "Dados inválidos",
                    str(error),
                    parent=dialog,
                )
                return

            dialog.destroy()
            self.show_admin_inventory()

        buttons = ttk.Frame(form)
        buttons.grid(
            row=1 + (len(field_specs) + 1) // 2,
            column=0,
            columnspan=4,
            sticky="e",
            pady=(20, 0),
        )
        ttk.Button(
            buttons,
            text="Cancelar",
            command=dialog.destroy,
        ).pack(side="right", padx=(8, 0))
        ttk.Button(
            buttons,
            text="Salvar quadrinho",
            command=save_comic,
        ).pack(side="right")
        fields["title_eng"].focus_set()

    def show_store(self) -> None:
        self._clear_screen()
        self._make_header()

        menu = ttk.Frame(self.root, padding=24)
        menu.pack(expand=True)

        ttk.Label(
            menu,
            text=f"Olá, {self.current_user.name}",
            font=("Segoe UI", 20, "bold"),
        ).pack(pady=(0, 16))

        ttk.Button(
            menu,
            text="Pesquisar quadrinhos",
            width=28,
            command=self.show_search,
        ).pack(pady=8)

        ttk.Button(
            menu,
            text=f"Abrir carrinho ({len(self.cart)} itens)",
            width=28,
            command=self.show_cart,
        ).pack(pady=8)

        ttk.Button(
            menu,
            text="Sair",
            width=28,
            command=self._logout,
        ).pack(pady=8)

    def show_search(self) -> None:
        self._clear_screen()
        self._make_header()

        page = ttk.Frame(self.root, padding=24)
        page.pack(fill="both", expand=True)

        search_bar = ttk.Frame(page)
        search_bar.pack(fill="x")
        ttk.Label(search_bar, text="Título").pack(side="left")
        search_entry = ttk.Entry(search_bar, width=40)
        search_entry.pack(side="left", padx=8)

        content = ttk.Frame(page)
        content.pack(fill="both", expand=True, pady=16)

        result_list = tk.Listbox(
            content,
            height=18,
            width=60,
            exportselection=False,
        )
        result_list.pack(side="left", fill="y")

        details = ttk.Frame(content, padding=(24, 0, 0, 0))
        details.pack(side="left", fill="both", expand=True)
        info_label = ttk.Label(details, text="Selecione um quadrinho.")
        info_label.pack(anchor="w")

        ttk.Label(details, text="Variação").pack(anchor="w", pady=(16, 4))
        variation_combo = ttk.Combobox(details, state="readonly")
        variation_combo.pack(fill="x")

        ttk.Label(details, text="Quantidade").pack(anchor="w", pady=(12, 4))
        quantity_entry = ttk.Entry(details)
        quantity_entry.insert(0, "1")
        quantity_entry.pack(fill="x")

        catalog = ComicCatalog(self.database.load_comics())
        results: list[Comic] = []
        selected_comic: Comic | None = None

        cart_button = ttk.Button(
            search_bar,
            text=f"Carrinho ({len(self.cart)})",
            command=self.show_cart,
        )
        cart_button.pack(side="right")

        def update_details(_event: tk.Event | None = None) -> None:
            nonlocal selected_comic
            selection = result_list.curselection()
            if not selection:
                selected_comic = None
                return

            selected_comic = results[selection[0]]
            comic = selected_comic
            title = comic.title_pt or comic.title_eng
            info_label.configure(
                text=(
                    f"{title}\n"
                    f"Série: {comic.saga_pt or comic.saga_eng}\n"
                    f"Editora: {comic.publisher} / {comic.imprint}"
                )
            )
            variation_combo["values"] = [
                f"{variation.state} - R$ {variation.price_brl:.2f}"
                for variation in comic.variations
            ]
            if comic.variations:
                variation_combo.current(0)

        def run_search() -> None:
            nonlocal selected_comic
            results.clear()
            result_list.delete(0, tk.END)
            query = search_entry.get().strip()
            matches = catalog.find_by_title(query) if query else catalog.comics

            if not matches:
                selected_comic = None
                info_label.configure(text="Nenhum quadrinho encontrado.")
                variation_combo["values"] = []
                variation_combo.set("")
                return

            results.extend(matches)
            for comic in matches:
                result_list.insert(tk.END, comic.title_pt or comic.title_eng)
            result_list.selection_set(0)
            update_details()

        ttk.Button(search_bar, text="Buscar", command=run_search).pack(
            side="left"
        )
        result_list.bind("<<ListboxSelect>>", update_details)

        def add_to_cart() -> None:
            if selected_comic is None:
                messagebox.showwarning(
                    "Nenhum quadrinho",
                    "Selecione um quadrinho.",
                    parent=self.root,
                )
                return

            try:
                quantity = int(quantity_entry.get())
            except ValueError:
                messagebox.showerror(
                    "Quantidade inválida",
                    "Informe um número inteiro maior que zero.",
                    parent=self.root,
                )
                return

            variation_index = variation_combo.current()
            if (
                variation_index < 0
                or variation_index >= len(selected_comic.variations)
            ):
                messagebox.showwarning(
                    "Nenhuma variação",
                    "Selecione uma variação.",
                    parent=self.root,
                )
                return

            variation = selected_comic.variations[variation_index]
            try:
                self._add_cart_item(selected_comic, variation, quantity)
            except ValueError as error:
                messagebox.showerror(
                    "Não foi possível adicionar",
                    str(error),
                    parent=self.root,
                )
                return

            cart_button.configure(text=f"Carrinho ({len(self.cart)})")

            messagebox.showinfo(
                "Carrinho",
                "Quadrinho adicionado ao carrinho.",
                parent=self.root,
            )

        ttk.Button(
            details,
            text="Adicionar ao carrinho",
            command=add_to_cart,
        ).pack(anchor="w", pady=16)
        ttk.Button(
            details,
            text="Voltar ao menu",
            command=self.show_store,
        ).pack(anchor="w")

        run_search()

    def _add_cart_item(
            self,
            comic: Comic,
            variation: ComicVariation,
            quantity: int,
    ) -> None:
        if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity < 1:
            raise ValueError("A quantidade deve ser um número inteiro maior que zero.")

        cart_quantity = sum(
            item["quantity"]
            for item in self.cart
            if item["comic_title"] == comic.title_eng
            and item["state"] == variation.state
        )
        if cart_quantity + quantity > variation.stock:
            raise ValueError(f"Estoque disponível: {variation.stock}.")

        for item in self.cart:
            if (
                item["comic_title"] == comic.title_eng
                and item["state"] == variation.state
            ):
                item["quantity"] += quantity
                return

        self.cart.append({
            "comic_title": comic.title_eng,
            "title": comic.title_pt or comic.title_eng,
            "state": variation.state,
            "price_brl": variation.price_brl,
            "quantity": quantity,
        })

    def show_cart(self) -> None:
        self._clear_screen()
        self._make_header()

        page = ttk.Frame(self.root, padding=24)
        page.pack(fill="both", expand=True)

        ttk.Label(
            page,
            text="Carrinho",
            font=("Segoe UI", 20, "bold"),
        ).pack(anchor="w")

        cart_list = tk.Listbox(page, height=16)
        cart_list.pack(fill="both", expand=True, pady=12)
        total_label = ttk.Label(page)
        total_label.pack(anchor="w")

        def refresh_cart() -> None:
            cart_list.delete(0, tk.END)
            total = 0.0
            for item in self.cart:
                subtotal = item["price_brl"] * item["quantity"]
                total += subtotal
                cart_list.insert(
                    tk.END,
                    f"{item['title']} - {item['state']} "
                    f"x{item['quantity']} - R$ {subtotal:.2f}",
                )
            total_label.configure(text=f"Total: R$ {total:.2f}")

        def remove_selected() -> None:
            selection = cart_list.curselection()
            if selection:
                del self.cart[selection[0]]
                refresh_cart()

        def finish_purchase() -> None:
            if not self.cart:
                messagebox.showwarning(
                    "Carrinho vazio",
                    "Adicione quadrinhos antes de comprar.",
                    parent=self.root,
                )
                return

            try:
                comics = self.database.load_comics()
                for item in self.cart:
                    comic = next(
                        (
                            candidate
                            for candidate in comics
                            if candidate.title_eng == item["comic_title"]
                        ),
                        None,
                    )
                    if comic is None:
                        raise ValueError("Um quadrinho do carrinho não existe mais.")

                    variation = next(
                        (
                            candidate
                            for candidate in comic.variations
                            if candidate.state == item["state"]
                        ),
                        None,
                    )
                    if variation is None:
                        raise ValueError("Uma variação do carrinho não existe mais.")
                    if item["quantity"] > variation.stock:
                        raise ValueError(
                            f"Estoque insuficiente para {item['title']} "
                            f"({item['state']})."
                        )

                for item in self.cart:
                    comic = next(
                        candidate
                        for candidate in comics
                        if candidate.title_eng == item["comic_title"]
                    )
                    variation = next(
                        candidate
                        for candidate in comic.variations
                        if candidate.state == item["state"]
                    )
                    variation.adjust_stock(-item["quantity"])

                self.database.save_comics(comics)
                self.cart.clear()
                refresh_cart()
                messagebox.showinfo(
                    "Compra finalizada",
                    "Compra realizada com sucesso.",
                    parent=self.root,
                )
            except (OSError, ValueError) as error:
                messagebox.showerror(
                    "Não foi possível finalizar",
                    str(error),
                    parent=self.root,
                )

        buttons = ttk.Frame(page)
        buttons.pack(fill="x")
        ttk.Button(
            buttons,
            text="Remover selecionado",
            command=remove_selected,
        ).pack(side="left")
        ttk.Button(
            buttons,
            text="Finalizar compra",
            command=finish_purchase,
        ).pack(side="left", padx=8)
        ttk.Button(
            buttons,
            text="Voltar ao menu",
            command=self.show_store,
        ).pack(side="left")

        refresh_cart()

    def _logout(self) -> None:
        self.current_user = None
        self.admin_manager = None
        self.cart.clear()
        self.show_welcome()
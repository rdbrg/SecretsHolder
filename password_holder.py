import tkinter as tk
import tkinter.ttk as ttk
from variables import *
import sqlite3
import string
import secrets
import copypaste
from cryptography.fernet import Fernet


class EntryPin(tk.Toplevel):
    """This class to make visible entry PIN window"""
    def __init__(self, master):
        tk.Toplevel.__init__(self, master)
        tk.Toplevel.title(self, "Entry PIN")
        w = 300
        h = 150
        w_src = self.winfo_screenwidth() // 2
        h_src = self.winfo_screenheight() // 2
        tk.Toplevel.geometry(self, f"+{w_src - w // 2}+{h_src - h // 2}")
        tk.Toplevel.resizable(self, False, False)

        self.init_widgets()

    def init_widgets(self):
        """Initialization widgets"""
        self.frame = ttk.Frame(self)
        self.frame.pack(padx=X, pady=Y, fill=tk.BOTH, expand=True)

        self.entry_pin = ttk.Entry(self.frame, show="*", width=40)
        self.entry_pin.pack(fill=tk.X, pady=Y)

        bottom_frame = ttk.Frame(self.frame)
        bottom_frame.pack(fill=tk.BOTH)

        button_ok = ttk.Button(bottom_frame, text="Ok", width=20, command=self.check_pin, style="PinButton.TLabel")
        button_ok.pack(side=tk.LEFT, pady=Y)
        self.bind('<Return>', lambda event: self.check_pin())

        self.status_tuple = ("Lock", "Incorrect")
        self.label_status = ttk.Label(bottom_frame, text=self.status_tuple[0], foreground=GRAY)
        self.label_status.pack(side=tk.RIGHT)

        self.grab_set()
        self.focus_set()
        print("Init EnterPin")

    def call_tree_view_and_destroy(self):
        """Метод делает видимым корневое окно Tk()"""
        self.master.deiconify()
        self.destroy()

    def check_pin(self):
        """Функция проверки ПИН-кода"""
        if self.entry_pin.get() == "awd":
            self.call_tree_view_and_destroy()
        else:
            self.label_status.configure(text=self.status_tuple[1], foreground=RED)
            self.label_status.after(1000, lambda: self.label_status.configure(text=self.status_tuple[0],
                                                                              foreground=GRAY))
            self.entry_pin.delete(0, 'end')


class TreeViewWindow(ttk.Frame):
    """
    Класс главного корневого окна Tk().
    В этом классе находятся основные методы по работе с базой данных SLQ.
    """
    def __init__(self, master):
        """Ининциализация метода конструктора класса"""
        super().__init__(master)
        self.master = master
        self.master.title("Accounts")
        self.master.iconbitmap(default=r"D:\YandexDisk\password_holder\resources\icon.ico")

        w = 240
        h = 600
        w_src = self.winfo_screenwidth() // 2
        h_src = self.winfo_screenheight() // 2
        self.master.geometry(f"{w}x{h}+{w_src - w // 2}+{h_src - h // 2}")
        self.master.resizable(False, False)

        self.db = db
        self.init_widgets()
        self.view_records()

    def init_widgets(self):
        """Ининциализация виджетов класса"""
        frame = ttk.Frame(self)
        frame.pack(padx=X, pady=Y, expand=True, fill=tk.X)

        btn_add_account = ttk.Button(frame, text="Add Account", command=self.call_add_account, style='PinButton.TLabel')
        btn_add_account.pack(pady=X, fill=tk.X)

        columns = ('id', 'account')
        self.tree = ttk.Treeview(frame, column=columns, height=30, show='headings')

        for col in columns:
            self.tree.heading(col, text=col,
                              command=lambda _col=col: self.tree_view_sort_column(self.tree, _col, False))

        self.tree.column('id', width=40, minwidth=40, stretch=tk.NO)
        self.tree.column('account', width=188, minwidth=188, stretch=tk.NO)
        self.tree.heading('id', text="№")
        self.tree.heading('account', text="Accounts")

        self.master.bind('<Button-3>', self.show_right_click_menu)

        self.tree.pack(fill=tk.X)

    def records(self, name, login, password, entry_add_list):
        """Метод записывает данные в базу данных"""
        self.db.insert_data(name.title(), login, password)

        for j in entry_add_list[:3]:
            j.delete(0, tk.END)

        self.view_records()

    def edit_record(self, name, login, password):
        """Метод осуществляет перезапись уже имеющихся данных"""
        self.db.encrypted_login = self.db.cipher.encrypt(bytes(login, encoding='utf-8'))
        self.db.encrypted_password = self.db.cipher.encrypt(bytes(password, encoding='utf-8'))

        self.db.c.execute("""UPDATE data_account SET d_name=?, d_login=?, d_password=? WHERE d_id=?""",
                          (name.title(),
                           self.db.encrypted_login,
                           self.db.encrypted_password,
                           self.tree.set(self.tree.selection()[0], '#1')))

        self.db.conn.commit()
        self.view_records()

    def delete_record(self):
        """Метод удаляет данные из базы данных"""
        for _ in self.tree.selection():
            self.db.c.execute("""DELETE FROM data_account WHERE d_id=?""",
                              [self.tree.set(self.tree.selection()[0], '#1')])

        self.db.conn.commit()
        self.view_records()

    def call_edit_account(self):
        """Метод вызывает класс редактирования данных"""
        EditAccount(root)

    def view_records(self):
        """Метод отображает записи из базы данных в виджете TreeView"""
        self.db.c.execute("""SELECT * FROM data_account""")
        [self.tree.delete(i) for i in self.tree.get_children()]
        [self.tree.insert("", tk.END, value=row) for row in self.db.c.fetchall()]

    def call_add_account(self):
        """Метод вызывает класс добавления данных в базу данных"""
        AddAccounts(self.master)

    def show_right_click_menu(self, event):
        """Метод создает и вызывает контекстное меню по правому клику мыши"""
        names_menu = ("Copy login", "Copy password", "Edit", "Delete")
        right_click_menu_commands = [self.copy_login,
                                     self.copy_password,
                                     self.call_edit_account,
                                     self.delete_record]

        menu = tk.Menu(self, tearoff=0)
        for count, item in enumerate(names_menu):
            if count == 2:
                menu.add_separator()
            menu.add_command(label=item, command=right_click_menu_commands[count])
        iid = self.tree.identify_row(event.y)
        if iid:
            self.tree.selection_set(iid)
            menu.post(event.x_root, event.y_root)
        menu.focus_set()

    def copy_login(self):
        """Метод копирует логин из базы данных"""
        for _ in self.tree.selection():
            self.db.c.execute("""SELECT d_login FROM data_account WHERE d_id=?""",
                              [self.tree.set(self.tree.selection()[0], '#1')])
        for login in self.db.c.fetchone():
            output = self.db.cipher.decrypt(login)
            copypaste.copy(str(output.decode('utf-8')))

    def copy_password(self):
        """Метод копирует пароль из базы данных"""
        for _ in self.tree.selection():
            self.db.c.execute("""SELECT d_password FROM data_account WHERE d_id=?""",
                              [self.tree.set(self.tree.selection()[0], '#1')])

        for password in self.db.c.fetchone():
            output = self.db.cipher.decrypt(password)
            copypaste.copy(str(output.decode('utf-8')))

    def tree_view_sort_column(self, tv, col, reverse):
        """
        Метод делает возможным сортировать колонки в виджете TreeView
        при нажатии на заголовки колонок
        """
        column_sorted = [(tv.set(k, col), k) for k in tv.get_children('')]
        column_sorted.sort(reverse=reverse)

        for index, (val, k) in enumerate(column_sorted):
            tv.move(k, '', index)

        tv.heading(col, text=col, command=lambda _col=col: self.tree_view_sort_column(tv, _col, not reverse))


class AddAccounts(tk.Toplevel):
    """Класс окна добавления данных в базу данных"""
    def __init__(self, master):
        """Инициализация окна"""
        tk.Toplevel.__init__(self, master)
        w = 240
        h = 380
        w_src = self.winfo_screenwidth() // 2
        h_src = self.winfo_screenheight() // 2
        tk.Toplevel.geometry(self, f"+{w_src - w // 2}+{h_src - h // 2}")
        tk.Toplevel.title(self, "Add Account")
        tk.Toplevel.resizable(self, False, False)

        self.db = db
        self.app = app
        self.init_widgets_add()
        self.grab_set()
        self.focus_set()

    def init_widgets_add(self):
        """Инициализация виджетов класса"""
        frame = ttk.Frame(self)
        frame.pack(padx=X, pady=Y, expand=True, fill=tk.X)

        self.labels = ("Name", "Login/Email", "Password")
        self.entry_list = []
        self.label_frame_list = []

        """Create labels name and Entry field"""
        for item, name in enumerate(self.labels):
            label_frame = ttk.Labelframe(frame, text=name)
            if item == 2:
                entry = ttk.Entry(label_frame, show="*")
            else:
                entry = ttk.Entry(label_frame)
            entry.pack(padx=X, fill=tk.X)
            label_frame.pack(pady=Y, fill=tk.X)
            self.check_button = ttk.Checkbutton(label_frame, text="Show Password (not recommended)",
                                                command=lambda: self.show_hide_pass_pin())
            self.check_button.state(['!alternate'])
            self.entry_list.append(entry)
            self.label_frame_list.append(label_frame)
        self.check_button.pack(padx=X, pady=Y, anchor=tk.W)
        """Common frame for Length and Type label-frames"""
        common_frame_length_type = ttk.Frame(frame)
        common_frame_length_type.pack(pady=Y)
        """Display password length"""
        rb_frame_length = ttk.Labelframe(common_frame_length_type, text="Length")
        rb_frame_length.pack(side=tk.LEFT, fill=tk.X)
        self.rb_length = tk.IntVar()
        self.rb_length.set(24)
        self.name_rb_list = ("4", "6", "12", "24")
        self.radiobutton_length_list = []
        for item in self.name_rb_list:
            rb = ttk.Radiobutton(rb_frame_length,
                                 text=item,
                                 variable=self.rb_length,
                                 value=int(item))
            rb.pack(padx=X, pady=Y, anchor=tk.W)
            self.radiobutton_length_list.append(rb)
        """Display types password"""
        rb_frame_type = ttk.Labelframe(common_frame_length_type, text="Type")
        rb_frame_type.pack(side=tk.LEFT, fill=tk.X)
        self.rb_type = tk.StringVar()
        self.charset_variation_list = (string.digits,
                                       string.ascii_letters,
                                       string.digits + string.ascii_letters,
                                       string.digits + string.ascii_letters + string.punctuation)
        self.name_rb_type_list = ("numbers", "letters", "numbers + letters", "numbers + letters + punct")
        self.rb_type.set(self.charset_variation_list[3])
        self.radiobutton_type_list = []
        for count, item in enumerate(self.name_rb_type_list):
            rb = ttk.Radiobutton(rb_frame_type,
                                 text=item,
                                 variable=self.rb_type,
                                 value=self.charset_variation_list[count])
            rb.pack(padx=X, pady=Y, anchor=tk.W)
            self.radiobutton_type_list.append(rb)
        """Display buttons"""
        self.name_buttons = ["Generate", "Add"]
        buttons_command = [lambda: self.generate_password(),
                           lambda: self.records_and_destroy()]
        self.bind('<Return>', lambda event: self.records_and_destroy())
        buttons_frame = ttk.Frame(frame)
        buttons_frame.pack(fill=tk.X, expand=True)
        self.button_list = []
        for count, item in enumerate(self.name_buttons):
            if count == 1:
                btn = ttk.Button(buttons_frame,
                                 text=item,
                                 command=buttons_command[count],
                                 style="PinButton.TLabel")
            else:
                btn = ttk.Button(buttons_frame, padding=3,
                                 text=item,
                                 command=buttons_command[count])
            btn.pack(side=tk.LEFT, pady=Y, fill=tk.X, expand=True)
            self.button_list.append(btn)

    def show_hide_pass_pin(self):
        """Метод реализует отображение пароля"""
        if self.check_button.instate(['!selected']):
            self.entry_list[2].configure(show="*")
        else:
            self.entry_list[2].configure(show="")

    def generate_password(self):
        """Метод генерирует пароль"""
        self.entry_list[2].delete(0, tk.END)
        password = ''.join(secrets.choice(self.rb_type.get()) for i in range(self.rb_length.get()))
        self.entry_list[2].insert(0, password)

    def records_and_destroy(self):
        """
        Метод забирает данные из поля ввода графического интерфейса и/или
        сообщает об отсутствии ввода в поле.
        """
        if self.entry_list[0].get() == "":
            self.entry_list[0].configure(style='RedLabel.TLabel')
            self.entry_list[0].after(1000, lambda: self.entry_list[0].configure(style='WhiteLabel.TLabel'))
        if self.entry_list[1].get() == "":
            self.entry_list[1].configure(style='RedLabel.TLabel')
            self.entry_list[1].after(1000, lambda: self.entry_list[1].configure(style='WhiteLabel.TLabel'))
        if self.entry_list[2].get() == "":
            self.entry_list[2].configure(style='RedLabel.TLabel')
            self.entry_list[2].after(1000, lambda: self.entry_list[2].configure(style='WhiteLabel.TLabel'))
        if self.entry_list[0].get() != "" and self.entry_list[1].get() != "" and self.entry_list[2].get() != "":
            self.app.records(self.entry_list[0].get(),
                             self.entry_list[1].get(),
                             self.entry_list[2].get(),
                             self.entry_list)
            self.destroy()


class EditAccount(AddAccounts):
    """
    Класс внесения изменений данных в базу данных.
    Наследуется от класса добавления данных.
    """
    def __init__(self, master):
        """Инициализация окна"""
        super().__init__(master)
        tk.Toplevel.title(self, "Edit Account")

        self.button_list[1].configure(text="Save", command=self.init_edit)
        self.bind('<Return>', lambda e: self.init_edit())
        self.entry_insert()

    def init_edit(self):
        """Метод забирает из полей ввода новые данны"""
        self.app.edit_record(self.entry_list[0].get(),
                             self.entry_list[1].get(),
                             self.entry_list[2].get())
        self.destroy()

    def entry_insert(self):
        """
        Метод вставляет данные из базы данных в соответствуйющие
        поля при редактировании данных
        """
        self.db.c.execute("""SELECT * FROM data_account WHERE d_id=?""", [
            self.app.tree.set(self.app.tree.selection()[0], '#1')])
        records = self.db.c.fetchall()

        for record in records:
            self.entry_list[0].insert(0, record[1])
            self.entry_list[1].insert(0, record[2])
            self.entry_list[2].insert(0, record[3])
            break


class Style:
    """Класс графических стилей виджетов"""
    def __init__(self):
        """Инициализация класса"""
        stl_button = ttk.Style()
        stl_button.configure('PinButton.TLabel', foreground=WHITE, background=BLUE,
                             anchor=tk.CENTER, padding=4)
        stl_button.map('PinButton.TLabel',
                       foreground=[('pressed', WHITE), ('active', WHITE)],
                       background=[('pressed', '!disabled', GRAY), ('active', BLUE_LIGHT)])
        stl_text_empty_entry = ttk.Style()
        stl_text_empty_entry.configure('RedLabel.TLabel', background=RED)
        stl_text_entry = ttk.Style()
        stl_text_entry.configure('WhiteLabel.TLabel', background=WHITE)


class DataBase:
    """Класс базы данных"""
    def __init__(self):
        """Инициализация базы данных"""
        self.conn = sqlite3.connect("mat4astb.db")
        self.c = self.conn.cursor()
        self.c.execute("""CREATE TABLE IF NOT EXISTS data_account (
        d_id integer primary key,
        d_name text,
        d_login text,
        d_password text
        )""")
        self.conn.commit()

        self.key = b'sw2cKTWWK-o0PpanMPrmpE3Zud-3KTgmAlao5pkxQnY='
        self.cipher = Fernet(self.key)

    def insert_data(self, name, login, password):
        """Метод вносит данные в таблицы базы данных"""
        self.encrypted_login = self.cipher.encrypt(bytes(login, encoding='utf-8'))
        self.encrypted_password = self.cipher.encrypt(bytes(password, encoding='utf-8'))

        self.c.execute("""INSERT INTO data_account (
        "d_name",
        "d_login",
        "d_password"
        ) VALUES (?, ?, ?)""", (name, self.encrypted_login, self.encrypted_password))

        self.conn.commit()


if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    db = DataBase()
    stl = Style()
    app = TreeViewWindow(root)
    app.pack(expand=True, fill=tk.BOTH)
    check_pin = EntryPin(root)
    root.mainloop()

import tkinter as tk
import tkinter.ttk as ttk
import sqlite3
import copypaste
import re
import sys
import os


TEN = 10


class SecurityWindow(tk.Tk):

    def __init__(self):
        tk.Tk.__init__(self)
        tk.Tk.title(self, "Enter symbols")
        w_src = self.winfo_screenwidth()
        h_src = self.winfo_screenheight()
        geometry = f'+{w_src // 2 - 300 // 2}+{h_src // 2 - 200 // 2}'
        tk.Tk.geometry(self, geometry)
        # tk.Tk.iconbitmap(self, default=r'D:\top_secret\YandexDisk\SecretsHolder\icon\key.ico')
        tk.Tk.resizable(self, False, False)
        self.db = db_main
        self.init_security_window()

    def init_security_window(self):
        def check_password():
            def change_set(label_status):
                label_status.after(1000, lambda: label_status.configure(text=self.status_list[0], foreground='gray'))
                self.entry_security_window.delete(0, 'end')

            if self.entry_security_window.get() == password:

                self.destroy()
                global app_main_page
                app_main_page = MainPage()

            elif self.entry_security_window.get() == "setpassword":
                if password == "":
                    SetPassword()
                    self.destroy()
                else:
                    print("Pass уже установлен")
            else:
                self.label_status.configure(text=self.status_list[1], foreground='red')
                change_set(self.label_status)

        main_frame = tk.Frame()
        main_frame.pack(side=tk.TOP, padx=TEN, pady=TEN // 2)

        self.entry_security_window = ttk.Entry(main_frame, show="*", width=50)
        self.entry_security_window.pack(pady=TEN // 2)

        second_frame = tk.Frame(main_frame)
        second_frame.pack(fill=tk.BOTH)

        self.button = ttk.Button(second_frame, text="Ok", command=check_password, width=20)
        self.button.pack(side=tk.LEFT, anchor=tk.W, pady=TEN // 2)
        self.bind('<Return>', lambda event: check_password())

        self.status_list = ["Lock", "Wrong"]
        self.label_status = ttk.Label(second_frame, text=self.status_list[0], foreground='gray')
        self.label_status.pack(side=tk.RIGHT)


class MainPage(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        tk.Tk.title(self, "Secure your data")
        w_src = self.winfo_screenwidth()
        h_src = self.winfo_screenheight()
        geometry = f'{500}x{700}+{w_src // 2 - 500 // 2}+{h_src // 2 - 700 // 2}'
        tk.Tk.geometry(self, geometry)
        # tk.Tk.iconbitmap(self, default=r'D:\top_secret\YandexDisk\SecretsHolder\icon\key.ico')
        tk.Tk.resizable(self, False, False)
        self.init_main_page()
        self.db = db_main
        self.view_records()

    def init_main_page(self):
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.X, padx=TEN, pady=TEN)

        buttons_bar = tk.Frame(main_frame)
        buttons_bar.pack(fill=tk.X)

        button_add = ttk.Button(buttons_bar, text="Add data", padding=10, command=self.open_add_data_dialog)
        button_add.pack(side=tk.LEFT, fill=tk.X, expand=True)

        data_frame = tk.Frame(main_frame)
        data_frame.pack(side=tk.LEFT)

        self.tree = ttk.Treeview(data_frame, column=("d_id", "d_name"), height=40, show='headings')  # tree

        self.tree.column("d_id", width=40)
        self.tree.column("d_name", width=435)

        self.tree.heading("d_id", text="№", anchor=tk.W)
        self.tree.heading("d_name", text="Name", anchor=tk.W)
        self.tree.bind("<Button-3>", self.show_button_3_menu)
        self.tree.pack(fill=tk.BOTH, expand=True)

    def show_button_3_menu(self, event):
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="Copy login", command=self.copy_login)
        self.menu.add_command(label="Copy password", command=self.copy_password)
        self.menu.add_separator()
        self.menu.add_command(label="Edit", command=self.open_edit_dialog)
        self.menu.add_command(label="Delete", command=self.delete_data)

        iid = self.tree.identify_row(event.y)
        if iid:
            self.tree.selection_set(iid)
            self.menu.post(event.x_root, event.y_root)

    def records(self, name, login, passwd, tel, address, note, entry_add_list):
        self.db.insert_data(name, login, passwd, tel, address, note)

        for j in entry_add_list[:5]:
            j.delete(0, 'end')
        entry_add_list[5].delete('1.0', 'end')

        self.view_records()

    def view_records(self):
        self.db.c.execute("""SELECT * FROM data_table""")
        [self.tree.delete(i) for i in self.tree.get_children()]
        [self.tree.insert('', 'end', value=row) for row in self.db.c.fetchall()]

    def edit_record(self, name, login, passwd, tel, address, note):
        self.db.c.execute("""UPDATE data_table SET
        d_name=?, d_login=?, d_password=?, d_tel=?, d_address=?, d_note=? WHERE d_id=?""",
                          (name, login, passwd, tel, address, note, self.tree.set(self.tree.selection()[0], '#1')))
        self.db.conn.commit()
        self.view_records()

    def delete_data(self):
        ConfirmPin(DeleteData)

    def copy_login(self):
        for selection_item in self.tree.selection():
            self.db.c.execute("""SELECT d_login FROM data_table WHERE d_id=?""",
                              (self.tree.set(self.tree.selection()[0], '#1')))

        for login in self.db.c.fetchone():
            copypaste.copy(str(login))

    def copy_password(self):
        for selection_item in self.tree.selection():
            self.db.c.execute("""SELECT d_password FROM data_table WHERE d_id=?""",
                              (self.tree.set(self.tree.selection()[0], '#1')))

        for cp in self.db.c.fetchone():
            copypaste.copy(str(cp))

    def open_add_data_dialog(self):
        Child()

    def open_edit_dialog(self):
        ConfirmPin(EditData)


class Child(tk.Toplevel):
    def __init__(self):
        super().__init__(app_main_page)
        self.title("Add data")
        w_src = self.winfo_screenwidth()
        h_src = self.winfo_screenheight()
        geometry = f'{430}x{450}+{w_src // 2 - 430 // 2}+{h_src // 2 - 450 // 2}'
        self.geometry(geometry)
        # self.iconbitmap(default=r'D:\top_secret\YandexDisk\SecretsHolder\icon\key.ico')
        self.resizable(False, False)
        self.init_add_data()
        self.db = db_main
        self.view = app_main_page

    def init_add_data(self):

        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, padx=TEN, pady=TEN)

        self.names_label_list = ["Name", "Login", "Password", "Telephone", "Address", "Note"]
        self.entry_add_list = []

        for i in self.names_label_list:
            self.frame_lab_ent = tk.Frame(self.main_frame)
            self.frame_lab_ent.pack(pady=TEN, fill=tk.X)

            lab = ttk.Label(self.frame_lab_ent, text=i)
            lab.pack(side=tk.LEFT)

            if i == "Password":
                self.entry = ttk.Entry(self.frame_lab_ent, width=50, show="*")
                self.entry.pack(side=tk.RIGHT, padx=TEN)
                self.entry_add_list.append(self.entry)
                continue
            elif i == "Note":
                self.entry_t = tk.Text(self.frame_lab_ent, wrap=tk.WORD, relief=tk.SUNKEN, width=38, height=7)
                self.entry_t.pack(side=tk.RIGHT, padx=TEN)
                self.entry_add_list.append(self.entry_t)
                continue

            self.entry = ttk.Entry(self.frame_lab_ent, width=50, font='TkDefaultFont')
            self.entry.pack(side=tk.RIGHT, padx=TEN)
            self.entry_add_list.append(self.entry)

        button_frame = tk.Frame(self, bg='white')
        button_frame.pack(fill=tk.BOTH, expand=True)
        self.toolbar = tk.Frame(button_frame)
        self.toolbar.pack(side=tk.RIGHT, pady=TEN, padx=TEN * 2)

        def add_command():
            self.view.records(self.entry_add_list[0].get(),
                              self.entry_add_list[1].get(),
                              self.entry_add_list[2].get(),
                              self.entry_add_list[3].get(),
                              self.entry_add_list[4].get(),
                              self.entry_add_list[5].get("1.0", 'end'),
                              self.entry_add_list)

        self.button_plus = ttk.Button(self.toolbar, text="Add", width=15, command=lambda: add_command())
        self.button_plus.pack(side=tk.LEFT, padx=TEN)
        self.bind('<Return>', lambda event: add_command())

        self.button_cancel = ttk.Button(self.toolbar, text="Cancel", width=15, command=lambda: self.destroy())
        self.button_cancel.pack(side=tk.RIGHT)

        self.grab_set()
        self.focus_set()


class EditData(Child):
    def __init__(self):
        super().__init__()
        self.title("Edit data")
        # self.iconbitmap(self, default=r'D:\top_secret\YandexDisk\SecretsHolder\icon\key.ico')
        self.app_main = app_main_page
        self.init_edit()
        self.entry_insert()

    def init_edit(self):

        def update_and_close(*args):
            self.view.edit_record(self.entry_add_list[0].get(),
                                  self.entry_add_list[1].get(),
                                  self.entry_add_list[2].get(),
                                  self.entry_add_list[3].get(),
                                  self.entry_add_list[4].get(),
                                  self.entry_add_list[5].get("1.0", 'end'))
            self.destroy()

        button_edit = ttk.Button(self.toolbar, text="Save", width=15)
        button_edit.pack(side=tk.LEFT, padx=TEN)
        button_edit.bind('<Button-1>', update_and_close)
        self.bind('<Return>', lambda event: update_and_close())

        self.button_plus.destroy()

    def entry_insert(self):
        self.db.c.execute("""SELECT * FROM data_table WHERE d_id=?""",
                          self.app_main.tree.set(self.app_main.tree.selection()[0], '#1'))
        records = self.db.c.fetchall()

        for record in records:
            self.entry_add_list[0].insert(0, record[1])
            self.entry_add_list[1].insert(0, record[2])
            self.entry_add_list[2].insert(0, record[3])
            self.entry_add_list[3].insert(0, record[4])
            self.entry_add_list[4].insert(0, record[5])
            self.entry_add_list[5].insert('1.0', record[6])
            break


class DeleteData:
    def __init__(self):
        self.db = db_main
        self.app_main = app_main_page
        self.init_delete()

    def init_delete(self):

        for selection_item in self.app_main.tree.selection():
            self.db.c.execute("""DELETE FROM data_table WHERE d_id=?""",
                              (self.app_main.tree.set(self.app_main.tree.selection()[0], '#1')))
            self.db.conn.commit()

        self.app_main.view_records()


class SetPassword(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Set password")
        w_src = self.winfo_screenwidth()
        h_src = self.winfo_screenheight()
        geometry = f'+{w_src // 2 - 300 // 2}+{h_src // 2 - 400 // 2}'
        # self.iconbitmap(default=r'D:\top_secret\YandexDisk\SecretsHolder\icon\key.ico')

        self.geometry(geometry)
        self.app_main = app_main_page
        self.init_set_password()

    def init_set_password(self):

        main_frame = tk.Frame(self, bg='white')
        main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=TEN, pady=TEN // 2)

        password_frame_global = tk.LabelFrame(main_frame, text="Password")
        password_frame_global.pack()

        password_frame = tk.Frame(password_frame_global)
        password_frame.pack(padx=TEN, pady=TEN)

        self.label_new_password = ttk.Label(password_frame, text="Enter new password")
        self.label_new_password.grid(row=0, column=0, sticky=tk.W)
        self.entry_setpassword = ttk.Entry(password_frame, show="*", width=50)
        self.entry_setpassword.grid(row=1, column=0, sticky=tk.W)

        self.label_new_password_confirm = ttk.Label(password_frame, text="Confirm password")
        self.label_new_password_confirm.grid(row=2, column=0, sticky=tk.W)
        self.entry_setpassword_confirm = ttk.Entry(password_frame, show="*", width=50)
        self.entry_setpassword_confirm.grid(row=3, column=0, sticky=tk.W)

        self.show_password = ttk.Checkbutton(password_frame, text="Show password",
                                             command=lambda: self.show_hide_pass_pin(self.show_password,
                                                                                     self.entry_setpassword,
                                                                                     self.entry_setpassword_confirm))
        self.show_password.grid(row=4, column=0, sticky=tk.W)
        self.show_password.state(['!alternate'])

        pin_frame_global = tk.LabelFrame(main_frame, text="Pin code")
        pin_frame_global.pack()

        pin_frame = tk.Frame(pin_frame_global)
        pin_frame.pack(padx=TEN, pady=TEN)

        self.label_new_pin = ttk.Label(pin_frame, text="Enter new PIN")
        self.label_new_pin.grid(row=0, column=0, sticky=tk.W)
        self.entry_pin = ttk.Entry(pin_frame, show="*", width=50)
        self.entry_pin.grid(row=1, column=0, sticky=tk.W)

        self.label_new_pin_confirm = ttk.Label(pin_frame, text="Confirm PIN")
        self.label_new_pin_confirm.grid(row=2, column=0, sticky=tk.W)
        self.entry_pin_confirm = ttk.Entry(pin_frame, show="*", width=50)
        self.entry_pin_confirm.grid(row=3, column=0, sticky=tk.W)

        self.show_pin = ttk.Checkbutton(pin_frame, text="Show pin",
                                        command=lambda: self.show_hide_pass_pin(self.show_pin,
                                                                                self.entry_pin,
                                                                                self.entry_pin_confirm))
        self.show_pin.grid(row=4, column=0, sticky=tk.W)
        self.show_pin.state(['!alternate'])

        self.button = ttk.Button(main_frame, text="Save", command=self.check_password_pin, width=20)
        self.button.pack(side=tk.RIGHT, anchor=tk.W, pady=TEN // 2)
        self.bind('<Return>', lambda event: self.check_password_pin())
        self.button.bind('<Button-1>')

        self.label_status = ttk.Label(main_frame, text="")
        self.label_status.pack(side=tk.LEFT)

    def show_hide_pass_pin(self, checkbutton, entry, entry_confirm):
        if checkbutton.instate(['!selected']):
            entry.configure(show='*')
            entry_confirm.configure(show='*')
        else:
            entry.configure(show='')
            entry_confirm.configure(show='')

    def check_password_pin(self):
        if self.entry_setpassword.get() == "" or \
                len(self.entry_setpassword.get().split()) != 1 or \
                5 >= len(self.entry_setpassword.get()) > 30 or \
 \
                re.findall(f'\D', self.entry_pin.get()) or \
                len(self.entry_pin.get()) != 4:
            self.label_status.configure(text="Enter error", foreground='red', background='white')
            self.label_status.after(3000, lambda: self.label_status.configure(text=""))

        elif self.entry_setpassword.get() != self.entry_setpassword_confirm.get() or \
                self.entry_pin.get() != self.entry_pin_confirm.get():
            self.label_status.configure(text="Password or pin do not match", foreground='red', background='white')
            self.label_status.after(3000, lambda: self.label_status.configure(text=""))

        else:
            self.db = db_main

            self.db.c.execute("""INSERT INTO pass_keeper (
            "password",
            "pin") VALUES (?, ?)""", (self.entry_setpassword.get(), self.entry_pin.get()))
            self.db.conn.commit()
            self.destroy()

            app = sys.executable
            os.execl(app, app, *sys.argv)


class ConfirmPin(SecurityWindow):
    def __init__(self, class_fade_in):
        super().__init__()
        self.class_fade_in = class_fade_in
        self.title("Confirm PIN")
        self.init_confirm_pin()

    def init_confirm_pin(self):
        def check_pin():
            def change_set(label_status):
                label_status.after(1000, lambda: label_status.configure(text=self.status_list[0], foreground='gray'))
                self.entry_pin.delete(0, 'end')

            if str(self.entry_pin.get()) == str(pin):
                self.destroy()
                self.class_fade_in()
            else:
                self.label_status.configure(text=self.status_list[1], foreground='red')
                change_set(self.label_status)

        main_frame = tk.Frame(self)
        main_frame.pack(padx=TEN, pady=TEN)

        label_enter_pin = ttk.Label(main_frame, text="Confirm action. Enter your PIN.")
        label_enter_pin.grid(row=0, column=0, sticky=tk.W)

        self.entry_pin = ttk.Entry(main_frame, width=50, show="*")
        self.entry_pin.grid(row=1, column=0, sticky=tk.W, pady=TEN)

        button = ttk.Button(main_frame, text="Confirm", command=check_pin, width=20)
        button.grid(row=3, column=0, sticky=tk.W)
        self.bind('<Return>', lambda event: check_pin())

        self.label_status = ttk.Label(main_frame, text=self.status_list[0], foreground='gray')
        self.label_status.grid(row=3, column=0, sticky=tk.E)

        self.grab_set()
        self.focus_set()

    def view_pin_in_db(self):
        self.db.c.execute("""SELECT pin FROM pass_keeper""")
        for rp in self.db.c.fetchall():
            print(rp[0])
            global pin
            rp[0] = pin


class DataBase:

    def __init__(self):
        self.conn = sqlite3.connect("test.db")
        self.c = self.conn.cursor()

        self.c.execute("""CREATE TABLE IF NOT EXISTS data_table (
        d_id integer primary key,
        d_name text,
        d_login text,
        d_password text,
        d_tel text,
        d_address text,
        d_note text
        )""")
        self.c.execute("""CREATE TABLE IF NOT EXISTS pass_keeper (
        password text, pin integer)""")

        self.conn.commit()

    def insert_data(self, name, login, passwd, tel, address, note):
        self.c.execute("""INSERT INTO data_table (
        "d_name",
        "d_login",
        "d_password",
        "d_tel",
        "d_address",
        "d_note") VALUES (?, ?, ?, ?, ?, ?)""", (name, login, passwd, tel, address, note))

        self.conn.commit()


if __name__ == '__main__':
    password = ""
    db_main = DataBase()

    db_main.c.execute("""SELECT password FROM pass_keeper""")
    for rec in db_main.c.fetchall():
        password = rec[0]

    pin = ""
    db_main.c.execute("""SELECT pin FROM pass_keeper""")
    for rec in db_main.c.fetchall():
        pin = rec[0]

    app_main_page = None
    app_security_window = SecurityWindow()
    app_security_window.mainloop()

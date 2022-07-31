import tkinter as tk
from tkinter import StringVar, messagebox
from tkinter.ttk import Separator
from typing import Any, Callable


class App(tk.Tk):
    PORTS: int = 4
    STATUS: dict = {
        'Emulator': 'Not Found',
        'Game ROM': 'Unknown',
    }
    TITLE: str = 'Stream Tool (Beta)'
    UNIT: int = 8

    def __init__(self, app_config: dict,
                 emulator: Any,
                 poll: Callable[[Any], bool],
                 update: Callable[[int, str], bool]):
        super().__init__()
        self.app_config = app_config
        self.poll_callback = poll
        self.emulator = emulator
        self.update_callback = update
        self.row_index = 0
        self.variables: dict[StringVar] = {}

        self.title(self.TITLE)
        self.resizable(False, False)
        self.config(menu=self.menu())
        self.bind_all("<Control-q>", self.quit_app)

        self.window = tk.Frame(self, padx=self.UNIT, pady=self.UNIT)
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        self.header('Player Names')
        for port in range(self.PORTS):
            self.editor(port, f"Player {port+1}", None)

        self.header('Status')
        for key, value in self.STATUS.items():
            self.status(key, value)

        self.window.grid(row=0, column=0)
        self.poll_loop(1000)

    def about_app(self):
        message = (
            f'This is an experimental tool for Smash Remix 1.2.0+.\n\n'
            f'This will only change the name of tags on your emulator.\n\n'
            f"It's unknown if this causes desyncs. Your mileage may vary.\n\n"
            f'CEnnis91 © 2022'
        )
        messagebox.showinfo(title="Stream Tool (Beta)", message=message)

    def editor(self, port: int, key: str, row: int = None):
        self.variables[key] = StringVar(value='')
        field = self.variables[key]
        row = self.row_index if row is None else row
        self.row_index = row + 1

        label = tk.Label(self.window, text=key)
        label.grid(row=row, column=0, sticky='news')
        entry = tk.Entry(self.window, textvariable=field)
        entry.grid(row=row, column=1, sticky='news', padx=self.UNIT)
        submit = tk.Button(self.window, text='Update Name',
                           command=lambda: self.update_port(port, field.get()))
        submit.grid(row=row, column=2, sticky='news')

    def get_config(self, key: str):
        if key in self.app_config:
            return self.app_config[key]
        else:
            return ''

    def get_field(self, key: str):
        return self.variables[key].get()

    def header(self, key: str, row: int = None):
        row = self.row_index if row is None else row
        self.row_index = row + 2
        padding = ((0 if row == 0 else self.UNIT*3), 0)  # built in spacer

        label = tk.Label(self.window, text=key)
        label.grid(row=row, column=0, columnspan=3,
                   sticky='news', pady=padding)
        separator = Separator(self.window, orient='horizontal')
        separator.grid(row=row+1, column=0, columnspan=3,
                       sticky='news', pady=(0, self.UNIT))

    def menu(self):
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label='Exit', accelerator='Ctrl+Q', underline=1,
                              command=self.quit_app)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label='About', underline=0,
                              command=self.about_app)

        menubar.add_cascade(label='File', menu=file_menu, underline=0)
        menubar.add_cascade(label='Help', menu=help_menu, underline=0)
        return menubar

    def poll_loop(self, frequency: int):
        self.after(frequency, lambda: self.poll_loop(frequency))
        result = self.poll_callback(self, self.emulator)

    def quit_app(self, event=None):
        self.quit()

    def set_field(self, key: str, value: str):
        return self.variables[key].set(value)

    def status(self, key: str, value: str = '', row: int = None):
        self.variables[key] = StringVar(value=value)
        row = self.row_index if row is None else row
        self.row_index = row + 1

        label = tk.Label(self.window, text=key)
        label.grid(row=row, column=0, sticky='nesw')
        message = tk.Label(self.window, anchor='w',
                           textvariable=self.variables[key])
        message.grid(row=row, column=1, columnspan=2,
                     sticky='nesw', padx=(self.UNIT, 0))

    def update_port(self, port: int, name: str):
        self.update_callback(self.emulator, port, name)

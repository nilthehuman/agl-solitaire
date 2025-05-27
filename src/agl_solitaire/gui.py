import re
import tkinter
import tkinter.font
from tkinter import ttk


from src.agl_solitaire import application
from src.agl_solitaire import utils


class GUIWindow(application.Application):
    """The windowed graphical user interface for the application, meant to replace
    the old terminal based UI."""

    # this is a singleton class, and some member functions will need to know about self
    _SELF = None

    class UserInput(KeyboardInterrupt):
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        GUIWindow._SELF = self
        self.root = tkinter.Tk()
        self.root.title('agl-solitaire')
        self.root.configure(background='grey20')
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.geometry('720x480')
        self.frame = None
        self.label = None
        self.text = None
        self.entry = None
        self.style = ttk.Style(self.root)
        try:
            self.style.theme_use('clam')
        except tkinter.TclError:
            # nevermind, fall back to default theme
            pass
        self.style.configure('TFrame', background='grey20', foreground='grey90')
        self.style.configure('TLabel', background='grey20', foreground='grey90')
        self.style.configure('Highlight.TLabel', background='grey20', foreground='lightgreen')
        self.style.map('TButton',
            foreground = [('!active', 'grey70'),  ('active', 'gray30'), ('pressed', 'gray30')],
            background = [('!active', '#8800DD'), ('active', 'gray70'), ('pressed', 'gray90')]
        )
        self.root.bind("<Return>", self.return_pressed)
        self.user_input = tkinter.StringVar(value=None)
        def quit_app():
            # TODO: offer to save experiment state before exiting for good
            self.root.destroy()
            # TODO: avoid forceful panic exit if we can
            import os
            os._exit(os.EX_OK)
        self.root.protocol('WM_DELETE_WINDOW', quit_app)

    def return_pressed(self, _event):
        """Handle user input in Entry widget."""
        assert self.entry
        input = self.entry.get()
        self.entry.delete(0, len(input))
        self.user_input.set(input)

    #### overridden Application member functions ####

    def main_menu(self):
        """Present the starting screen of the application."""
        if self.frame:
            self.frame.destroy()

        self.frame = ttk.Frame(self.root, relief=tkinter.RAISED, borderwidth=12)
        self.frame.grid(column=0, row=0, sticky=tkinter.NSEW, columnspan=1)
        self.frame['padding'] = (10, 15, 10, 15)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)

        #self.label = ttk.Label(self.frame, font=('Consolas', 11), text='', style='TLabel')
        #vsb = ttk.Scrollbar(self.frame, command=self.label.yview, orient='vertical')
        #self.label.configure(yscrollcommand=vsb.set)
        #self.label.grid(column=0, row=0, sticky=tkinter.N)
        #char_width = tkinter.font.Font(font=self.label.cget('font')).measure('N')
        #self.label.configure(wraplength=char_width * 60)

        self.text = tkinter.Text(self.frame, height=20, borderwidth=0, wrap=tkinter.WORD)
        self.text.configure(background=self.style.lookup('TLabel', 'background'), foreground=self.style.lookup('TLabel', 'foreground'))
        self.text.grid(column=0, row=0, sticky=tkinter.N)

        self.entry = ttk.Entry(self.frame)
        self.entry.grid(column=0, row=1, sticky=tkinter.S, pady=15)
        self.entry.focus_set()

        # widen root to fit largest widget
        self.root.update_idletasks()
        self.root.minsize(self.frame.winfo_width(), self.frame.winfo_height())

        super().main_menu()
        self.root.destroy()

    def run_experiment(self, *args, **kwargs):
        """Create message labels and controls needed for the experiment."""
        #if self.frame:
        #    self.frame.destroy()

        #self.frame = ttk.Frame(self.root, relief=tkinter.RAISED, borderwidth=12)
        #self.frame.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
        #self.frame['padding'] = (10, 15, 10, 15)

        #string = "Vongo as dakhkhad sa ognov.       'The mayor came from the town square alone.'"
        #martian_string = 'Vongo as dakhkhad sa ognov.'
        #english_translation = "'The mayor came from the town square alone.'"

        #self.text = tkinter.Text(self.frame, height=10, borderwidth=0, wrap=tkinter.WORD)
        #self.text.configure(background=self.style.lookup('TLabel', 'background'), foreground=self.style.lookup('TLabel', 'foreground'))
        #self.text.tag_configure('highlight', foreground='red', font=('Arial', 11))
        #self.text.insert(tkinter.END, martian_string, 'highlight')
        #self.text.insert(tkinter.END, '  ' + english_translation)
        #self.text.configure(state=tkinter.DISABLED)
        #self.text.configure(width=len(martian_string) + len(english_translation) + 2)
        #self.text.grid(column=0, row=0, columnspan=2, pady=10)

        #string_frame = ttk.Frame(self.frame, relief=tkinter.FLAT, borderwidth=0)
        #string_frame.grid(column=0, row=1, columnspan=2)
        #martian_label = ttk.Label(string_frame, font=('Consolas', 11), text=martian_string, style='Highlight.TLabel')
        #martian_label.grid(column=0, row=1, padx=10)
        #english_label = ttk.Label(string_frame, font=('Consolas', 11), text=english_translation, style='TLabel')
        #english_label.grid(column=1, row=1, padx=10)

        #self.entry = ttk.Entry(self.frame)
        #self.entry.grid(column=0, row=2, columnspan=2, pady=10)

        # TODO: use nice buttons for user judgements
        #ttk.Button(self.frame, text='Good', command=self.user_answered_yes).grid(column=0, row=3, padx=10)
        #ttk.Button(self.frame, text='Bad', command=user_answered_no).grid(column=1, row=3, padx=10)

        # widen root to fit largest widget
        self.root.update_idletasks()
        self.root.minsize(self.frame.winfo_width(), self.frame.winfo_height())

        # start the actual experiment procedure
        super().run_experiment(*args, **kwargs)

    def on_button_click(self, text):
        utils.print(f"input: {text}")

    #### I/O member functions, replacing the OG terminal based functions from utils ####

    def print(string='', end='\n'):
        MAX_LINES_ON_SCREEN = 20
        assert GUIWindow._SELF.label or GUIWindow._SELF.text
        formatted_string = _old_print(string, end=end, left_margin=0, silent=True)
        # remove ANSI control sequences from terminal output
        formatted_string = re.sub(r'(\033)\[\d+m', '', formatted_string)
        if GUIWindow._SELF.label:
            existing_text = GUIWindow._SELF.label['text']
            all_text = existing_text + formatted_string
            text_kept_on_screen = '\n'.join(all_text.split('\n')[-MAX_LINES_ON_SCREEN:])
            GUIWindow._SELF.label.config(text=text_kept_on_screen)
        else:
            # TODO: create a class derived from tkinter.Text to do this on its own
            GUIWindow._SELF.text.configure(state=tkinter.NORMAL)
            GUIWindow._SELF.text.insert('end', formatted_string)
            GUIWindow._SELF.text.configure(state=tkinter.DISABLED)
            GUIWindow._SELF.text.yview(tkinter.END)
 
    def input(prompt=''):
        GUIWindow._SELF.root.wait_variable(GUIWindow._SELF.user_input)
        user_input = GUIWindow._SELF.user_input.get()
        GUIWindow._SELF.user_input.set(None)
        return user_input

    def clear(prompt=''):
        assert GUIWindow._SELF.label or GUIWindow._SELF.text
        if GUIWindow._SELF.label:
            # remove all text from the label:
            GUIWindow._SELF.label.config(text='')
        if GUIWindow._SELF.text:
            GUIWindow._SELF.text.delete('start', 'end')


# monkey patching: override a bunch of I/O functions from utils
_old_print = utils.print

utils.print = GUIWindow.print
utils.input = GUIWindow.input

# make sure we avoided infinite recursion
assert not _old_print is utils.print


if __name__ == '__main__':
    GUIWindow().main_menu()
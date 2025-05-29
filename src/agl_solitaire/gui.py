import re
import tkinter
#import tkinter.font
from tkinter import ttk


from src.agl_solitaire import application
from src.agl_solitaire import utils


MAX_LINES_ON_SCREEN = 20


# TODO
class CustomText(tkinter.Text):
    pass


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
        self.root.geometry('800x480')
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
        self.root.bind('<Configure>', self.redraw_now)
        self.root.bind('<Return>', self.return_pressed)
        self.user_input = tkinter.StringVar(value=None)
        def quit_app():
            # TODO: offer to save experiment state before exiting for good
            self.root.destroy()
            # TODO: avoid forceful panic exit if we can
            import os
            os._exit(os.EX_OK)
        self.root.protocol('WM_DELETE_WINDOW', quit_app)

    def redraw_now(self, _event):
        self.root.update_idletasks()

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

        # TODO move this to CustomText class
        self.text = tkinter.Text(self.frame, font=('Consolas', 11), height=MAX_LINES_ON_SCREEN, borderwidth=0, takefocus=False, wrap=tkinter.WORD)
        self.text.configure(background=self.style.lookup('TLabel', 'background'), foreground=self.style.lookup('TLabel', 'foreground'))
        self.text.tag_configure('red', foreground='red')
        self.text.tag_configure('green', foreground='green')
        self.text.tag_configure('yellow', foreground='yellow')
        self.text.tag_configure('blue', foreground='blue')
        self.text.tag_configure('magenta', foreground='magenta')
        self.text.tag_configure('cyan', foreground='cyan')
        self.text.tag_configure('white', foreground='white')
        self.text.tag_configure('lightred', foreground='tomato')
        self.text.tag_configure('lightgreen', foreground='lightgreen')
        self.text.tag_configure('lightyellow', foreground='lightyellow')
        self.text.tag_configure('lightblue', foreground='lightblue')
        self.text.tag_configure('lightmagenta', foreground='orchid1')
        self.text.tag_configure('lightcyan', foreground='lightcyan')
        self.text.tag_configure('lightwhite', foreground='snow')
        self.text.tag_configure('highlight', foreground='red')
        self.text.tag_configure('bold', font=('Consolas', 11, 'bold'))
        self.text.tag_configure('center', justify=tkinter.CENTER)
        self.text.grid(column=0, row=0, sticky=tkinter.NSEW)

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
        #ttk.Button(self.frame, text='Bad', command=self.user_answered_no).grid(column=1, row=3, padx=10)

        # widen root to fit largest widget
        self.root.update_idletasks()
        self.root.minsize(self.frame.winfo_width(), self.frame.winfo_height())

        # start the actual experiment procedure
        super().run_experiment(*args, **kwargs)

    #### I/O member functions, replacing the OG terminal based functions from utils ####

    def print(string='', end='\n'):
        # TODO update screen width dynamically based on Text widget width
        assert GUIWindow._SELF.label or GUIWindow._SELF.text
        formatted_string = _old_print(string, end=end, left_margin=0, silent=True)
        if GUIWindow._SELF.label:
            existing_text = GUIWindow._SELF.label['text']
            # remove ANSI control sequences from terminal output
            formatted_string = re.sub(r'\033\[\d+m', '', formatted_string)
            all_text = existing_text + formatted_string
            text_kept_on_screen = '\n'.join(all_text.split('\n')[-MAX_LINES_ON_SCREEN:])
            GUIWindow._SELF.label.config(text=text_kept_on_screen)
        else:
            # TODO: create a class derived from tkinter.Text to do all this on its own
            GUIWindow._SELF.text.configure(state=tkinter.NORMAL)
            # all Text widgets contain a '\n' at the end which is stupid but what can you do
            num_existing_lines = GUIWindow._SELF.text.get('1.0', tkinter.END).count('\n')
            if formatted_string.startswith('\r'):
                GUIWindow._SELF.text.delete(f'{num_existing_lines-1}.0', tkinter.END)
                formatted_string = '\n' + formatted_string[1:]
            GUIWindow._SELF.text.insert(tkinter.END, formatted_string)
            # replace ANSI control sequences with Text tags
            open_tags = []
            closed_tags = []
            for match in re.finditer(r'\033\[(\d+)m', formatted_string):
                code = int(match.group(1))
                if 0 != code:
                    # beginning of a colored span, will require an opening tag
                    open_from, open_to = match.span()
                    # N.B. tkinter.Text line indexes start from 1
                    open_line = num_existing_lines + formatted_string[:open_from].count('\n')
                    nearest_newline = formatted_string[:open_from].rfind('\n')
                    if nearest_newline != -1:
                        open_from -= nearest_newline + 1
                        open_to -= nearest_newline + 1
                    tag = utils.ansi_codes_to_names[code].replace(' ', '')
                    open_tags.append((tag, (open_line, open_from, open_to)))
                else:
                    # end of a colored span, will require a closing tag
                    close_from, close_to = match.span()
                    close_line = num_existing_lines + formatted_string[:close_from].count('\n')
                    nearest_newline = formatted_string[:close_from].rfind('\n')
                    if nearest_newline != -1:
                        close_from -= nearest_newline + 1
                        close_to -= nearest_newline + 1
                    # pop the stack
                    last_open_tag = open_tags[-1]
                    close_pos = (close_line, close_from, close_to)
                    closed_tags.append(last_open_tag + (close_pos,))
                    tag, (open_line, open_from, open_to) = last_open_tag
                    open_tags = open_tags[:-1]
                    GUIWindow._SELF.text.tag_add(tag, f'{open_line}.{open_from}', f'{close_line}.{close_from}')
            spans_to_delete = sorted([pos for tag in closed_tags for pos in tag[1:]])
            for (line, _from, to) in spans_to_delete[::-1]:
                GUIWindow._SELF.text.delete(f'{line}.{_from}', f'{line}.{to}')
            GUIWindow._SELF.text.configure(state=tkinter.DISABLED)
            GUIWindow._SELF.text.yview(tkinter.END)
            GUIWindow._SELF.root.update_idletasks()
 
    def input(prompt=''):
        assert GUIWindow._SELF.entry
        #print(prompt)
        GUIWindow._SELF.root.wait_variable(GUIWindow._SELF.user_input)
        user_input = GUIWindow._SELF.user_input.get()
        GUIWindow._SELF.user_input.set(None)
        return user_input

    def clear():
        assert GUIWindow._SELF.label or GUIWindow._SELF.text
        if GUIWindow._SELF.label:
            GUIWindow._SELF.label.config(text='')
        if GUIWindow._SELF.text:
            # remove all text from the text widget:
            GUIWindow._SELF.text.configure(state=tkinter.NORMAL)
            GUIWindow._SELF.text.delete('1.0', tkinter.END)
            GUIWindow._SELF.text.configure(state=tkinter.DISABLED)


# monkey patching: override a bunch of I/O functions from utils
_old_print = utils.print

utils.print = GUIWindow.print
assert not _old_print is utils.print  # make sure we avoided infinite recursion
utils.input = GUIWindow.input
utils.clear = GUIWindow.clear


if __name__ == '__main__':
    GUIWindow().main_menu()
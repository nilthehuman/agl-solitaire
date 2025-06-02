"""Brand new basic experimental graphical user interface using the built-in tkinter toolkit.
The application is eventually meant to be migrated to a web-based form, towards which this is
an intermediate step."""

import platform
import re
import sys
import tkinter
import tkinter.font
import tkinter.messagebox
from tkinter import ttk


from src.agl_solitaire import application
from src.agl_solitaire import utils


MAX_LINES_ON_SCREEN = 20


# FIXME: this won't be needed once the GUI is refactored to a proper event driven design
def handle_loose_exceptions(ex_type, value, _traceback):
    assert ex_type is tkinter.TclError
    # let this slide and quit silently

sys.excepthook = handle_loose_exceptions


class CustomText(tkinter.Text):
    """More convenient to use Text widget, with pleasing default style."""

    def __init__(self, *args, **kwargs):
        """Set up styling and custom tags."""
        super().__init__(*args, **kwargs)
        style = ttk.Style()
        self.configure(background=style.lookup('TLabel', 'background'),
                       foreground=style.lookup('TLabel', 'foreground'))
        self.tag_configure('red', foreground='red')
        self.tag_configure('green', foreground='green')
        self.tag_configure('yellow', foreground='yellow')
        self.tag_configure('blue', foreground='blue')
        self.tag_configure('magenta', foreground='magenta')
        self.tag_configure('cyan', foreground='cyan')
        self.tag_configure('white', foreground='white')
        self.tag_configure('lightred', foreground='tomato')
        self.tag_configure('lightgreen', foreground='lightgreen')
        self.tag_configure('lightyellow', foreground='lightyellow')
        self.tag_configure('lightblue', foreground='lightblue')
        self.tag_configure('lightmagenta', foreground='orchid1')
        self.tag_configure('lightcyan', foreground='lightcyan')
        self.tag_configure('lightwhite', foreground='snow')
        self.tag_configure('highlight', foreground='red')
        self.tag_configure('bold', font=('Consolas', 12, 'bold'))
        self.tag_configure('center', justify=tkinter.CENTER)

    def append(self, string):
        """Add more lines to the end of current content."""
        self.configure(state=tkinter.NORMAL)
        # all tkinter.Text widgets contain a '\n' at the end which is stupid but what can you do
        num_existing_lines = self.get('1.0', tkinter.END).count('\n')
        if string.startswith('\r'):
            self.delete(f'{num_existing_lines-1}.0', tkinter.END+'-1c')
            self.insert(tkinter.END, string[1:])
            # no Text.yview, don't jerk the screen while counting down time
        else:
            self.insert(tkinter.END, string)
            self.yview(tkinter.END)
        # replace ANSI control sequences with Text tags
        open_tags = []
        closed_tags = []
        for match in re.finditer(r'\033\[(\d+)m', string):
            code = int(match.group(1))
            if 0 != code:
                # beginning of a colored span, will require an opening tag
                open_from, open_to = match.span()
                # N.B. tkinter.Text line indexes start from 1
                open_line = num_existing_lines + string[:open_from].count('\n')
                nearest_newline = string[:open_from].rfind('\n')
                if nearest_newline != -1:
                    open_from -= nearest_newline + 1
                    open_to -= nearest_newline + 1
                tag = utils.ansi_codes_to_names[code].replace(' ', '')
                open_tags.append((tag, (open_line, open_from, open_to)))
            else:
                # end of a colored span, will require a closing tag
                close_from, close_to = match.span()
                close_line = num_existing_lines + string[:close_from].count('\n')
                nearest_newline = string[:close_from].rfind('\n')
                if nearest_newline != -1:
                    close_from -= nearest_newline + 1
                    close_to -= nearest_newline + 1
                # pop the stack
                last_open_tag = open_tags[-1]
                close_pos = (close_line, close_from, close_to)
                closed_tags.append(last_open_tag + (close_pos,))
                tag, (open_line, open_from, open_to) = last_open_tag
                open_tags = open_tags[:-1]
                self.tag_add(tag, f'{open_line}.{open_from}', f'{close_line}.{close_from}')
        spans_to_delete = sorted([pos for tag in closed_tags for pos in tag[1:]])
        for line, _from, to in spans_to_delete[::-1]:
            self.delete(f'{line}.{_from}', f'{line}.{to}')
        self.configure(state=tkinter.DISABLED)
        self.update_idletasks()


class GUIWindow(application.Application):
    """The windowed graphical user interface for the application, meant to replace
    the old terminal based UI."""

    # this is a singleton class, and some member functions called from outside
    # will need to know about self
    _SELF = None

    def __init__(self, *args, **kwargs):
        # sic, delay calling super().__init__() on purpose
        GUIWindow._SELF = self
        self.root = tkinter.Tk()
        self.root.title('agl-solitaire')
        self.root.configure(background='grey20')
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.geometry('800x560')
        self.frame = None
        self.label = None
        self.text = None
        self.entry = None
        self.button = None
        self.style = ttk.Style(self.root)
        try:
            self.style.theme_use('clam')
        except tkinter.TclError:
            # nevermind, fall back to default theme
            pass
        self.style.configure('TFrame', background='grey20', foreground='grey90')
        self.style.configure('TLabel', background='grey20', foreground='grey90')
        self.style.configure('Highlight.TLabel', background='grey20', foreground='lightgreen')
        # use a normal sized font in message windows as well
        default_font = tkinter.font.nametofont('TkDefaultFont').actual()['family'].replace(' ', '_')
        self.root.option_add('*Dialog.msg.font', default_font+' 12')
        self.style.map('TButton',
            foreground = [('!active', 'grey70'),  ('active', 'gray30'), ('pressed', 'gray30')],
            background = [('!active', '#8800DD'), ('active', 'gray70'), ('pressed', 'gray90')]
        )
        self.root.bind('<Configure>', self.redraw_now)
        self.root.bind('<Return>', self.on_return_pressed)
        self.root.bind('<Control-c>', self.on_ctrl_c_pressed)
        self.root.bind('<Control-Break>', self.on_ctrl_c_pressed)
        self.root.bind('<F11>', self.on_f11_pressed)
        self.root.timed_callback = None
        self.user_input = tkinter.StringVar(value=None)
        self.root.protocol('WM_DELETE_WINDOW', self.quit_app)
        super().__init__(*args, **kwargs)

    def prepare_transition_to(self, new_status):
        """Mark transitions between different stages of the application. Necessary for rearranging the GUI."""
        if new_status == GUIWindow.Status.MENU:
            if self.status != GUIWindow.Status.POST_TASK:
                self.set_up_default_screen()
        elif new_status == GUIWindow.Status.PRE_TASK:
            pass
        elif new_status == GUIWindow.Status.TRAINING:
            self.set_up_training_screen()
        elif new_status == GUIWindow.Status.TEST:
            self.set_up_test_screen()
        elif new_status == GUIWindow.Status.POST_TASK:
            self.set_up_default_screen()
        super().prepare_transition_to(new_status)

    ##############################
    ####    event handlers    ####
    ##############################

    def redraw_now(self, _event):
        self.root.update_idletasks()

    def on_return_pressed(self, _event):
        """Handle user input from Entry widget."""
        if self.entry:
            input_string = self.entry.get()
            self.entry.delete(0, len(input_string))
            self.user_input.set(input_string)
        else:
            # no Entry being shown on screen
            self.user_input.set('')

    def on_ctrl_c_pressed(self, _event):
        assert GUIWindow.Status.INITIALIZED < self.status
        if self.status == GUIWindow.Status.MENU:
            # looks like the user is trying to quit the application
            self.quit_app()
        elif GUIWindow.Status.MENU < self.status:
            self.halt_experiment()
            # this is really crude but at least kinda works...
            # TODO it really highlights how the blocking wait for input approach sucks though,
            # need to restructure the whole GUI I/O
            self.main_menu()
        else:
            raise ValueError

    def on_f11_pressed(self, _event):
        # platform specific, sadly
        if 'Windows' == platform.system():
            if self.root.state() == 'normal':
                self.root.state('zoomed')
            else:
                self.root.state('normal')
        else:
            current_state = self.root.attributes('-zoomed')
            self.root.attributes('-zoomed', not current_state)

    def quit_app(self):
        # TODO: offer to save experiment state before exiting for good
        self.root.destroy()
        # TODO: avoid forceful panic exit if we can
        import os
        os._exit(os.EX_OK)

    #######################################################
    ####    overridden Application member functions    ####
    #######################################################

    def set_up_default_screen(self):
        """Prepare to present the starting screen of the application."""
        if self.frame:
            self.frame.destroy()

        self.frame = ttk.Frame(self.root, relief=tkinter.RAISED, borderwidth=12)
        self.frame.grid(column=0, row=0, sticky=tkinter.NSEW, columnspan=1)
        self.frame['padding'] = (10, 15, 10, 15)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)

        #self.label = ttk.Label(self.frame, font=('Consolas', 12), text='', style='TLabel')
        #vsb = ttk.Scrollbar(self.frame, command=self.label.yview, orient='vertical')
        #self.label.configure(yscrollcommand=vsb.set)
        #self.label.grid(column=0, row=0, sticky=tkinter.N)
        #char_width = tkinter.font.Font(font=self.label.cget('font')).measure('N')
        #self.label.configure(wraplength=char_width * 60)

        self.text = CustomText(self.frame,
                               font=('Consolas', 12),
                               height=MAX_LINES_ON_SCREEN,
                               borderwidth=0,
                               takefocus=False,
                               wrap=tkinter.WORD)
        self.text.grid(column=0, row=0, sticky=tkinter.NSEW)

        self.entry = ttk.Entry(self.frame)
        self.entry.grid(column=0, row=1, sticky=tkinter.S, pady=15)
        self.entry.focus_set()

        # widen root to fit largest widget
        self.root.update_idletasks()
        self.root.minsize(self.frame.winfo_width(), self.frame.winfo_height())

    def main_menu(self):
        """Activate the starting screen where the user can choose what to do next."""
        super().main_menu()
        # if this function finishes that means we're quitting the application
        self.root.destroy()

    def set_up_training_screen(self):
        """Remove Entry widget for the first half of an experiment task where the participant is
        just observing the training stimuli."""
        #if self.frame:
        #    self.frame.destroy()

        # TODO: put a progress bar at the top to show how far into the experiment we are, like PsyToolkit does

        #self.frame = ttk.Frame(self.root, relief=tkinter.RAISED, borderwidth=12)
        #self.frame.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
        #self.frame['padding'] = (10, 15, 10, 15)

        #self.text = CustomText(self.frame, height=10, borderwidth=0, wrap=tkinter.WORD)
        #self.text.configure(background=self.style.lookup('TLabel', 'background'), foreground=self.style.lookup('TLabel', 'foreground'))
        #self.text.tag_configure('highlight', foreground='red', font=('Arial', 12))
        #self.text.insert(tkinter.END, martian_string, 'highlight')
        #self.text.insert(tkinter.END, '  ' + english_translation)
        #self.text.configure(state=tkinter.DISABLED)
        #self.text.configure(width=len(martian_string) + len(english_translation) + 2)
        #self.text.grid(column=0, row=0, columnspan=2, pady=10)

        if self.entry:
            self.entry.destroy()
            self.entry = None
        #self.entry = ttk.Entry(self.frame)
        #self.entry.grid(column=0, row=2, columnspan=2, pady=10)

    def set_up_test_screen(self):
        """Create controls needed for the latter half of an experiment task where the participant
        judges novel stimuli."""
        #string = "Vongo as dakhkhad sa ognov.       'The mayor came from the town square alone.'"
        #martian_string = 'Vongo as dakhkhad sa ognov.'
        #english_translation = "'The mayor came from the town square alone.'"

        #string_frame = ttk.Frame(self.frame, relief=tkinter.FLAT, borderwidth=0)
        #string_frame.grid(column=0, row=1, columnspan=2)
        #martian_label = ttk.Label(string_frame, font=('Consolas', 12), text=martian_string, style='Highlight.TLabel')
        #martian_label.grid(column=0, row=1, padx=10)
        #english_label = ttk.Label(string_frame, font=('Consolas', 12), text=english_translation, style='TLabel')
        #english_label.grid(column=1, row=1, padx=10)

        if self.entry:
            self.entry.destroy()
            self.entry = None

        self.frame.grid_columnconfigure(1, weight=1)
        self.text.grid(column=0, row=0, columnspan=2, sticky=tkinter.NSEW)

        self.button = ttk.Button(self.frame, text='Yes', command=lambda: self.on_user_answer('yes'))
        self.button.grid(column=0, row=3, sticky=tkinter.E, padx=40, pady=15)
        ttk.Button(self.frame, text='No', command=lambda: self.on_user_answer('no')).grid(column=1, row=3, sticky=tkinter.W, padx=40, pady=15)

    def on_user_answer(self, answer):
        """Handle user's judgement about a test string in the experiment."""
        assert GUIWindow.Status.MENU < self.status
        self.user_input.set(answer)

    def halt_experiment(self):
        assert GUIWindow.Status.MENU < self.status
        if self.root.timed_callback is not None:
            self.root.after_cancel(self.root.timed_callback)
        return super().halt_experiment()

    ##########################################################################################
    ####    I/O member functions, replacing the OG terminal based functions from utils    ####
    ##########################################################################################

    @staticmethod
    def print(string='', **moreargs):
        if match := re.match(r'\s*(warning|error):\s*(.*)', str(string)):
            header = match.group(1).capitalize()
            body_text = match.group(2)
            body_text = body_text[0].upper() + body_text[1:] + ('.' if not body_text.endswith('.') else '')
            tkinter.messagebox.showwarning(header, body_text, parent=GUIWindow._SELF.root)
            return
        assert GUIWindow._SELF.label or GUIWindow._SELF.text
        formatted_string = _old_print(string, left_margin=0, silent=True, **moreargs)
        if GUIWindow._SELF.label:
            existing_text = GUIWindow._SELF.label['text']
            # remove ANSI control sequences from terminal output
            formatted_string = re.sub(r'\033\[\d+m', '', formatted_string)
            all_text = existing_text + formatted_string
            text_kept_on_screen = '\n'.join(all_text.split('\n')[-MAX_LINES_ON_SCREEN:])
            GUIWindow._SELF.label.config(text=text_kept_on_screen)
        else:
            assert GUIWindow._SELF.text
            GUIWindow._SELF.text.append(formatted_string)

    @staticmethod
    def input(prompt=''):
        if prompt:
            utils.print(prompt)
        GUIWindow._SELF.root.wait_variable(GUIWindow._SELF.user_input)
        user_input = GUIWindow._SELF.user_input.get()
        GUIWindow._SELF.user_input.set(None)
        return user_input

    @staticmethod
    def clear():
        assert GUIWindow._SELF.label or GUIWindow._SELF.text
        if GUIWindow._SELF.label:
            GUIWindow._SELF.label.config(text='')
        if GUIWindow._SELF.text:
            GUIWindow._SELF.text.configure(state=tkinter.NORMAL)
            GUIWindow._SELF.text.delete('1.0', tkinter.END)
            GUIWindow._SELF.text.configure(state=tkinter.DISABLED)

    @staticmethod
    def sleep(seconds, callback=None):
        def callback_wrapper():
            if callback is not None:
                callback()
            # trigger user input variable manually
            GUIWindow._SELF.user_input.set('')
        GUIWindow._SELF.root.timed_callback = GUIWindow._SELF.root.after(int(seconds * 1000), callback_wrapper)
        GUIWindow._SELF.root.wait_variable(GUIWindow._SELF.user_input)
        GUIWindow._SELF.root.after_cancel(GUIWindow._SELF.root.timed_callback)

    @staticmethod
    def breakable_loop(total_time, wait_per_cycle=1, step=None, _input_thread=None):
        assert 0 < total_time
        # ignore _input_thread, we use the tkinter event loop instead
        def loop(remaining_time):
            if remaining_time <= 0:
                return
            if step is not None:
                step(remaining_time)
            utils.sleep(wait_per_cycle, lambda: loop(remaining_time - wait_per_cycle))
        loop(total_time)


# monkey patching: override a bunch of I/O functions from utils
# TODO: maybe refactor so that the Application > GUIWindow inheritance does this
_old_print = utils.print
_old_sleep = utils.sleep

utils.print = GUIWindow.print
utils.sleep = GUIWindow.sleep
utils.breakable_loop = GUIWindow.breakable_loop
# make sure we avoided infinite recursion
assert not _old_print is utils.print
assert not _old_print is utils.print
utils.input = GUIWindow.input
utils.clear = GUIWindow.clear


if __name__ == '__main__':
    GUIWindow().main_menu()
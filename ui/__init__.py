import tkinter as tk
import ttkbootstrap as ttk
from PIL import Image, ImageTk

''' Constants '''
COLOURS = {
    "primary": "#3d4b74",
    "secondary": "#fbc536",
    "success": "#02b875",
    "info": "#17a2b8",
    "warning": "#f0ad4e",
    "danger": "#d9534f",
    "light": "#F8F9FA",
    "dark": "#343A40",
    "bg": "#ffffff",
    "fg": "#343a40",
    "selectbg": "#adb5bd",
    "selectfg": "#ffffff",
    "border": "#bfbfbf",
    "inputfg": "#343a40",
    "inputbg": "#ffffff",
    "active": "#f5f5f5"
}

# Fonts
BODY_FONT = 'TkTextFont 18'
HEADING_FONT = 'TkHeadingFont 38 bold'
ITALIC_CAPTION_FONT = 'TEMP - set in main.py when MainApp is initialised'
BOLD_CAPTION_FONT = 'TEMP - set in main.py when MainApp is initialised'
TOOLTIP_FONT = 'TkTooltipFont 13'
TEXT_ENTRY_FONT = 'TkTextFont 15'

def createWidgetStyles(style):
    ''' Creates the custom styles for the widgets which overwrite the base styles from the theme '''
    # Test styles for debugging
    style.configure('test.TFrame', background='red')

    # Text
    style.configure('TLabel', font=BODY_FONT)
    style.configure('Heading.TLabel', font=HEADING_FONT, background=COLOURS["primary"], foreground='#ffffff')
    style.configure('ItalicCaption.TLabel', font=ITALIC_CAPTION_FONT)
    style.configure('BoldCaption.TLabel', font=BOLD_CAPTION_FONT)
    style.configure('Entry.TLabel', font=TEXT_ENTRY_FONT)

    # Menu bar
    style.configure('mb.TFrame', background='#3D4B74')
    style.configure("mt.TLabel", font=("Arial", 16, "bold"), foreground="#ffffff", background="#3D4B74")
    style.configure("Close.secondary.TButton", foreground='black', font=('TkTextFont 15 bold'), width=10)

    # Login Screen
    style.configure('Items.TFrame', padding=(20, 20, 20, 20))

def createStyle():
    ''' Initialises the style and loads the theme for the entire application '''
    style = ttk.Style()
    ttk.Style.load_user_themes(style, 'agsStyle.json')
    style.theme_use('ags')
    createWidgetStyles(style)
    return style

#Tooltip class and functions adapted from
#https://stackoverflow.com/questions/20399243/display-message-when-hovering-over-something-with-mouse-cursor-in-python
class ToolTip:
    ''' Class to create a tooltip for a given widget. With customisable text. '''
    def __init__(self, widget: tk.Widget):
        self.widget = widget
        self.tipWindow = None
        self.id = None
        self.text = ''
        self.x = self.y = 0

    def showTooltip(self, text: str):
        ''' Display text in a tooltip window based on the mouse position '''
        self.text = text
        if self.tipWindow or not self.text:
            return
        x = self.widget.winfo_pointerx() + 8
        y = self.widget.winfo_pointery() + 8
        self.tipWindow = tk.Toplevel(self.widget)
        self.tipWindow.wm_overrideredirect(1)
        self.tipWindow.wm_geometry(f'+{x}+{y}')
        label = ttk.Label(self.tipWindow, text=self.text, justify='left',
                          background='#ffffff', relief='flat', borderwidth=1,
                          font=TOOLTIP_FONT)
        label.pack(ipadx=1)

    def showTooltipOnWidget(self, text: str):
        ''' Display text in a tooltip window based on the widget position '''
        self.text = text
        if self.tipWindow or not self.text:
            return
        x = self.widget.winfo_rootx() + self.widget.winfo_width() - 10
        y = self.widget.winfo_rooty() - 10
        self.tipWindow = tk.Toplevel(self.widget)
        self.tipWindow.wm_overrideredirect(1)
        self.tipWindow.transient(self.widget)
        self.tipWindow.wm_geometry(f'+{x}+{y}')
        label = ttk.Label(self.tipWindow, text=self.text, justify='left',
                          background='#ffffff', relief='flat', borderwidth=1,
                          font=TOOLTIP_FONT)
        label.pack(ipadx=1)

    def hideTooltip(self):
        if self.tipWindow:
            self.tipWindow.destroy()
        self.tipWindow = None

def createTooltip(widget: tk.Widget, text: str, onWidget: bool = False):
    ''' Initialise a tooltip with text that is shown when the user hovers over chosen widget.
    If onWidget is True, the tooltip will be shown on the widget itself without the need to hover over it. '''
    tool_tip = ToolTip(widget)

    if onWidget:
        tool_tip.showTooltipOnWidget(text)

        def leave(tk_event: tk.Event = None):
            tool_tip.hideTooltip()

        widget.bind('<FocusIn>', leave)
        widget.after(8000, leave) # After 8 seconds, hide the tooltip
        #master.bind('<ShowFrame>', leave) #Add an event for when the page is changed to hide the tooltip
    else:
        def enter(tk_event: tk.Event):
            tool_tip.showTooltip(text)

        def leave(tk_event: tk.Event):
            tool_tip.hideTooltip()

        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)
    

class PageStructure(ttk.Frame):
    ''' Base class for all pages '''
    def __init__(self, parent, controller):
        super().__init__(parent)

class MenuBar(ttk.Frame):
    ''' Class to create the menu bar shown on many pages '''
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.pack(side='top', fill='x')

        self.configure(style='mb.TFrame')
        
        # Create title label
        self.logo = ImageTk.PhotoImage(Image.open("images/ags.png").resize((50, 50), Image.LANCZOS))
        self.titleLabel = ttk.Label(self, text="Sound and Lighting", image=self.logo, compound='left', style='mt.TLabel')
        self.titleLabel.pack(side="left", padx=10, pady=5)

        # Create close button
        closeButton = ttk.Button(self, text="Close", command=self.quit, style='Close.secondary.TButton')
        closeButton.pack(side="right", padx=10, pady=5)

        # Create FAQ/Help button
        helpButton = ttk.Button(self, text="FAQ", command=None, style='Close.secondary.TButton')
        helpButton.pack(side="right", padx=10, pady=5)
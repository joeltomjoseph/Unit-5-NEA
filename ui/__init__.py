import tkinter as tk
import ttkbootstrap as ttk

''' Constants '''
COLORS = {
    'fg': '#5c616c',
    'bg': '#f5f6f7',
    'disabledbg': '#fbfcfc',
    'disabledfg': '#a9acb2',
    'selectbg': '#5294e2',
    'selectfg': '#ffffff',
    'window': '#ffffff',
    'focuscolor': '#5c616c',
    'checklight': '#fbfcfc'
}

# Fonts
BODY_FONT = 'TkTextFont'
HEADING_FONT = 'TkHeadingFont 20 bold'
ITALIC_CAPTION_FONT = 'TEMP - set in main.py when MainApp is initialised'
BOLD_CAPTION_FONT = 'TEMP - set in main.py when MainApp is initialised'
TOOLTIP_FONT = 'TkTooltipFont 11'
TEXT_ENTRY_FONT = 'TkTextFont 11'

#Tooltip class and create_tooltip function adapted from
#https://stackoverflow.com/questions/20399243/display-message-when-hovering-over-something-with-mouse-cursor-in-python
class ToolTip:
    def __init__(self, widget: tk.Widget):
        self.widget = widget
        self.tip_window = None
        self.id = None
        self.text = ''
        self.x = self.y = 0

    def show_tooltip(self, text: str):
        """
        Display text in a tooltip window
        """
        self.text = text
        if self.tip_window or not self.text:
            return
        x = self.widget.winfo_pointerx() + 8
        y = self.widget.winfo_pointery() + 8
        self.tip_window = tk.Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(1)
        self.tip_window.wm_geometry(f'+{x}+{y}')
        label = ttk.Label(self.tip_window, text=self.text, justify='left',
                          background='#ffffff', relief='flat', borderwidth=1,
                          font=TOOLTIP_FONT)
        label.pack(ipadx=1)

    def hide_tooltip(self):
        if self.tip_window:
            self.tip_window.destroy()
        self.tip_window = None

def create_tooltip(widget: tk.Widget, text: str):
    """
    Create a tooltip with text that is shown when the user hovers over widget.
    """
    tool_tip = ToolTip(widget)

    def enter(tk_event: tk.Event):
        tool_tip.show_tooltip(text)

    def leave(tk_event: tk.Event):
        tool_tip.hide_tooltip()

    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)

class PageStructure(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

class MenuBar(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.pack(side='top', fill='x')
        
        # Create title label
        title_label = ttk.Label(self, text="Sound and Lighting")
        title_label.pack(side="left", padx=10, pady=5)
        
        # Create close button
        close_button = ttk.Button(self, text="Close", command=self.quit)
        close_button.pack(side="right", padx=10, pady=5)
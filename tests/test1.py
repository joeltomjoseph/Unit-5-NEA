import ttkbootstrap as ttk


dict = {
"themes": {
    "ags": {
        "type": "light",
        "colors": {
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
    }
}
}

themes = dict['themes']
for theme in themes:
    for name, definition in themes.items():
        print(name)
        print(definition)
        print('\n')
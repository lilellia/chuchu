# A reimplementation of the tutorial example from
# https://www.geeksforgeeks.org/python/python-menu-widget-in-tkinter/

from chuchu import Application, Label



def main() -> None:
    app = Application(title="Menu Demonstration", size=(500, 200), status="no command yet")

    def update(label: Label, text: str) -> None:
        label.text = text
        app.status = f"Status: {text}"

    (label,) = app.add_row([Label("no command yet")])

    menu = app.set_menubar({
        "File": {
            "New File": lambda: update(label, "new file"),
            "Open...": lambda: update(label, "open"),
            "Save": lambda: update(label, "save"),
            "---": None,  # separator: key doesn't matter, just that the value is None
            "Exit": app.quit
        },

        "Edit": {
            "Cut": lambda: update(label, "cut"),
            "Copy": lambda: update(label, "copy"),
            "Paste": lambda: update(label, "paste"),
            "Select All": lambda: update(label, "select all"),
            "---": None,
            "Find": lambda: update(label, "find"),
            "Replace": lambda: update(label, "replace")
        },

        "Help": {
            "chuchu help": lambda: update(label, "chuchu help"),
            "demo": lambda: update(label, "demo"),
            "---": None,
            "about chuchu": lambda: update(label, "about chuchu")
        }
    })

    app.run()


if __name__ == "__main__":
    main()

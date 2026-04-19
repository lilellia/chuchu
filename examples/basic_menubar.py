# A reimplementation of the tutorial example from
# https://www.geeksforgeeks.org/python/python-menu-widget-in-tkinter/

from chuchu import Application, Label


def main() -> None:
    app = Application(title="Menu Demonstration", size=(500, 200), status="no command yet")

    label = Label("no command yet")
    app.add_row([label])

    def update(text: str) -> None:
        label.text = text
        app.status = f"Status: {text}"

    app.set_menubar(
        {
            "File": {
                "New File": lambda: update(text="new file"),
                "Open...": lambda: update(text="open"),
                "Save": lambda: update(text="save"),
                "---": None,  # separator: key doesn't matter, just that the value is None
                "Exit": app.quit,
            },
            "Edit": {
                "Cut": lambda: update(text="cut"),
                "Copy": lambda: update(text="copy"),
                "Paste": lambda: update(text="paste"),
                "Select All": lambda: update(text="select all"),
                "---": None,
                "Find": lambda: update(text="find"),
                "Replace": lambda: update(text="replace"),
            },
            "Help": {
                "chuchu help": lambda: update(text="chuchu help"),
                "demo": lambda: update(text="demo"),
                "---": None,
                "about chuchu": lambda: update(text="about chuchu"),
            },
        }
    )

    app.run()


if __name__ == "__main__":
    main()

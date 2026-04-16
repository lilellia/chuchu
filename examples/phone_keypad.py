from chuchu import Application, Button, Label, Textbox

def main():
    app = Application(title="Phone Dialer Demo")

    box = Textbox()

    # top rows: label and textbox
    app.grid(
        [
            [Label("Phone Number")],
            [box]
        ],
        weights=[[3], [3]]
    )

    # *technically* this is a 9-element row, but it'll be coerced into a 3x3 grid
    app.add_row([Button(digit, onclick=lambda d=digit: box.write(d), style="primary") for digit in "789456123"], columns=3)

    # the bottom row
    app.add_row([
        Button("<", onclick=box.backspace, style="secondary"),             # Textbox implements .backspace natively
        Button("0", onclick=lambda: box.write("0"), style="primary"),
        Button("*", onclick=lambda: print(box), style="secondary")         # Textbox also implements .__str__
    ])

    print(app.theme)
    app.run()


if __name__ == "__main__":
    main()

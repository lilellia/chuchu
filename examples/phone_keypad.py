from chuchu import Application, Button, Textbox

def main():
    app = Application(title="Phone Dialer Demo")

    box = Textbox()

    # top row: just the textbox
    app.add_row([box], weights=[3])

    # *technically* this is a 9-element row, but it'll be coerced into a 3x3 grid
    app.add_row([Button(digit, onclick=lambda d=digit: box.write(d)) for digit in "789456123"], columns=3)

    # the bottom row
    app.add_row([
        Button("<", onclick=box.backspace),             # Textbox implements .backspace natively
        Button("0", onclick=lambda: box.write("0")),
        Button("*", onclick=lambda: print(box))         # Textbox also implements .__str__
    ])

    app.run()


if __name__ == "__main__":
    main()

from bearlibterminal import terminal


def draw_page(tx, ty, page):
    for y in range(16):
        for x in range(16):
            terminal.put((x * 2) + tx, y + ty, page + (16 * y) + x)


def main():
    terminal.open()
    terminal.set("window: title='Test!', size=80x25, cellsize=16x32;")
    terminal.set("input.filter=keyboard,mouse")
    terminal.set("font: res/font.png, size=12x24, codepage=437, align=top-left")
    terminal.set("0xE000: res/meph_32x32.png, size=32x32, align=top-left")
    terminal.set("0xE100: res/meph_trees.png, size=32x32, align=top-left")

    tx = 1
    ty = 5
    page = 0xE000

    draw_page(tx, ty, page)

    terminal.refresh()

    event = terminal.read()
    while event != terminal.TK_CLOSE:
        terminal.clear()

        if event == terminal.TK_MOUSE_MOVE:
            mx = terminal.state(terminal.TK_MOUSE_X) + 1
            my = terminal.state(terminal.TK_MOUSE_Y) + 1

            terminal.printf(15, 1, "mx: {}, my: {}", mx, my)

            if mx >= tx and my >= ty:
                tid = page + (mx - tx) // 4 + ((my - ty) // 2) * 16
                terminal.printf(1, 4, "tile: {:04x}", tid)
            else:
                terminal.printf(1, 4, "tile: XXXX")
        elif event == terminal.TK_UP:
            page += 0x0100
        elif event == terminal.TK_DOWN:
            page -= 0x0100

        terminal.printf(1, 1, "event: {}", event)
        terminal.printf(1, 3, "page: {:x}", page)

        draw_page(tx, ty, page)

        terminal.refresh()
        event = terminal.read()

    terminal.close()


if __name__ == '__main__':
    main()

from sfml import sf

# create the main window
window = sf.RenderWindow(sf.VideoMode(640, 480), "pySFML Window")

# start the game loop
while window.is_open:
    # process events
    for event in window.events:
        # close window: exit
        if type(event) is sf.CloseEvent:
            window.close()

    window.clear()  # clear screen

    window.display()  # update the window
import random
import asyncio
import curses
import time
from itertools import cycle

STARS = 150

SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258


def read_controls(canvas):
    """Read keys pressed and returns tuple witl controls state."""
    rows_direction = columns_direction = 0
    space_pressed = False
    while True:
        pressed_key_code = canvas.getch()
        if pressed_key_code == -1:
            # https://docs.python.org/3/library/curses.html#curses.window.getch
            break

        if pressed_key_code == UP_KEY_CODE:
            rows_direction = -1

        if pressed_key_code == DOWN_KEY_CODE:
            rows_direction = 1

        if pressed_key_code == RIGHT_KEY_CODE:
            columns_direction = 1

        if pressed_key_code == LEFT_KEY_CODE:
            columns_direction = -1

        if pressed_key_code == SPACE_KEY_CODE:
            space_pressed = True

    return rows_direction, columns_direction, space_pressed


def draw_frame(canvas, start_row, start_column, text, negative=False):
    """Draw multiline text fragment on canvas, erase text instead of drawing if negative=True is specified."""
    rows_number, columns_number = canvas.getmaxyx()

    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < 0:
            continue

        if row >= rows_number:
            break

        for column, symbol in enumerate(line, round(start_column)):
            if column < 0:
                continue

            if column >= columns_number:
                break

            if symbol == ' ':
                continue

            # Check that current position it is not in a lower right corner of the window
            # Curses will raise exception in that case. Don`t ask why…
            # https://docs.python.org/3/library/curses.html#curses.window.addch
            if row == rows_number - 1 and column == columns_number - 1:
                continue

            symbol = symbol if not negative else ' '
            canvas.addch(row, column, symbol)


def get_frame_size(text):
    """Calculate size of multiline text fragment, return pair — number of rows and colums."""
    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns

def load_frames():
    ship_frames = []
    with open("sprite/rocket_frame_1.txt", "r") as sprite_file:
        ship_frames.append(sprite_file.read())
    with open("sprite/rocket_frame_2.txt", "r") as sprite_file:
        ship_frames.append(sprite_file.read())
    return ship_frames



async def animate_spaceship(canvas, row, column, ship_frames):
    while True:
        draw_frame(canvas, row, column, ship_frames[1], negative=True)
        draw_frame(canvas, row, column, ship_frames[0])
        canvas.refresh()
        await asyncio.sleep(0)

        # стираем предыдущий кадр, прежде чем рисовать новый
        draw_frame(canvas, row, column, ship_frames[0], negative=True)
        draw_frame(canvas, row, column, ship_frames[1])
        canvas.refresh()
        await asyncio.sleep(0)


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed

async def blink(canvas, row, column, symbol='*'):
    while True:
        if random.randint(0, 1):
            canvas.addstr(row, column, symbol, curses.A_DIM)
            for i in range(200):
                await asyncio.sleep(0)

        if random.randint(0, 1):
            canvas.addstr(row, column, symbol)
            for i in range(30):
                await asyncio.sleep(0)

        if random.randint(0, 1):
            canvas.addstr(row, column, symbol, curses.A_BOLD)
            for i in range(50):
                await asyncio.sleep(0)

        if random.randint(0, 1):
            canvas.addstr(row, column, symbol)
            for i in range(30):
                await asyncio.sleep(0)


def draw(canvas):
    stars = ['*', '+', '.', ':', '#']
    curses.curs_set(False)
    rows, cols = curses.initscr().getmaxyx()

    coroutines = []
    coroutine = fire(canvas, rows/2, cols/2)
    coroutines.append(coroutine)

    coroutine = animate_spaceship(canvas, rows/2, cols/2, load_frames())
    coroutines.append(coroutine)

    for star in range(1, STARS):
        coroutine = blink(canvas, random.randint(1, rows-1), random.randint(1, cols-1), symbol=random.choice(stars))
        coroutines.append(coroutine)
    count = 0


    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
                time.sleep(0.0001)
            except StopIteration:
                coroutines.remove(coroutine)
        if not coroutines:
            break
        canvas.refresh()


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)


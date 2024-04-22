import os
import random
import asyncio
import curses
import time
from itertools import cycle
from explosion import explode
from physics import update_speed
from curses_tools import draw_frame, get_frame_size, sleep
from obstacles import Obstacle, show_obstacles

STARS = 200
SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258
TIC_TIMEOUT = 0.01
ROWS = COLS = 0
COROUTINES = []
OBSTACLES = []
OBSTACLES_COLLISIONS = []
EVENTS = ""
TOTAL_SHOTS = 0
YEAR = 1956
TARGETS_DESTROYED = 0
DAMAGE = 0
GARBAGE_DELAY_TICS = 550



def read_controls(canvas):
    """Read keys pressed and returns tuple witl controls state."""
    rows_direction = columns_direction = 0
    space_pressed = False
    while True:
        pressed_key_code = canvas.getch()
        if pressed_key_code == -1:
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


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    rows_number, columns_number = canvas.getmaxyx()
    garbage_row_size, garbage_columns_size = get_frame_size(garbage_frame)
    column = max(column, 0)
    column = min(column, columns_number - 1)
    row = 0
    obstacle = Obstacle(row, column, garbage_row_size, garbage_columns_size)
    OBSTACLES.append(obstacle)
    COROUTINES.append(show_obstacles(canvas, OBSTACLES))
    try:
        while row < rows_number:
            if obstacle in OBSTACLES_COLLISIONS:
                OBSTACLES_COLLISIONS.remove(obstacle)
                await explode(canvas, obstacle.row, obstacle.column)
                global TARGETS_DESTROYED
                TARGETS_DESTROYED += 1
                break
            obstacle.row = row
            draw_frame(canvas, row, column, garbage_frame)
            await asyncio.sleep(0)
            draw_frame(canvas, row, column, garbage_frame, negative=True)
            row += speed
    finally:
        OBSTACLES.remove(obstacle)


def load_frames():
    ship_frames = []
    with open("sprite/rocket_frame_1.txt", "r") as sprite_file:
        ship_frames.append(sprite_file.read())
    with open("sprite/rocket_frame_2.txt", "r") as sprite_file:
        ship_frames.append(sprite_file.read())
    return ship_frames


def load_garbage_frames():
    garbage_frames = []
    with open("sprite/duck.txt", "r") as sprite_file:
        garbage_frames.append(sprite_file.read())
    with open("sprite/hubble.txt", "r") as sprite_file:
        garbage_frames.append(sprite_file.read())
    with open("sprite/lamp.txt", "r") as sprite_file:
        garbage_frames.append(sprite_file.read())
    with open("sprite/trash_large.txt", "r") as sprite_file:
        garbage_frames.append(sprite_file.read())
    with open("sprite/trash_small.txt", "r") as sprite_file:
        garbage_frames.append(sprite_file.read())
    with open("sprite/trash_xl.txt", "r") as sprite_file:
        garbage_frames.append(sprite_file.read())
    return garbage_frames


async def fill_orbit_with_garbage(canvas):
    garbage_frames = load_garbage_frames()
    while True:
        garbage_frame_current = random.choice(garbage_frames)
        _, garbage_frames_size = get_frame_size(garbage_frame_current)
        coroutine = fly_garbage(canvas, column=random.randint(1, COLS - garbage_frames_size),
                          garbage_frame=garbage_frame_current, speed=0.05)
        COROUTINES.append(coroutine)
        await sleep(GARBAGE_DELAY_TICS)


async def display_end_game(canvas):
    while True:
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        color = curses.color_pair(1)
        canvas.addstr(5, 15, '██╗  ██╗ ██████╗ ██╗  ██╗███████╗██╗   ██╗', color)
        canvas.addstr(6, 15, '██║ ██╔╝██╔═══██╗██║  ██║██╔════╝██║   ██║', color)
        canvas.addstr(7, 15, '█████╔╝ ██║   ██║███████║█████╗  ██║   ██║', color)
        canvas.addstr(8, 15, '██╔═██╗ ██║   ██║██╔══██║██╔══╝  ██║   ██║', color)
        canvas.addstr(9, 15, '██║  ██╗╚██████╔╝██║  ██║███████╗╚██████╔╝▄█╗', color)
        canvas.addstr(10, 15, '╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝', color)
        canvas.refresh()
        await asyncio.sleep(0)


async def display(canvas):
    while True:
        curses.init_pair(1, curses.COLOR_RED if TOTAL_SHOTS > 1000 else curses.COLOR_CYAN, curses.COLOR_BLACK)
        color = curses.color_pair(1)
        canvas.addstr(0, 0, 'Всего выстрелов = '+str(TOTAL_SHOTS), color)
        canvas.addstr(1, 0, 'Год = '+str(YEAR))
        canvas.addstr(2, 0, 'События: '+EVENTS)
        canvas.addstr(3, 0, 'Уничтожено = '+str(TARGETS_DESTROYED))
        curses.init_pair(2, curses.COLOR_RED if DAMAGE > 90 else curses.COLOR_GREEN, curses.COLOR_BLACK)
        color_damage = curses.color_pair(2)
        canvas.addstr(4, 0, 'Повреждений = '+str(DAMAGE)+"%", color_damage)
        canvas.refresh()
        await asyncio.sleep(0)

async def year():
    PHRASES = {
        # Только на английском, Repl.it ломается на кириллице
        1957: "First Sputnik",
        1961: "Gagarin flew!",
        1969: "Armstrong got on the moon!",
        1971: "First orbital space station Salute-1",
        1981: "Flight of the Shuttle Columbia",
        1998: 'ISS start building',
        2011: 'Messenger launch to Mercury',
        2020: "Take the plasma gun! Shoot the garbage!",
        2022: "Wow, earth is flat",
        2024: "Present days!",
    }

    while True:
        global YEAR, EVENTS, GARBAGE_DELAY_TICS
        YEAR += 1
        EVENTS = PHRASES.get(YEAR, '                                     ')
        if EVENTS:
            GARBAGE_DELAY_TICS -= 50
        await sleep(100)


async def animate_spaceship(canvas):
    sprite = 0
    ship_frames = load_frames()
    ship_size_row, ship_size_column = get_frame_size(ship_frames[sprite])
    row_screen_edge = ROWS - int(ship_size_row/4)
    fire_ship_position = int(ship_size_column/2)
    column_screen_edge = COLS - ship_size_column
    row = int(ROWS/2)
    column = int(COLS/2)
    row_speed = column_speed = 0
    global DAMAGE
    for frame in cycle([ship_frames[0], ship_frames[0], ship_frames[1], ship_frames[1]]):
        for obstacle in OBSTACLES:
            if obstacle.has_collision(row, column):
                DAMAGE += 1

        if DAMAGE <= 99:
            get_row, get_column, get_space_pressed = read_controls(canvas)
            row_speed, column_speed = update_speed(row_speed, column_speed, get_row, get_column)

            row += row_speed
            column += column_speed
            row = row + get_row
            column = column + get_column

            if row < 0:
                row = 0
            if column < 0:
                column = 0
            if row > row_screen_edge:
                row = row_screen_edge
            if column > column_screen_edge:
                column = column_screen_edge
            if get_space_pressed:
                global TOTAL_SHOTS
                TOTAL_SHOTS += 1
                coroutine = fire(canvas, row, column+fire_ship_position)
                COROUTINES.append(coroutine)
            draw_frame(canvas, row, column, frame)
            await asyncio.sleep(0)
            draw_frame(canvas, row, column, frame, negative=True)
        else:
            DAMAGE = 100
            coroutine = display_end_game(canvas)
            COROUTINES.append(coroutine)
            await asyncio.sleep(0)




async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    color = curses.color_pair(2)
    row, column = start_row, start_column
    canvas.addstr(round(row), round(column), '*', color)
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), 'O', color)
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ', color)
    row += rows_speed
    column += columns_speed
    symbol = '-' if columns_speed else '|'
    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1
    curses.beep()
    while 0 < row < max_row and 0 < column < max_column:
        for obstacle in OBSTACLES:
            if obstacle.has_collision(row, column):
                OBSTACLES_COLLISIONS.append(obstacle)
                return
        canvas.addstr(round(row), round(column), symbol, color)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ', color)
        row += rows_speed
        column += columns_speed


async def blink(canvas, row, column, symbol='*'):
    delay = random.randint(50, 100)
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(delay)
        canvas.addstr(row, column, symbol)
        await sleep(delay)
        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(delay)
        canvas.addstr(row, column, symbol)
        await sleep(delay)


def draw(canvas):
    stars = ['*', '+', '.', ':', '#']
    coroutine = animate_spaceship(canvas)
    COROUTINES.append(coroutine)
    coroutine = fill_orbit_with_garbage(canvas)
    COROUTINES.append(coroutine)
    coroutine = display(canvas)
    COROUTINES.append(coroutine)
    coroutine = year()
    COROUTINES.append(coroutine)

    for star in range(1, STARS):
        coroutine = blink(canvas, random.randint(1, ROWS-2),
                          random.randint(1, COLS-2), symbol=random.choice(stars))
        COROUTINES.append(coroutine)

    while True:
        for coroutine in COROUTINES.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                COROUTINES.remove(coroutine)
        if not COROUTINES:
            break
        time.sleep(TIC_TIMEOUT)
        canvas.refresh()


def main():
    curses.initscr().nodelay(True)
    curses.curs_set(False)
    curses.update_lines_cols()
    curses.wrapper(draw)


if __name__ == '__main__':
    ROWS, COLS = curses.initscr().getmaxyx()
    main()

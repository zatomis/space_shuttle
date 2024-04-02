import random
import time
import asyncio
import curses

STARS = 100

async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for i in range(400):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for i in range(60):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for i in range(100):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for i in range(60):
            await asyncio.sleep(0)


def draw(canvas):
    stars = ['*', '+', '.', ':', 'x']
    canvas.border()
    curses.curs_set(False)
    rows, cols = curses.initscr().getmaxyx()
    coroutines = []
    for star in range(1, STARS):
        coroutine = blink(canvas, random.randint(1, rows-2), random.randint(1, cols-2), symbol=random.choice(stars))
        coroutines.append(coroutine)
    while True:
        for coroutine in coroutines:
            try:
                coroutine.send(None)
            except StopIteration:
                break
        canvas.refresh()



if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)

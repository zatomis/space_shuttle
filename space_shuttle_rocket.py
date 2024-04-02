import time
import asyncio
import curses

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
    canvas.border()
    curses.curs_set(False)
    row, column = (5, 20)
    coroutine1 = blink(canvas, row, column, symbol='*')
    coroutine2 = blink(canvas, row+2, column, symbol='*')
    coroutine3 = blink(canvas, row+4, column, symbol='*')
    coroutine4 = blink(canvas, row+6, column, symbol='*')
    coroutine5 = blink(canvas, row+8, column, symbol='*')
    coroutines = [coroutine1, coroutine2, coroutine3, coroutine4, coroutine5]
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

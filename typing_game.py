"""built-in cross-platform modules"""

import argparse
import ctypes
import re
import unicurses as uc  # type: ignore
from pyle_manager import file_manager
import languages


class _Status:
    def __init__(self, lines: list[str]) -> None:
        self.line_num = 0
        self.line_index = 0
        self.lines = lines

    def end(self) -> bool:
        """return true if reached the end"""

        return self.line_num == len(self.lines) and self.line_index == len(
            self.lines[-1]
        )

    def current(self) -> str:
        """return current letter"""

        if self.line_index < len(self.lines[self.line_num]):
            return self.lines[self.line_num][self.line_index]
        else:
            return "^J"  # enter key

    def next(self) -> None:
        """continue to the next"""

        if self.line_index == len(self.lines[self.line_num]):
            self.line_index = 0
            self.line_num += 1
        else:
            self.line_index += 1

    def previous(self) -> None:
        """go to the previous"""

        if self.line_index > 0:
            self.line_index -= 1
        elif self.line_num > 0:
            self.line_num -= 1
            self.line_index = len(self.lines[self.line_num])

    def normal(self) -> None:
        """mark letter as normal"""

        uc.mvchgat(
            self.line_num,
            self.line_index,
            1,
            uc.A_NORMAL,
            uc.COLOR_WHITE,
        )

    def green(self) -> None:
        """mark letter as green"""

        uc.mvchgat(
            self.line_num,
            self.line_index,
            1,
            uc.A_ITALIC,
            2 if self.line_index < len(self.lines[self.line_num]) else 20,
        )

    def red(self) -> None:
        """mark letter red"""

        uc.mvchgat(
            self.line_num,
            self.line_index,
            1,
            uc.A_ITALIC,
            1 if self.line_index < len(self.lines[self.line_num]) else 10,
        )

    def white(self) -> None:
        """mark letter white"""

        uc.mvchgat(
            self.line_num,
            self.line_index,
            1,
            uc.A_NORMAL,
            3,
        )


def _timer() -> None:
    raise NotImplementedError("""
create an asyncronous timer to count the number of letters covered
""")


def _printer(status: _Status) -> None:
    """function that handles the printing operation"""

    for i in range(min(uc.getmaxx(uc.stdscr), len(status.lines)) - 1):
        uc.mvaddstr(i, 0, status.lines[i])

    status.white()
    while not status.end() and (button := uc.getkey()) != "^[":
        if button == status.current():
            status.green()
            status.next()
        elif button != "KEY_BACKSPACE":
            status.red()
            status.next()
        else:
            status.normal()
            status.previous()
        status.white()


def game(stdscr: ctypes.c_void_p, path: str) -> None:
    """main function"""

    # initialise
    uc.clear()
    uc.cbreak()
    uc.noecho()
    uc.keypad(uc.stdscr, True)
    uc.curs_set(0)
    uc.leaveok(uc.stdscr, True)

    # uc.use_default_colors()

    with open(path, "r", encoding="UTF-8") as file:
        lines = [re.sub(r"\s*$", "", line) for line in file.readlines()]

    status = _Status(lines)

    uc.mvaddstr(0, 0, "Press a button when you are ready to start!")

    if uc.has_colors():
        uc.start_color()
        uc.init_pair(1, uc.COLOR_RED, uc.COLOR_BLACK)
        uc.init_pair(10, uc.COLOR_RED, uc.COLOR_RED)
        uc.init_pair(2, uc.COLOR_GREEN, uc.COLOR_BLACK)
        uc.init_pair(20, uc.COLOR_GREEN, uc.COLOR_GREEN)
        uc.init_pair(uc.COLOR_WHITE, uc.COLOR_WHITE, uc.COLOR_BLACK)
        uc.init_pair(3, uc.COLOR_BLACK, uc.COLOR_WHITE)
    else:
        uc.mvaddstr(
            1, 0, "This terminal does not support colors and could behave unexpectedly."
        )

    uc.getkey()
    uc.clear()

    _printer(status)


if __name__ == "__main__":
    # parsing args
    PARSER = argparse.ArgumentParser(
        prog="typing game", description="typing game written in python"
    )
    PARSER.add_argument("-c", "--commandline", help="select via command line argument")
    ARGS = PARSER.parse_args()  # args.picker contains the modality

    # get path if not command line
    PATH = ARGS.commandline if ARGS.commandline else file_manager(picker=True)

    uc.wrapper(game, PATH)

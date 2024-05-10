"""built-in cross-platform modules"""

import argparse
import ctypes
import re
import os
import time
import unicurses as uc  # type: ignore
from pyle_manager import file_manager
from languages import format_config


class _Status:
    def __init__(self, lines: list[str], path: str) -> None:
        self.line_num = 0
        self.line_index = 0
        self.lines = lines

        self.language = format_config(path)

        # page variable
        self.start_line: int
        self.end_line: int

        # metrics
        self.correct = 0
        self.ignore = 0
        self.wrong = 0

    def update_correct(self) -> None:
        """increment correct count"""

        if self.ignore:
            self.ignore -= 1
        else:
            self.correct += 1

    def update_wrong(self) -> None:
        """increment wrong count"""

        if self.ignore:
            self.ignore -= 1
        else:
            self.wrong += 1

    def end(self) -> bool:
        """return true if reached the end"""

        end_file = (self.line_num == len(self.lines) - 1) and (
            self.line_index == len(self.lines[-1])
        )
        end_page = (self.line_num == self.end_line) and (self.line_index == 0)

        return end_page or end_file

    def current(self) -> str:
        """return current letter as in the source file"""

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
            self.ignore += 1
        elif self.line_num > self.start_line:
            self.line_num -= 1
            self.line_index = len(self.lines[self.line_num])
            self.ignore += 1

    def normal(self, cursor) -> None:
        """mark letter as normal"""

        if self.current() == " ":
            uc.mvaddstr(self.line_num - self.start_line, self.line_index, " ")

        uc.mvchgat(
            self.line_num - self.start_line,
            self.line_index,
            1,
            uc.A_NORMAL,
            uc.COLOR_WHITE if not cursor else 3,
        )

    def mark(self, success) -> None:
        """mark letter as green"""

        if self.current() == " ":
            uc.mvaddstr(self.line_num - self.start_line, self.line_index, "·")

        word, new_line = (2, 20) if success else (1, 10)

        uc.mvchgat(
            self.line_num - self.start_line,
            self.line_index,
            1,
            uc.A_ITALIC,
            word if self.line_index < len(self.lines[self.line_num]) else new_line,
        )


def _printer(status: _Status) -> None:
    """function that handles the printing operation"""

    status.start_line = 0
    status.end_line = min(uc.getmaxy(uc.stdscr), len(status.lines))
    button = ""

    start = time.time()
    while status.end_line > status.start_line and button != "^[":
        uc.clear()
        for i in range(status.start_line, status.end_line):
            uc.mvaddstr(i - status.start_line, 0, status.lines[i])

        status.normal(True)
        while not status.end() and (button := uc.getkey()) != "^[":
            if button == status.current():
                status.update_correct()
                status.mark(True)
                status.next()
            elif button == "KEY_BACKSPACE":
                status.normal(False)
                status.previous()
            elif button == "^I":
                for _ in range(4):
                    uc.ungetch(" ")
            else:
                status.update_wrong()
                status.mark(False)
                status.next()
            status.normal(True)

        # update lines
        status.start_line = status.end_line
        status.end_line = min(
            uc.getmaxy(uc.stdscr) + status.end_line, len(status.lines)
        )
    end = time.time()

    minutes = 5 * (end - start) / 60
    wpm = (status.correct + status.wrong) / minutes

    uc.clear()

    if status.correct + status.wrong == 0:
        uc.mvaddstr(0, 0, "You didn't even try...")
        uc.getkey()
        return

    accuracy = status.correct / (status.correct + status.wrong)
    uc.mvaddstr(0, 0, f"Accuracy: {accuracy:.2%}")
    uc.mvaddstr(1, 0, f"Speed: {wpm:.2f} wpm.")

    uc.getkey()


def game(stdscr: ctypes.c_void_p, path: str) -> None:
    """main function"""

    # initialise
    uc.clear()
    uc.cbreak()
    uc.noecho()
    uc.keypad(uc.stdscr, True)
    uc.curs_set(0)
    uc.leaveok(uc.stdscr, True)

    with open(path, "r", encoding="UTF-8") as file:
        lines = [re.sub(r"\s*$", "", line) for line in file.readlines()]

    status = _Status(lines, path)

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

    if os.path.isfile(PATH):
        uc.wrapper(game, PATH)
    else:
        print(PATH)
        print("Is not a text file!")

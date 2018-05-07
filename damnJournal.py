import curses
from curses import wrapper
from curses.textpad import rectangle
import calendar
import datetime


def main(screen):
    screen = curses.initscr()
    screen.keypad(True)

    # Set variables and create the calendar

    tmp_cursor_month = 0
    cur_time = datetime.datetime.now()  # type: datetime
    key_press = ""
    cursor_position = [-2, -2, -2]
    tmp_cursor_position = cursor_position
    cal = calendar.Calendar(0)
    cal_year = cur_time.year
    year = cal.yeardayscalendar(cal_year, 12)
    cal_month = ["January", "February", "March", "April", "May",
                 "June", "July", "August", "September", "October",
                 "November", "December"]
    days_of_week = "Mo Tu We Th Fr Sa Su"

    while key_press != "q" and key_press != "Q":

        if key_press == "y" or key_press == "Y":
            cursor_position = [-2, -2, -2]
            tmp_cursor_position = [-2, -2, -2]

        if key_press == "KEY_RIGHT":
            if cursor_position[1] == -2 and cal_year < 9999:
                cal_year += 1
                year = cal.yeardayscalendar(cal_year, 12)
            elif cursor_position[1] == -1 and cursor_position[0] < 11:
                cursor_position[0] += 1
            elif -1 <= cursor_position[0] and cursor_position[2] < 6:
                tmp_cursor_position = [cursor_position[0], cursor_position[1], cursor_position[2]]
                cursor_position[2] += 1

        if key_press == "KEY_LEFT":
            if cursor_position[1] == -2 and cal_year > 1:
                cal_year -= 1
                year = cal.yeardayscalendar(cal_year, 12)
            elif cursor_position[1] == -1 and cursor_position[0] > 0:
                cursor_position[0] -= 1
            elif cursor_position[0] >= 0 and cursor_position[2] > 0:
                tmp_cursor_position = [cursor_position[0], cursor_position[1], cursor_position[2]]
                cursor_position[2] -= 1

        if key_press == "KEY_DOWN":
            if cursor_position[0] == -2:
                if tmp_cursor_month != 0:
                    cursor_position = [tmp_cursor_month, -1, -1]
                else:
                    cursor_position = [0, -1, -1]
            elif cursor_position[1] == -1:
                if cursor_position[0] > 0:
                    cursor_position[1] = 0
                    cursor_position[2] = 0
                else:
                    cursor_position = [0, 0, 0]
            if cursor_position[0] >= 0 and -1 < cursor_position[1] < 5:
                tmp_cursor_position = [cursor_position[0], cursor_position[1], cursor_position[2]]
                cursor_position[1] += 1

        if key_press == "KEY_UP":
            if cursor_position[0] > -1 and cursor_position[1] == 0:
                cursor_position[1] = -1
                cursor_position[2] = -1
            elif cursor_position[1] == -1:
                tmp_cursor_month = cursor_position[0]
                cursor_position = [-2, -2, -2]
            elif cursor_position[0] > -1 and cursor_position[1] > 0:
                tmp_cursor_position = [cursor_position[0], cursor_position[1], cursor_position[2]]
                cursor_position[1] -= 1

        if cursor_position[1] > -1:
            try:
                test = year[0][cursor_position[0]][cursor_position[1]][cursor_position[2]]
            except IndexError:
                cursor_position = tmp_cursor_position
                current_day = year[0][cursor_position[0]][cursor_position[1]][cursor_position[2]]

        current_day = year[0][cursor_position[0]][cursor_position[1]][cursor_position[2]]

        if cursor_position[1] > -1 and current_day == 0:
            cursor_position = tmp_cursor_position


        screen.clear()

        uy = 4
        ux = 1
        counter = 1

        # Programatically print the month, days of week, and divider
        for i in range(0, len(cal_month)):
            weeks = cal.monthdayscalendar(cal_year, i + 1)
            if cursor_position[0] == i and cursor_position[1] == -1:
                screen.insstr(uy, ux, "{:^21s}".format(cal_month[i]), curses.A_REVERSE)
            else:
                screen.insstr(uy, ux, "{:^21s}".format(cal_month[i]))
            screen.insstr(uy + 1, ux, "{:^21s}".format(days_of_week))
            screen.insstr(uy + 2, ux, "{:~>21s}".format(""))
            # We need to convert the week to a string
            for j in range(0, len(weeks)):
                for k in range(0, len(weeks[j])):
                    if weeks[j][k] == 0 and (
                            cursor_position[0] == i and cursor_position[1] == j and cursor_position[2] == k):
                        screen.insstr(uy + 3 + j, ux + (k * 3), " {:2}".format(" "), curses.A_REVERSE)
                    elif weeks[j][k] == 0 and (
                            cursor_position[0] != i or cursor_position[1] != j or cursor_position[2] != k):
                        screen.insstr(uy + 3 + j, ux + (k * 3), " {:2}".format(" "))
                    elif weeks[j][k] != 0 and (
                            cursor_position[0] == i and cursor_position[1] == j and cursor_position[2] == k):
                        screen.insstr(uy + 3 + j, ux + (k * 3), " {:0>2}".format(str(weeks[j][k])), curses.A_REVERSE)
                    elif weeks[j][k] != 0 and (
                            cursor_position[0] != i or cursor_position[1] != j or cursor_position[2] != k):
                        screen.insstr(uy + 3 + j, ux + (k * 3), " {:0>2}".format(str(weeks[j][k])))
            ux += 24
            if counter == 4:
                ux = 1
                uy += 11
                counter = 1
            else:
                counter += 1

        # Draw Rectangles with 2 lines for the header, 6 lines for the body, 20 spaces wide programatically
        # Reset the positioning variables
        uy = 3
        ux = 0
        ly = 14
        lx = 23

        for i in range(0, 3):  # Rows
            for j in range(0, 4):  # Columns. 4 rows of 3
                rectangle(screen, uy, ux, ly, lx)
                # Increment x to draw the next column
                ux += 24
                lx += 24
            # Increment y to drow on the next row
            uy += 11
            ux = 0
            ly += 11
            lx = 23

        # Draw the Rectangle and Text for the Year Selector
        rectangle(screen, 0, 0, 2, 95)
        if cursor_position[0] == -2:
            screen.addstr(1, 1, "{:^94s}".format("<    " + str(cal_year) + "    >"), curses.A_REVERSE)
        else:
            screen.addstr(1, 1, "{:^94s}".format("<    " + str(cal_year) + "    >"))

        if cursor_position[1] > -1:
            rectangle(screen, 37, 0, 39, 95)
            current_day = year[0][cursor_position[0]][cursor_position[1]][cursor_position[2]]
            datestamp = cal_month[cursor_position[0]] + " " + str(current_day) + ", " + str(cal_year)
            screen.addstr(38, 1,
                          "{:^94s}".format(datestamp))
        screen.addstr(50, 0,
                      "Curser Position: {} {} {}".format(cursor_position[0], cursor_position[1], cursor_position[2]))
        screen.addstr(51, 0,
                      "  Temp Position: {} {} {}".format(tmp_cursor_position[0], tmp_cursor_position[1], tmp_cursor_position[2]))
        screen.addstr(52, 0,
                      "  Temp Position: {}".format(tmp_cursor_position))
        screen.addstr(53, 0, "Temp Cursor: {}".format(tmp_cursor_month))

        # Calendar draw is done, refresh, get a key press, and get out
        screen.refresh()
        key_press = screen.getkey()


wrapper(main)

import curses
from curses import wrapper
from curses.textpad import rectangle
import calendar
import datetime
import os

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

def main(screen):
    screen = curses.initscr()
    curses.start_color()
    curses.use_default_colors()
    screen.keypad(True)

    # Set variables and create the calendar

    tmp_cursor_month = 0  # This value stores the month when navigating up to the year selector.
    cur_time = datetime.datetime.now()  # type: datetime
    key_press = ""
    cursor_position = [-2, -2, -2] # Initializes cursor_position at the year selector
    tmp_cursor_position = cursor_position # Initializes a temporary cursor position variable for error recovery
    cal = calendar.Calendar(0)
    cal_year = cur_time.year
    year = cal.yeardayscalendar(cal_year, 12)
    cal_month = ["January", "February", "March", "April", "May",
                 "June", "July", "August", "September", "October",
                 "November", "December"]  # List of names to draw on for Calendar months
    days_of_week = "Mo Tu We Th Fr Sa Su"  # String to be printed for each calendar
    filename = ""
    home = os.system("echo $HOME")
    dir = os.environ['HOME'] + "/.damnJournal/"
    curses.init_pair(2, 0, 7)
    curses.init_pair(3, 6, 0)

    while key_press != "q" and key_press != "Q":
        error = 0

        if key_press == "y" or key_press == "Y":  # Gives option to return to year selector in navigation
            cursor_position = [-2, -2, -2]
            tmp_cursor_position = [-2, -2, -2]

        if (key_press == "e" or key_press == "E") and cursor_position[1] >= 0:  # Manages Edit function
            day = str(year[0][cursor_position[0]][cursor_position[1]][cursor_position[2]])
            filename = "{}{:0>4}{:0>2}{:0>2}.dat".format(dir, str(cal_year), str(cursor_position[0] + 1), str(day))
            os.system("nano " + filename)

        if (key_press == "d" or key_press == "D") and cursor_position[1] >= 0:  # Manages Edit function
            day = str(year[0][cursor_position[0]][cursor_position[1]][cursor_position[2]])
            filename = "{}{:0>4}{:0>2}{:0>2}.dat".format(dir, str(cal_year), str(cursor_position[0] + 1), str(day))
            if os.path.isfile(filename):
                os.system("mv -f {} {}.old".format(filename, filename))

        if (key_press == "u" or key_press == "U") and cursor_position[1] >= 0:  # Manages Edit function
            day = str(year[0][cursor_position[0]][cursor_position[1]][cursor_position[2]])
            filename = "{}{:0>4}{:0>2}{:0>2}.dat".format(dir, str(cal_year), str(cursor_position[0] + 1), str(day))
            if os.path.isfile("{}.old".format(filename)):  # Verify if file to undelete exists
                if os.path.isfile(filename):  # Check if new content has been added
                    os.system("cat {}.old >> {}".format(filename, filename))  # Append old file to new file
                    os.system("rm -f {}.old".format(filename))
                else:
                    os.system("mv -f {}.old {}".format(filename, filename))

        if "kLFT" in key_press and cursor_position[0] == -2:  # Handle Control and Alt Left Year Selector
            if key_press[4] == "5" and cal_year > 10:
                cal_year -= 10
            if key_press[4] == "5" and cal_year < 10:
                cal_year = 1
            if key_press[4] == "7" and cal_year > 100:
                cal_year -= 100
            if key_press[4] == "7" and cal_year < 100:
                cal_year = 1


        if key_press == "KEY_RIGHT" or key_press == "C":  # Manages the Right Arrow key press
            if cursor_position[1] == -2 and cal_year < 9999:  # Selector is on Year
                cal_year += 1
                year = cal.yeardayscalendar(cal_year, 12)
            elif cursor_position[1] == -1 and cursor_position[0] < 11:  # Selector is on Month
                cursor_position[0] += 1
            elif -1 <= cursor_position[0] and cursor_position[2] < 6:  # Selector is in Calendar navigation
                tmp_cursor_position = [cursor_position[0], cursor_position[1], cursor_position[2]]
                cursor_position[2] += 1

        if key_press == "KEY_LEFT" or key_press == "D":  # Manages the Left Arrow key press
            if cursor_position[1] == -2 and cal_year > 1:  # Selector is on Year
                cal_year -= 1
                year = cal.yeardayscalendar(cal_year, 12)
            elif cursor_position[1] == -1 and cursor_position[0] > 0:  # Selector is on Month
                cursor_position[0] -= 1
            elif cursor_position[0] >= 0 and cursor_position[2] > 0:  # Selector is in Calendar Navigation
                tmp_cursor_position = [cursor_position[0], cursor_position[1], cursor_position[2]]
                cursor_position[2] -= 1

        if key_press == "KEY_DOWN" or key_press == "B":  # Manages the Down Arrow key press
            if cursor_position[0] == -2:
                if tmp_cursor_month != 0:
                    cursor_position = [tmp_cursor_month, -1, -1]
                else:
                    cursor_position = [0, -1, -1]
            elif cursor_position[1] == -1:
                if cursor_position[0] > 0:
                    cursor_position[1] = 0
                    cursor_position[2] = next((i for i, x in enumerate(year[0][cursor_position[0]][0]) if x), None)
                else:
                    cursor_position[0] = 0
                    cursor_position[1] = 0
                    cursor_position[2] = next((i for i, x in enumerate(year[0][cursor_position[0]][0]) if x), None)

            elif cursor_position[0] > -1 and -1 < cursor_position[1] <= (len(year[0][cursor_position[0]][cursor_position[1]]) + 1):
                tmp_cursor_position = [cursor_position[0], cursor_position[1], cursor_position[2]]
                try:
                    if year[0][cursor_position[0]][cursor_position[1] + 1][cursor_position[2]] == 0:
                        b = cursor_position[1] + 1
                        for i, item in enumerate(year[0][cursor_position[0]][b]):
                            if item != 0:
                                cursor_position[2] = i
                        cursor_position[1] += 1
                    else:
                        cursor_position[1] += 1
                except:  # If anything goes awry, return to last known good cursor location
                    cursor_position = tmp_cursor_position

        if key_press == "KEY_UP" or key_press == "A":  # Manages the Up Arrow key press
            if cursor_position[0] > -1 and cursor_position[1] == 0:
                cursor_position[1] = -1
                cursor_position[2] = -1
            elif cursor_position[1] == -1:
                tmp_cursor_month = cursor_position[0]
                cursor_position = [-2, -2, -2]
            elif cursor_position[0] > -1 and cursor_position[1] >= 0:
                tmp_cursor_position = [cursor_position[0], cursor_position[1], cursor_position[2]]
                b = cursor_position[1] - 1
                if year[0][cursor_position[0]][b][cursor_position[2]] == 0:
                    cursor_position[1] -= 1
                    cursor_position[2] = next((i for i, x in enumerate(year[0][cursor_position[0]][b]) if x), None)
                else:
                    cursor_position[1] -= 1

        # Once key_press is processed, make one last test of cursor position to ensure there is no Index Error
        if cursor_position[1] > -1:
            try:
                test = year[0][cursor_position[0]][cursor_position[1]][cursor_position[2]]
            except IndexError:
                error = 1
                cursor_position = tmp_cursor_position
                current_day = year[0][cursor_position[0]][cursor_position[1]][cursor_position[2]]

        # One last check to ensure the cursor isn't on a zero-day.
        current_day = year[0][cursor_position[0]][cursor_position[1]][cursor_position[2]]
        if cursor_position[1] > -1 and current_day == 0:
            cursor_position = tmp_cursor_position

        # Clear the screen, and reset the values back to base for drawing text and shapes.
        screen.clear()

        uy = 4
        ux = 1
        counter = 1

        # Programmatically print the month, days of week, and divider
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
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
                        screen.addstr(uy + 3 + j, ux + (k * 3), " {:2}".format(" "), curses.A_REVERSE)

                    elif weeks[j][k] == 0 and (
                            cursor_position[0] != i or cursor_position[1] != j or cursor_position[2] != k):
                        screen.addstr(uy + 3 + j, ux + (k * 3), " {:2}".format(" "))

                    elif weeks[j][k] != 0 and (
                            cursor_position[0] == i and cursor_position[1] == j and cursor_position[2] == k):
                        filename = "{}{:0>4}{:0>2}{:0>2}.dat".format(dir, str(cal_year), str(i + 1), str(weeks[j][k]))
                        if os.path.isfile(filename):
                            screen.addstr(uy + 3 + j, ux + (k * 3), " {:0>2}".format(str(weeks[j][k])),
                                          curses.color_pair(1))
                        else:
                            screen.addstr(uy + 3 + j, ux + (k * 3), " {:0>2}".format(str(weeks[j][k])), curses.color_pair(2))

                    elif weeks[j][k] != 0 and (
                            cursor_position[0] != i or cursor_position[1] != j or cursor_position[2] != k):
                        filename = "{}{:0>4}{:0>2}{:0>2}.dat".format(dir, str(cal_year), str(i + 1), str(weeks[j][k]))
                        if os.path.isfile(filename):
                            screen.addstr(uy + 3 + j, ux + (k * 3), " {:0>2}".format(str(weeks[j][k])), curses.color_pair(3))
                        else:
                            screen.addstr(uy + 3 + j, ux + (k * 3), " {:0>2}".format(str(weeks[j][k])))


            # Increment the X position of the written text, then if the counter has reached 4, move down to next Y.
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
            filename = "{}{:0>4}{:0>2}{:0>2}.dat".format(dir, str(cal_year), str(cursor_position[0] + 1), str(current_day))
            datestamp = cal_month[cursor_position[0]] + " " + str(current_day) + ", " + str(cal_year)
            if os.path.isfile(filename):
                screen.addstr(38, 1,
                              "{:^94s}".format(datestamp), curses.color_pair(3))
                # rectangle(screen, 39, 0, 51, 95)
                # preview = open(filename, 'r')
                # data = [line.split('\n') for line in preview.readlines()]
                # if len(data) <= 5:
                #     for i in range(0, len(data)):
                #         screen.addstr(40 + i, 1, str(data[i]))
                # if len(data) >= 5:
                #     for i in range(0, 5):
                #         screen.addstr(40 + i, 1, str(data[i]))
            else:
                screen.addstr(38, 1,
                              "{:^94s}".format(datestamp))

        # Calendar draw is done, refresh, get a key press, and get out
        screen.refresh()
        key_press = screen.getkey()


wrapper(main)

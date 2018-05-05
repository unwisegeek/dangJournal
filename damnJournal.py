import curses
from curses import wrapper
from curses.textpad import rectangle
import calendar
import datetime


def main(screen):
    screen = curses.initscr()
    curTime = datetime.datetime.now()
    calYear = curTime.year
    keyPress = ""
    while keyPress != "q":
        if keyPress == "d":
            calYear += 1
        if keyPress == "a":
            calYear -= 1

        screen.clear()
        # Set variables and create the calendar
        calMonth = ["January", "February", "March", "April", "May",
                    "June", "July", "August", "September", "October",
                 "November", "December"]
        daysOfWeek = "Mo Tu We Th Fr Sa Su"
        cal = calendar.Calendar(0)
        uY = 4
        uX = 1
        counter = 1


        # Programatically print the month, days of week, and divider
        for i in range(0, len(calMonth)):
            weeks = cal.monthdayscalendar(calYear, i + 1)
            monthLength = len(calMonth[i])
            screen.insstr(uY, uX, "{:^22s}".format(calMonth[i]))
            screen.insstr(uY + 1, uX, "{:^22s}".format(daysOfWeek))
            screen.insstr(uY + 2, uX, "{:~>22s}".format(""))
            # We need to convert the week to a string
            for j in range(0, len(weeks)):
                days = []
                for k in range(0, len(weeks[j])):
                    if weeks[j][k] != 0:
                        days.append(weeks[j][k])
                    else:
                        days.append("  ")
                screen.insstr(uY+3+j, uX, " {:0>2} {:0>2} {:0>2} {:0>2} {:0>2} {:0>2} {:0>2}".format(days[0], days[1], days[2], days[3], days[4], days[5], days[6]))
            days = []
            uX += 24
            if counter == 4:
                uX = 1
                uY += 11
                counter = 1
            else:
                counter += 1


        # Draw Rectangles with 2 lines for the header, 6 lines for the body, 20 spaces wide programaticallY
        ## Reset the positioning variables
        uY = 3
        uX = 0
        lY = 14
        lX = 23

        for i in range(0, 3):  # Rows
            for j in range(0, 4):  # Columns. 4 rows of 3
                rectangle(screen, uY, uX, lY, lX)
                # Increment x to draw the next column
                uX += 24
                lX += 24
            # Increment y to drow on the next row
            uY += 11
            uX = 0
            lY += 11
            lX = 23

        # Draw the Rectangle and Text for the Year Selector
        rectangle(screen, 0, 0, 2, 95)
        screen.addstr(1, 1, "{:^94s}".format("<    " + str(calYear) + "    >"))



        # Calendar draw is done, refresh, get a key press, and get out
        screen.refresh()
        keyPress = screen.getkey()

wrapper(main)

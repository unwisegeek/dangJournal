import curses, calendar, datetime, os, sys, getpass, textwrap
from curses import wrapper
from curses.textpad import rectangle
from simplecrypt import encrypt, decrypt

def dimensions(chkscreen):
    chkscreen = curses.initscr()
    max_x = curses.COLS - 1
    max_y = curses.LINES - 1

    if max_x < 100 or max_y < 40:
        return False
    else:
        return True

def main(screen):
    screen = curses.initscr()
    curses.start_color()
    curses.use_default_colors()
    screen.keypad(True)


    # Set variables and create the calendar
    max_x = curses.COLS - 1
    max_y = curses.LINES - 1
    tmp_cursor_month = 0  # This value stores the month when navigating up to the year selector.
    cur_time = datetime.datetime.now()  # type: datetime
    key_press = ""
    cursor_position = [-2, -2, -2]  # Initializes cursor_position at the year selector
    tmp_cursor_position = cursor_position  # Initializes a temporary cursor position variable for error recovery
    cal = calendar.Calendar(0)
    cal_year = cur_time.year
    year = cal.yeardayscalendar(cal_year, 12)
    cal_month = ["January", "February", "March", "April", "May",
                 "June", "July", "August", "September", "October",
                 "November", "December"]  # List of names to draw on for Calendar months
    days_of_week = " Mo Tu We Th Fr Sa Su"  # String to be printed for each calendar
    conf_directory = os.environ['HOME'] + "/.damnJournal/"  # type: object
    curses.init_pair(2, 0, 7)
    curses.init_pair(3, 6, 0)

    while key_press != "q" and key_press != "Q":

        # Check for Terminal resizing
        if curses.is_term_resized(max_y, max_x):
            max_x = curses.COLS - 1
            max_y = curses.LINES - 1

        if key_press == "y" or key_press == "Y":  # Gives option to return to year selector in navigation
            cursor_position = [-2, -2, -2]
            tmp_cursor_position = [-2, -2, -2]

        if (key_press == "e" or key_press == "E") and cursor_position[1] >= 0:  # Manages Edit function
            day = str(year[0][cursor_position[0]][cursor_position[1]][cursor_position[2]])
            filename = "{}{:0>4}{:0>2}{:0>2}.dat".format(conf_directory, str(cal_year), str(cursor_position[0] + 1), str(day))
            os.system("nano " + filename)

        if (key_press == "r" or key_press == "R") and cursor_position[1] >= 0:  # Manages Edit function
            day = str(year[0][cursor_position[0]][cursor_position[1]][cursor_position[2]])
            filename = "{}{:0>4}{:0>2}{:0>2}.dat".format(conf_directory, str(cal_year), str(cursor_position[0] + 1), str(day))
            if os.path.isfile(filename):
                os.system("mv -f {} {}.old".format(filename, filename))

        if (key_press == "u" or key_press == "U") and cursor_position[1] >= 0:  # Manages Edit function
            day = str(year[0][cursor_position[0]][cursor_position[1]][cursor_position[2]])
            filename = "{}{:0>4}{:0>2}{:0>2}.dat".format(conf_directory, str(cal_year), str(cursor_position[0] + 1), str(day))
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

            elif not (not (cursor_position[0] > -1) or not (
                    -1 < cursor_position[1] <= (len(year[0][cursor_position[0]][cursor_position[1]]) + 1))):
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
                cursor_position = tmp_cursor_position

        # One last check to ensure the cursor isn't on a zero-day.
        current_day = year[0][cursor_position[0]][cursor_position[1]][cursor_position[2]]
        if cursor_position[1] > -1 and current_day == 0:
            cursor_position = tmp_cursor_position

        # Clear the screen, and reset the values back to base for drawing text and shapes.
        screen.clear()

        uy = 3
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
            screen.insstr(uy + 2, ux, " {:~>20s}".format(""))
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
                        filename = "{}{:0>4}{:0>2}{:0>2}.dat".format(conf_directory, str(cal_year), str(i + 1), str(weeks[j][k]))
                        if os.path.isfile(filename):
                            screen.addstr(uy + 3 + j, ux + (k * 3), " {:0>2}".format(str(weeks[j][k])),
                                          curses.color_pair(1))
                        else:
                            screen.addstr(uy + 3 + j, ux + (k * 3), " {:0>2}".format(str(weeks[j][k])),
                                          curses.color_pair(2))

                    elif weeks[j][k] != 0 and (
                            cursor_position[0] != i or cursor_position[1] != j or cursor_position[2] != k):
                        filename = "{}{:0>4}{:0>2}{:0>2}.dat".format(conf_directory, str(cal_year), str(i + 1), str(weeks[j][k]))
                        if os.path.isfile(filename):
                            screen.addstr(uy + 3 + j, ux + (k * 3), " {:0>2}".format(str(weeks[j][k])),
                                          curses.color_pair(3))
                        else:
                            screen.addstr(uy + 3 + j, ux + (k * 3), " {:0>2}".format(str(weeks[j][k])))

            # Increment the X position of the written text, then if the counter has reached 4, move down to next Y.
            ux += 24
            if counter == 4:
                ux = 1
                uy += 10
                counter = 1
            else:
                counter += 1

        # Draw Rectangles with 3 lines for the header, 6 lines for the body, 20 spaces wide programmatically
        # Reset the positioning variables
        uy = 2
        ux = 0
        ly = 12
        lx = 23

        for i in range(0, 3):  # Rows
            for j in range(0, 4):  # Columns. 4 rows of 3
                rectangle(screen, uy, ux, ly, lx)
                # Increment x to draw the next column
                ux += 24
                lx += 24
            # Increment y to draw on the next row
            uy += 10
            ux = 0
            ly += 10
            lx = 23

        # Draw the Rectangle and Text for the Year Selector
        rectangle(screen, 0, 0, 2, 95)
        if cursor_position[0] == -2:
            screen.addstr(1, 1, "{:^94s}".format("<    " + str(cal_year) + "    >"), curses.A_REVERSE)
        else:
            screen.addstr(1, 1, "{:^94s}".format("<    " + str(cal_year) + "    >"))

        if cursor_position[1] > -1:
            rectangle(screen, 32, 0, 34, 95)
            current_day = year[0][cursor_position[0]][cursor_position[1]][cursor_position[2]]
            filename = "{}{:0>4}{:0>2}{:0>2}.dat".format(
                conf_directory, str(cal_year), str(cursor_position[0] + 1), str(current_day))
            datestamp = cal_month[cursor_position[0]] + " " + str(current_day) + ", " + str(cal_year)
            if os.path.isfile(filename):
                screen.addstr(33, 1,
                              "{:^94s}".format(datestamp), curses.color_pair(3))
                rectangle(screen, 34, 0, max_y, 95)
                openfile = open(filename, 'r')
                contents = textwrap.wrap(decrypt(password, openfile.read()), width = 85, replace_whitespace = False)
                formatted_contents = []
                for i in range(0, len(contents)):
                    formatted_contents = formatted_contents + str.splitlines(contents[i])
                # textbox = [word for line in contents for word in line.split()]
                wordwrap = 1
                line = 35
                col = 3
                # 
                # for i in range(0, len(textbox)):
                #     wordwrap += len(textbox[i]) + 1
                #     if wordwrap > 85:
                #         line += 1
                #         wordwrap = 0
                #         col = 3
                #     if line < max_y:
                #         screen.addstr(line, col, str(textbox[i]))
                #         col += len(textbox[i]) + 1
                for i in range(0, len(formatted_contents)):
                    if i < 20:
                        screen.addstr(i + 36, 3, formatted_contents[i])
            else:
                screen.addstr(33, 1,
                              "{:^94s}".format(datestamp))

        # Calendar draw is done, refresh, get a key press, and get out
        screen.refresh()
        key_press = screen.getkey()
    screen.clear()


# Check for first run items.

# Check if configuration directory exists. If not, run the first run greeter.
conf_directory = os.environ['HOME'] + "/.damnJournal/"  # type: object
if not os.path.isdir(conf_directory):
    print("Welcome to damnJournal, of the Crass Office Suite. As a one time process, "
          "we are creating a configuration directory at {}").format(conf_directory)
    os.makedirs(conf_directory)
    if not os.path.isdir(conf_directory):
        print("Something went wrong. Please ensure damnJournal is running with permissions"
              "to create {}".format(conf_directory))

# Check if password file exists. If not, set the password.
passwd_file = conf_directory + "00000000.dat"
if not os.path.isfile(passwd_file):
    print("damnJournal will password protect and encode your journal entries. Please make a secure note of this"
          "password, as it can not be recovered under any circumstances.")
    print("")
    pass1 = str(getpass.getpass(prompt='Password: '))
    pass2 = str(getpass.getpass(prompt='Confirm Password: '))
    while pass1 != pass2:
        print("Passwords do not match. Please try again.")
	print("")
        pass1 = str(getpass.getpass(prompt='Password: '))
        pass2 = str(getpass.getpass(prompt='Confirm Password: '))
    # We now have matching passwords. Write the encrypted password to the passwd_file location

    password = pass1
    encrypted_data = encrypt(password, "Confirmed")
    try:
        openfile = open(passwd_file, 'w')
        openfile.write(encrypted_data)
        openfile.close
        openfile = open(conf_directory + "20180513.dat", 'w')
        sample_entry = """Dear Diary,

Today I was pompous and my sister was crazy. Today we were kidnapped by hillfolk never to be seen again.

It was the best day ever."""
        encrypted_data = encrypt(password, sample_entry)
        openfile.write(encrypted_data)
        openfile.close
    except IOError:
	print("Unable to write to {}. Please check the directory permissions and try again.").format(conf_directory)
        sys.exit()
    print("First run tasks complete. damnJournal will now exit.")
    sys.exit()


# Check the Password, start by opening the password file and pulling in the encrypted data.
openfile = open(passwd_file, 'r') # Open the password file.
enc_data = openfile.read() # Read the encoded data.
openfile.close() # Filestream is no longer needed. Closing.

password = getpass.getpass() # Prompt for the passowrd.
# Check the password against the confirmation file. If not, reprompt three times.
reprompt = 0

confirmed = decrypt(password, enc_data)

while confirmed != "Confirmed":
    try:
        confirmed = decrypt(password, enc_data)
    except simplecrypt.DecryptionException:
        print("Password incorrect.")
        confirmed = ""
        reprompt += 1
    if confirmed is not "Confirmed" and reprompt < 3:
        reprompt = reprompt + 1
        print("Password incorrect. Retry count: {}").format(str(reprompt))
        password = str(getpass.getpass())
    else:
        print("Failed to enter the correct password. Exiting.")
        sys.exit()


if dimensions:
    wrapper(main)
else:
    print("damnJournal requires a terminal at least 95 characters wide, and 40 characters tall.")

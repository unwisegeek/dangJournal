
import curses, calendar, datetime, os, sys, getpass, textwrap, string, random, base64, configparser, getopt, tarfile
from time import sleep
from curses import wrapper
from curses.textpad import rectangle
from simplecrypt import encrypt, decrypt

# Define global variables
password = ""
conf_directory = os.environ['HOME'] + "/.damnJournal/"  # type: object
temp_directory = conf_directory + "tmp/"
passwd_file = conf_directory + "00000000.dat"
config_file = conf_directory + "damnJournal.ini"
config = configparser.ConfigParser()
encryption_types = ["Plaintext", "Encoded", "Encrypted"]

def get_password(override=0):
    global password
    if config['Options']['Encryption'] == "3" or override == 1:
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
    else:
        password = ""

def dimensions(chkscreen):
    chkscreen = curses.initscr()
    max_x = curses.COLS - 1
    max_y = curses.LINES - 1

    if max_x < 100 or max_y < 40:
        return False
    else:
        return True

def tmp_generate(size=5, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def encode(password, type, text):
    if str(type) == "1":
        return text
    if str(type) == "2":
        return base64.encodestring(text)
    if str(type) == "3":
        return encrypt(password, text)

def decode(password, type, text):
    if str(type) == "1":
        return text
    if str(type) == "2":
        return base64.decodestring(text)
    if str(type) == "3":
        return decrypt(password, text)

def config_backup():
    # Backup the conf_directory
    # Create a timestamp
    timestamp = int((datetime.datetime(1970,1,1,0,0,0) - datetime.datetime.utcnow()).total_seconds()) * - 1
    backup_files = conf_directory + "bak/" + "djbackup-" + str(timestamp) + ".tar.gz"
    # command = "tar czf " + backup_files + " " + conf_directory + " &> /dev/null"
    print("Creating a backup at {}.".format(backup_files))
    # os.system(command)
    tar = tarfile.open(backup_files, "w:gz")
    # Get a list of files in the config directory
    files = os.listdir(conf_directory)
    for file in files:
        if ".dat" in file[-4:] or ".ini" in file[-4:]:
            tar.add(conf_directory + file)
    tar.close()

def make_passwd_file():
    global password
    # passwd_file = conf_directory + "00000000.dat"
    global passwd_file
    print("damnJournal will password protect and encode your journal entries. Please make a secure note of this "
          "password, as it can not be recovered under any circumstances.")
    print("")
    pass1 = str(getpass.getpass(prompt='New Password: '))
    pass2 = str(getpass.getpass(prompt='Confirm Password: '))
    while pass1 != pass2:
        print("Passwords do not match. Please try again.")
        print("")
        pass1 = str(getpass.getpass(prompt='New Password: '))
        pass2 = str(getpass.getpass(prompt='Confirm Password: '))
    # We now have matching passwords. Write the encrypted password to the passwd_file location
    password = pass1
    encrypted_data = encode(password, "3", "Confirmed")
    try:
        openfile = open(passwd_file, 'w')
        openfile.write(encrypted_data)
        openfile.close
    except IOError:
        print("Unable to write to {}. Please check the directory permissions and try again.").format(conf_directory)
        sys.exit()


def migrate(oldconfig, newconfig):
    global password
    print("Switching encryption from {} to {}.".format(encryption_types[int(oldconfig) - 1], encryption_types[int(newconfig) - 1]))
    # Make a backup of all config files
    config_backup()
    sleep(2)
    # Get a list of files in the config directory
    files = os.listdir(conf_directory)
    datfiles = [] 
    # Parse the list so there are only .dat files that aren't 00000000.dat
    for file in files:
        if ".dat" in file[-4:] and file != "00000000.dat":
            datfiles += [ file ]
    if oldconfig == "1": # Plaintext to...
        if newconfig == "2": # ...Base64
            for file in datfiles:
                openfile = open(conf_directory + "/" + file, 'r') # Open the file to be migrated for reading/writing
                contents = openfile.read() # Read the encoded file contents
                openfile.close()
                decoded_contents = decode(password, 1, contents) # Decode the contents with the old encoding scheme
                encoded_contents = encode(password, 2, decoded_contents) # Encode the decoded contents with the new encoding scheme
                openfile = open(conf_directory + "/" + file, 'w') # Open the file to be migrated for reading/writing
                openfile.write(encoded_contents) # Write the new encoded contents to the file
                openfile.close() # Close the filestream
        if newconfig == "3": # ...Simple-Crypt
            if os.path.isfile(passwd_file):
                choice = ""
                while choice.lower() != "y" and choice.lower() != "n":
                    choice = str(raw_input("We found a password already defined. Keep this password? (y/n) "))
                if choice == "n":
                    # Make a new 00000000.dat file
                    make_passwd_file()
                if choice == "y":
                        get_password(1)
            else:
                # Make a new 00000000.dat file
                make_passwd_file()
            # Password file is created. Migrate the files.
            for file in datfiles:
                openfile = open(conf_directory + "/" + file, 'r') # Open the file to be migrated for reading/writing
                contents = openfile.read() # Read the encoded file contents
                openfile.close()
                decoded_contents = decode("", 1, contents) # Decode the contents with the old encoding scheme
                encoded_contents = encode(password, 3, decoded_contents) # Encode the decoded contents with the new encoding scheme
                openfile = open(conf_directory + "/" + file, 'w') # Open the file to be migrated for reading/writing
                openfile.write(encoded_contents) # Write the new encoded contents to the file
                openfile.close() # Close the filestream

    if oldconfig == "2": # Base64 to...
        if newconfig == "1": # ...Plaintext
            for file in datfiles:
                openfile = open(conf_directory + "/" + file, 'r') # Open the file to be migrated for reading/writing
                contents = openfile.read() # Read the encoded file contents
                openfile.close()
                decoded_contents = decode(password, 2, contents) # Decode the contents with the old encoding scheme
                encoded_contents = encode(password, 1, decoded_contents) # Encode the decoded contents with the new encoding scheme
                openfile = open(conf_directory + "/" + file, 'w') # Open the file to be migrated for reading/writing
                openfile.write(encoded_contents) # Write the new encoded contents to the file
                openfile.close() # Close the filestream
        if newconfig == "3": # ...Simple-Crypt
            if os.path.isfile(passwd_file):
                choice = ""
                while choice.lower() != "y" and choice.lower() != "n":
                    choice = str(raw_input("We found a password already defined. Keep this password? (y/n) "))
                if choice == "n":
                    # Make a new 00000000.dat file
                    make_passwd_file()
                if choice == "y":
                        get_password(1)
            else:
                # Make a new 00000000.dat file
                make_passwd_file()            # Password file is created. Migrate the files.

            for file in datfiles:
                openfile = open(conf_directory + "/" + file, 'r') # Open the file to be migrated for reading/writing
                contents = openfile.read() # Read the encoded file contents
                decoded_contents = decode("", 2, contents) # Decode the contents with the old encoding scheme
                encoded_contents = encode(password, 3, decoded_contents) # Encode the decoded contents with the new encoding scheme
                openfile = open(conf_directory + "/" + file, 'w') # Open the file to be migrated for reading/writing
                openfile.write(encoded_contents) # Write the new encoded contents to the file
                openfile.close() # Close the filestream

    if oldconfig == "3": # Simple-Crypt to...
        # Get the password for decryption functions.
        get_password(1)
        if newconfig == "1": # ...Plaintext
            for file in datfiles:
                openfile = open(conf_directory + "/" + file, 'r') # Open the file to be migrated for reading/writing
                contents = openfile.read() # Read the encoded file contents
                openfile.close()
                decoded_contents = decode(password, 3, contents) # Decode the contents with the old encoding scheme
                encoded_contents = encode("", 1, decoded_contents) # Encode the decoded contents with the new encoding scheme
                openfile = open(conf_directory + "/" + file, 'w') # Open the file to be migrated for reading/writing
                openfile.write(encoded_contents) # Write the new encoded contents to the file
                openfile.close() # Close the filestream
        if newconfig == "2": # ...Base64
            for file in datfiles:
                openfile = open(conf_directory + "/" + file, 'r') # Open the file to be migrated for reading/writing
                contents = openfile.read() # Read the encoded file contents
                openfile.close()
                decoded_contents = decode(password, 3, contents) # Decode the contents with the old encoding scheme
                encoded_contents = encode("", 2, decoded_contents) # Encode the decoded contents with the new encoding scheme
                openfile = open(conf_directory + "/" + file, 'w') # Open the file to be migrated for reading/writing
                openfile.write(encoded_contents) # Write the new encoded contents to the file
                openfile.close() # Close the filestream

def configure(config_exists):
    global config
    if config_exists: # Configuration exists.
        curencryption = config['Options']['Encryption']
        choice = [0, 0]
        print("Starting configuration.\n\ndamnJournal has three different methods by which to store your journal entries.\n\n"
              "1. Plaintext...Fastest of the configurations, but offers no protection for sensitive data contained within journal entries.\n"
              "2. Encoded.....Base64 encoded. Protects only against the most casual of attacks.\n"
              "3. Encrypted...AES encryption based on the simple-crypt library. Much slower. Previews are recommended turned off.\n\n")
        print("Current Selection: {}".format(encryption_types[int(curencryption) - 1]))
        choice[0] = str(raw_input("Please choose 1, 2, 3, or Q to quit: "))
        if choice[0].lower() == "q":
            sys.exit()
        if choice[0] in "1,2,3":
            newencryption = choice[0]
            if curencryption != newencryption:
                print("Applying changes, backing up current entries, migrating entries, and exiting to system.")
                config['Options']['Encryption'] = choice[0]
                migrate(curencryption, newencryption)
                with open(config_file, 'w') as configfile:
                    config.write(configfile)
                sys.exit()
        else:
            print("Invalid entry. Aborting.")
            sys.exit()
        print("\n\ndamnJournal features a preview of each journal entry. Based on the encryption scheme above, you want to disbale this.\n\n"
              "1. Enabled\n"
              "2. Disabled\n\n")
        print("Current Selection: {}".format(config['Options']['Preview']))
        while choice[1] not in "12qQ":
            choice[1] = str(raw_input("Please choose 1, 2, or Q to quit: "))
        if choice[1] in "1":
            config['Options']['Preview'] = "On"
        elif choice[1] in "2":
            config['Options']['Preview'] = "Off"
        elif choice[1].lower() in "q":
            sys.exit()
        else:
            print("Error. Exiting to system.")
            sys.exit()
        print("Configuration complete. Writing configuration file now.")
        with open(config_file, 'w') as configfile:
            config.write(configfile)

    else: # Configuration does not exist. Fresh start.
        choice = ["0", "0"]
        config['Options'] = {}
        print("Starting configuration.\n\ndamnJournal has three different methods by which to store your journal entries.\n\n"
              "1. Plaintext...Fastest of the configurations, but offers no protection for sensitive data contained within journal entries.\n"
              "2. Encoded.....Base64 encoded. Protects only against the most casual of attacks.\n"
              "3. Encrypted...AES encryption based on the simple-crypt library. Much slower. Previews are recommended turned off.\n\n"
              "Once decided, all future operations with damnJournal will depend on this setting. Please read the manual for guidance on \n"
              "how to migreate from one entry schema to another.\n")
        while str(choice[0]) in "0":
            choice[0] = str(raw_input("Please choose 1, 2, 3, or Q to quit: "))
        if choice[0].lower() in "q":
            sys.exit()
        elif choice[0] in "1,2,3":
            encopt = int(choice[0])
            config['Options']['Encryption'] = str(encopt)
        elif choice[0] == "3": # Special process for Encrypted journals
            passwd_file = conf_directory + "00000000.dat"
            make_passwd_file()
        else:
            print("No valid input detected. Exiting.")
            sys.exit()

        openfile = open(conf_directory + "20180513.dat", 'w')
        sample_entry = "Dear Diary,\n\nToday I was pompous and my sister was crazy. Today we were kidnapped by hillfolk never to be seen again.\n\nIt was the best day ever."
        encrypted_data = encode(password, encopt, sample_entry)
        openfile.write(encrypted_data)
        openfile.close
        print("\n\ndamnJournal features a preview of each journal entry. Based on the encryption scheme above, you want to disbale this.\n\n"
              "1. Enabled\n"
              "2. Disabled\n\n")
        while str(choice[1]) in "0":
            choice[1] = str(raw_input("Please choose 1, 2, or Q to quit: "))
        if choice[1].lower() in "q,Q":
            sys.exit()
        elif choice[1] in "1":
            config['Options']['Preview'] = "On"
        elif coice[1] in "2":
            config['Options']['Preview'] = "Off"
        else:
            print("No valid input detected. Exiting.")
            sys.exit()
        print("Configuration complete. Writing configuration file now.")
        with open(config_file, 'w') as configfile:
            config.write(configfile)


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
            tmpfile = '{}dj_{}'.format(temp_directory, tmp_generate())
            if os.path.isfile(filename):
                openfile = open(filename, 'r') # Start working with the current file, as exists in the configuration directory
                contents = decode(password, enctype, openfile.read())
                openfile.close() # Close the current file
                openfile = open(tmpfile, 'w')  # Open the temporary file, write the contents of the current file into it for editing
                openfile.write(contents)
                openfile.close() # Close the temporary file
                os.system("editor " + tmpfile) # Edit the temporary file in the system editor
                openfile = open(tmpfile, 'r') # Open the temporary file, read the contents, encrypt it, and then write to the current file
                contents = encode(password, enctype, openfile.read())
                openfile.close()
                openfile = open(filename, 'w')
                openfile.write(contents)
                openfile.close() # Close the file
                os.system("rm -f {}".format(tmpfile)) # Clean up the temp directory
            else:
                openfile = open(tmpfile, 'w')
                openfile.write("")
                openfile.close()
                os.system("editor " + tmpfile)
                openfile = open(tmpfile, 'r')
                contents = encode(password, enctype, openfile.read())
                openfile.close()
                openfile = open(filename, 'w')
                openfile.write(contents)
                openfile.close()
                os.system("rm -f {}".format(tmpfile))

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
            if os.path.isfile(filename) and config['Options']['Preview'] == "On":
                screen.addstr(33, 1,
                              "{:^94s}".format(datestamp), curses.color_pair(3))
                rectangle(screen, 34, 0, max_y, 95)
                openfile = open(filename, 'r')
                contents = textwrap.wrap(decode(password, enctype, openfile.read()), width = 85, replace_whitespace = False)
                formatted_contents = []
                for i in range(0, len(contents)):
                    formatted_contents = formatted_contents + str.splitlines(contents[i])
                # textbox = [word for line in contents for word in line.split()]
                for i in range(0, len(formatted_contents)):
                    if i in range(0, max_y - 36):
                        screen.addstr(i + 36, 3, formatted_contents[i])
            else:
                screen.addstr(33, 1,
                              "{:^94s}".format(datestamp))

        # Calendar draw is done, refresh, get a key press, and get out
        screen.refresh()
        key_press = screen.getkey()
    screen.clear()



# Check the configuration
config.read(config_file)

try:
    enctype = config['Options']['Encryption']
except KeyError:
    print("No configuration setting for encryption found. Have your ran damnJournal with the --configure flag?")

# Check for first run items.

# Check if configuration directory exists. If not, run the first run greeter.
if not os.path.isdir(conf_directory):
    print("Welcome to damnJournal, of the Crass Office Suite. As a one time process, "
          "we are creating a configuration directory at {}\n").format(conf_directory)
    os.makedirs(conf_directory)
if not os.path.isdir(temp_directory):
    print("We also creating a temporary and backup directory at {}\n").format(temp_directory)
    os.makedirs(conf_directory + 'tmp/')
if not os.path.isdir(conf_directory + 'bak/'):
    print("Creating directory for backups.")
    os.makedirs(conf_directory + 'bak/')
    if not os.path.isdir(conf_directory):
        print("Something went wrong. Please ensure damnJournal is running with permissions "
              "to create {}".format(conf_directory))
        sys.exit()
    if not os.path.isdir(temp_directory):
        print("Something went wrong. Please ensure damnJournal is running with permissions "
              "to create {}".format(temp_directory))
        sys.exit()
    if not os.path.isdir(conf_directory + 'bak/'):
        print("Something went wrong. Please ensure damnJournal is running with permissions "
              "to create {}".format(temp_directory))
        sys.exit()

if not os.path.isfile(config_file) and "--configure" not in sys.argv:
    print("damnJournal does not have a configuration file. We will now exit. Please run damnJournal with "
          "the following argument: python damnJournal.py --configure")
    sys.exit()

if "--configure" in sys.argv:
    configure(os.path.isfile(config_file))
    sys.exit()

if "--backup" in sys.argv:
    config_backup()
    sys.exit()


# Check the Password, start by opening the password file and pulling in the encrypted data.
if config['Options']['Encryption'] == "3":
    get_password()
else:
    password = ""


if dimensions:
    wrapper(main)
else:
    print("damnJournal requires a terminal at least 95 characters wide, and 40 characters tall.")

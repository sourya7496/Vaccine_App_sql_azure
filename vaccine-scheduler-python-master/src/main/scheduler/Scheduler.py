from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None

def check_password(password):
    valid_password = True
    special_characters = "!@#?"

    if len(password) < 8:
        print("Password must be at least 8 characters")
        valid_password = False

    has_uppercase = False
    has_digit = False
    has_special_char = False

    for char in password:
        if char.isupper():
            has_uppercase = True
        if char.isdigit():
            has_digit = True
        if char in special_characters:
            has_special_char = True

    if not has_uppercase:
        print("Password must have at least 1 capital letter")
        valid_password = False

    if not has_digit:
        print("Password must have at least 1 number")
        valid_password = False

    if not has_special_char:
        print("Password must have at least 1 special character from (!, @, #, ?)")
        valid_password = False

    return valid_password
    
def create_patient(tokens):
    """
    Part 1
    """
    if len(tokens) != 3:
        print("Failed to create patient.")
        return

    username = tokens[1]
    password = tokens[2]

    
    # check 2: check if the username has been taken already
    if username_exists_patients(username):
        print("Username taken, try again!")
        return
    if not check_password(password):  # Password must be valid to continue
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    patient = Patient(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        patient.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)

def username_exists_patients(username):
    cm = ConnectionManager()
    conn = cm.create_connection()
    select_username = "SELECT username FROM Patients WHERE username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username.lower())
        for row in cursor:
            if row['Username'] is not None:
                print("Username already taken! Try again.")
                cm.close_connection()
                return
    except pymssql.Error as e:
        print("Error occurred when checking username availability")
        print("Db-Error:", e)
        return
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False

    cm.close_connection()
def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return
    if not check_password(password):  # Password must be valid to continue
        return
    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)


def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False



def login_patient(tokens):
    """
    TODO: Part 1
    """
    global current_patient
    if current_patient is not None or current_caregiver is not None:
        print("User already logged in.")
        return

    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    if patient is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_patient = patient
        patient_menu()



def login_caregiver(tokens):
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if caregiver is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_caregiver = caregiver
        caregiver_menu


def search_caregiver_schedule(tokens):
    """
    TODO: Part 2
    """
   ## if current_patient == current_caregiver:
   ##     print("Please login before executing this task!")
   ##     return
    if len(tokens) != 2:
        print("Please check credentials!")
        return

    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)
    try:
        given_date = tokens[1].split("-")
        month = int(given_date[0])
        day = int(given_date[1])
        year = int(given[2])
        dt = datetime.datetime(year, month, day)

        get_available_dates = "SELECT date, username FROM Availabilities WHERE date = %s ORDER BY username"
        get_vaccines = "SELECT Name, Doses FROM Vaccines"

        cursor.execute(get_available_dates, dt) ##Check available dates from the date input by the user
        availability_rows = cursor.fetchall()
        cursor.execute(get_vaccines) ##Get all vaccines available
        vaccine_rows = cursor.fetchall()

        if len(availability_rows) == 0:  # If there is no availability
            print("There are no appointments available on", tokens[1])
            return

        for row1 in availability_rows:
            print(row1['username'])  ##Printing available caregivers for the corresponding date
        for row2 in vaccine_rows:
            print(row2['Doses'])  ##Printing available Dose of Vaccines.


    except pymssql.Error as e:
        print("Availability Check failed.")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please check the date format, it should be mm-dd-yyyy")
        return
    except Exception as e:
        print("Availability Check failed.")
        print("Error:", e)
        return
    finally:
        cm.close_connection()



def reserve(tokens):
    """
    TODO: Part 2
    """
    # First: check valid arguments / login requirements
    if current_patient == current_caregiver:
        print("Please login first before reserving an appointment")
        return
    if current_patient is None:
        print("Please login as a patient to reserve an appointment")
        return
    if len(tokens) != 3:
        print("Please check your entry!")
        return
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)
    try:
        # Second: Parse the date and attempt to retrieve date, caregiver, and vaccine name from the database
        given_date = tokens[1].split("-")
        month = int(date_whole[0])
        day = int(date_whole[1])
        year = int(date_whole[2])
        dt = datetime.datetime(year, month, day)
        available_dates = "SELECT date, username FROM Availabilities WHERE date = %s ORDER BY username LIMIT 1"
        cursor.execute(available_dates, dt)
        av_dates = cursor.fetchall()
        if len(av_dates) == 0:
            print("There are no caregivers available for this date")
            return
        assigned_caregiver = av_dates[0]['username']
        assigned_date = av_dates[0]['date']
        vaccine_name = tokens[2]
        vaccine = Vaccine(vaccine_name, available_doses=None).get()

        # Third: Check vaccine is valid and if it is remove 1 from the supply
        if vaccine is None:
            print("Our caregivers do not have this vaccine. Try again inputting a valid vaccine from this list:")
            cursor.execute("SELECT Name FROM Vaccines")
            for row in cursor:
                print(row['Name'])
            return
        if vaccine.available_doses == 0:
            print("Sorry, we donot have the vaccine!")
            return
        vaccine.decrease_available_doses(1)

        # 4th: Add appointment to appointment database. ID is just 1 + the highest id number
        add_appointment = "INSERT INTO Appointments VALUES (%d, %s, %s, %s, %s)"
        temp_cursor = conn.cursor()
        temp_cursor.execute("SELECT MAX(appointment_id) FROM Appointments")
        highest_row = temp_cursor.fetchone()[0]
        if highest_row is None:
            cursor.execute(add_appointment, (1
                                             , assigned_date, current_patient.username, assigned_caregiver,
                                             vaccine_name))
        else:
            cursor.execute(add_appointment, (highest_row + 1
                                             , assigned_date, current_patient.username, assigned_caregiver,
                                             vaccine_name))

        # 5th: Drop that caregiver's availability from the availability database
        drop_availability = "DELETE FROM Availabilities WHERE date = %s AND username = %s"
        cursor.execute(drop_availability, (dt, assigned_caregiver))

        conn.commit()

        get_appointment = "SELECT appointment_id, date, cid, vaccine_name FROM appointments WHERE pid = %s AND cid = %s AND date = %s"
        cursor.execute(get_appointment, (current_patient.username, assigned_caregiver, assigned_date))
        for row3 in cursor:
            print((row3['appointment_id'], str(row3['date']), row3['cid'], row['vaccine_name']))

    except pymssql.Error as e:
        print("Error trying to create appointment; try again")
        print("DBError:", e)
        return
    except ValueError as e:
        print("Date should be in format mm-dd-yyyy. Please check!")
        print("Error:", e)
        return
    except Exception as e:
        print("Error occurred when creating an appointment; try again")
        print("Error:", e)
        return
    finally:
        cm.close_connection()



def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        current_caregiver.upload_availability(d)
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
        return
    print("Availability uploaded!")


def cancel(tokens):
    """
    TODO: Extra Credit
    """
    if current_patient == current_caregiver:
        print("Please login first!")
        return
    if len(tokens) != 2:
        print("Please check your entry")
        return
    try:
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)
        cancel_id = tokens[1]

        # Check 1: check that the user's desired appointment id is actually in their own appointments
        fetch_appointment = "SELECT appointment_id, date, pid, cid, vaccine_name FROM Appointments WHERE appointment_id = %d"
        cursor.execute(fetch_appointment, cancel_id)
        appointment = cursor.fetchone()
        valid_appointment = False
        if current_patient is not None:
            if appointment['pid'] == current_patient.username:
                valid_appointment = True
            else:
                print("There is no such ID in the database, please check again!", cancel_id)
        elif current_caregiver is not None:
            if appointment['cid'] == current_caregiver.username:
                valid_appointment = True
            else:
                print("There is no such ID in the database, please check again!", cancel_id)

        # If valid appointment id, then delete that appointment while replenishing the respective vaccine supply (+1)
        if valid_appointment:
            delete_appointment = "DELETE FROM Appointments WHERE appointment_id = %d"
            vaccine = Vaccine(appointment['vaccine_name'], None).get()
            vaccine.increase_available_doses(1)  
            cursor.execute(delete_appointment, cancel_id)
            conn.commit()
            print("Appointment successfully cancelled.")
            if current_patient is not None:  # If a patient canceled that appointment, add the availability back to caregiver
                appointment_date = appointment['date']
                caregiver = appointment['cid']
                cursor.execute("INSERT INTO Availabilities VALUES (%d, %d)", (appointment_date, caregiver))
                conn.commit()
        else:
            print("There is no such ID in the database, please check again!", cancel_id)
    except pymssql.Error as e:
        print("Failed to retrieve appointment information")
        print("DBError:", e)
    except Exception as e:
        print("There is no such ID in the database, please check again!", cancel_id)
    finally:
        cm.close_connection()


def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Error occurred when adding doses")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when adding doses")
        print("Error:", e)
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    print("Doses updated!")


def show_appointments(tokens):
    '''
    TODO: Part 2
    '''
    if current_patient == current_caregiver:
        print("Please login first!")
        return
    if len(tokens) != 1:
        print("Please check your entry")
        return
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)
    try:
        if current_patient is not None:
            # Attempt to get appointments for the current logged in patient and then print them
            get_patient_appointments = "SELECT appointment_id, vaccine_name, date, cid FROM Appointments WHERE pid = %s ORDER BY appointment_id"
            cursor.execute(get_patient_appointments, current_patient.username)
            appointments = cursor.fetchall()
            if len(appointments) == 0:
                print("There are no appointments scheduled")
                return

            for i in range(0, len(appointments)):
                print(appointments[i]['appointment_id'], appointments[i]['vaccine_name'], str(appointments[i]['date']), appointments[i]['cid'])

        elif current_caregiver is not None:
            # Attempt to get the appointments for the current logged in caregiver.
            get_caregiver_appointments = "SELECT appointment_id, vaccine_name, date, pid FROM Appointments WHERE cid = %s ORDER BY appointment_id"
            cursor.execute(get_caregiver_appointments, current_caregiver.username)
            appointments = cursor.fetchall()
            if len(appointments) == 0:
                print("There are no appointments scheduled")
                return
            print("-" * (len(appointments) * 20))
            print("{: >10}\t{: >10}\t{: >10}\t{: >10}\t".format("Appointment ID", "Vaccine", "Date", "Patient"), end="")
            print("")
            for i in range(0, len(appointments)):
                print(appointments[i]['appointment_id'], appointments[i]['vaccine_name'], str(appointments[i]['date']), appointments[i]['pid'])

    except pymssql.Error as e:
        print("Error occured when checking appointments")
        print("DBError:", e)
    except Exception as e:
        print("Error occured while showing appointments")
        print("Error:", e)
    finally:
        cm.close_connection()


def logout(tokens):
    """
    TODO: Part 2
    """
    global current_patient
    global current_caregiver
    try:
        if current_patient != current_caregiver:
            current_patient = None
            current_caregiver = None
            print("Successfully logged out!")
            base_menu()
        else:
            print("Please login!")
    except Exception as e:
        print("Error occured while logging out!")
        print("Error:", e)
    return


def start():
    stop = False
    print()
    print(" *** Please enter one of the following commands *** ")
    print("> create_patient <username> <password>")  # //TODO: implement create_patient (Part 1)
    print("> create_caregiver <username> <password>")
    print("> login_patient <username> <password>")  # // TODO: implement login_patient (Part 1)
    print("> login_caregiver <username> <password>")
    print("> search_caregiver_schedule <date>")  # // TODO: implement search_caregiver_schedule (Part 2)
    print("> reserve <date> <vaccine>")  # // TODO: implement reserve (Part 2)
    print("> upload_availability <date>")
    print("> cancel <appointment_id>")  # // TODO: implement cancel (extra credit)
    print("> add_doses <vaccine> <number>")
    print("> show_appointments")  # // TODO: implement show_appointments (Part 2)
    print("> logout")  # // TODO: implement logout (Part 2)
    print("> Quit")
    print()
    while not stop:
        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break

        response = response.lower()
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Please try again!")
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == cancel:
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Bye!")
            stop = True
        else:
            print("Invalid operation name!")


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()

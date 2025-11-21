import sqlite3
import re
import time

conn = sqlite3.connect('contacts.db')
c = conn.cursor()

def add_contact():
    while True:
        f_name = input("Enter first name: ").lower().strip()
        l_name = input("Enter last name: ").lower().strip()
        if f_name == "" or l_name == "" or search_contact_with_f_name(f_name):
            print("Enter a valid first name or last name.")
        else:
            break

    while True:
        phone = input("Enter phone number(1112223333): ")
        if validate_phone_number(phone):
            phone = validate_phone_number(phone)
            if search_phone_number(phone):
                print("Phone number already in use, please try again with a different phone number.")
            else:
                break
        else:
            print("Invalid phone number")

    while True:
        email = input("Enter email address: ")
        if validate_email(email):
            break
        else:
            print("Invalid email address")

    c.execute('''INSERT INTO contacts (first_name, last_name, phone_number, email) VALUES (?,?,?,?)''', (f_name, l_name, phone, email))
    print("Contact added successfully")

def load_contact():
    c.execute('''SELECT * FROM contacts ORDER BY first_name ASC''')
    return c.fetchall()

def search_contact_with_f_name(name):
    c.execute('''SELECT * FROM contacts WHERE first_name = ?''', (name,))
    return c.fetchall()


def view_contacts(contacts):
    count = 1
    for contact in contacts:
        print(f'{count}. {contact[1].capitalize()} {contact[2].capitalize()}({contact[4]}) - {contact[3]}')
        count += 1

def search_phone_number(contact):
    c.execute('''SELECT * FROM contacts WHERE phone_number = ?''', (contact,))
    return c.fetchall()


def delete_contact(contacts):
    f_name = input("What's the first name of the contact you are trying to delete? ").strip().lower()
    c.execute("SELECT * FROM contacts WHERE first_name = ?", (f_name,))
    search_result = c.fetchall()
    if not search_result:
        print("No such contact")
        return
    elif len(search_result) == 1:
        view_contacts(search_result)
        confirmation_response = input("Are you sure you want to delete this contact? (y/n): ").lower()
        if confirmation_response == 'y':
            c.execute("DELETE FROM contacts WHERE id = ?", (search_result[0][0],))
            print("Deleted successfully")
            conn.commit()
            return
        elif confirmation_response == 'n':
            return delete_contact(contacts)
        else:
            print("Invalid input")
            return delete_contact(contacts)

    elif len(search_result) > 1:
        view_contacts(search_result)
        l_name = input("What's the last name of the contact you are trying to delete? ").strip().lower()
        c.execute("SELECT * FROM contacts WHERE first_name = ? AND last_name = ?", (f_name, l_name))
        refined_search_result = c.fetchall()
        if not refined_search_result:
            print("No such contact")
            return delete_contact(contacts)
        elif len(refined_search_result) == 1:
            view_contacts(refined_search_result)
            confirmation_response = input("Are you sure you want to delete this contact? (y/n): ").lower()
            if confirmation_response == 'y':
                c.execute("DELETE FROM contacts WHERE id = ?", (refined_search_result[0][0],))
                print("Deleted successfully")
                conn.commit()
                print("Succesfully deleted contact")
                return
            elif confirmation_response == 'n':
                return delete_contact(contacts)
            else:
                print("Invalid input")
                return delete_contact(contacts)

        elif len(refined_search_result) > 1:
            view_contacts(refined_search_result)
            p_number = input("What's the phone number you are trying to delete? ").strip()
            formatted_p_number = validate_phone_number(p_number)
            c.execute("SELECT * FROM contacts WHERE phone_number = ?", (formatted_p_number,))
            p_refined_search_result = c.fetchall()
            if not p_refined_search_result:
                print("No such contact")
                return delete_contact(contacts)
            elif len(p_refined_search_result) == 1:
                view_contacts(p_refined_search_result)
                confirmation_response = input("Are you sure you want to delete this contact? (y/n): ").lower()
                if confirmation_response == 'y':
                    c.execute("DELETE FROM contacts WHERE phone_number = ?", (formatted_p_number,))
                    print("Deleted successfully")
                    conn.commit()
                    print("Succesfully deleted contact")
                    return
            else:
                print("Couldn't find the contact you are trying to delete, please try again.")
                return

def validate_phone_number(phone):
    PHONE_REGEX = re.compile(r'^\d{10}$')
    phone = phone.strip()

    if phone and PHONE_REGEX.match(phone) is not None:
        return f"+1 ({phone[:3]}) {phone[3:6]}-{phone[6:]}"
    else:
        return


def validate_email(email):
    EMAIL_REGEX = re.compile(
        r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    )
    if not isinstance(email, str):
        return False
    email = email.strip()
    if not email or len(email) > 254:
        return False
    return EMAIL_REGEX.match(email) is not None

def update_f_name(contact):
    while True:
        first_name = input("Enter first name: ")
        if first_name == "" or search_contact_with_f_name(first_name):
            print("first name already in use, please try again with a different name.")
            return update_f_name(contact)
        else:
            c.execute("""UPDATE contacts SET first_name = ? WHERE id = ?""", (first_name, contact[0]))
            conn.commit()
            print("Updated successfully")
            return

def update_l_name(contact):
    while True:
        last_name = input("Enter last name: ")
        if last_name == "":
            print("last name cannot be empty")
            return update_l_name(contact)
        else:
            c.execute("""UPDATE contacts SET last_name = ? WHERE id = ?""", (last_name, contact[0]))
            conn.commit()
            print("Updated successfully")
            return

def update_email(contact):
    while True:
        email = input("Enter email: ")
        if not validate_email(email):
            print("Invalid email")
            return update_email(contact)
        else:
            c.execute("""UPDATE contacts SET email = ? WHERE id = ?""", (email, contact[0]))
            conn.commit()
            print("Updated successfully")

def update_phone_number(contact):
    while True:
        number = input("Enter phone number: ")
        formatted_number = validate_phone_number(number)
        if not formatted_number or search_phone_number(formatted_number):
            print("Invalid phone number")
            return update_phone_number(contact)
        else:
            number = validate_phone_number(number)
            c.execute("""UPDATE contacts SET phone_number = ? WHERE id = ?""", (number, contact[0]))
            conn.commit()
            print("Updated successfully")

def update_helper(search_results):
    print(f"\n1. First name\n2. Last name\n3. Phone number\n4. Email")
    to_be_updated = input("What would you like to be updated(enter a number): ")
    if to_be_updated == "1":
        update_f_name(search_results[0])
    elif to_be_updated == "2":
        update_l_name(search_results[0])
    elif to_be_updated == "3":
        update_phone_number(search_results[0])
    elif to_be_updated == "4":
        update_email(search_results[0])

def update_contact(contacts):
    f_name = input("What's the first name of the contact you are trying to update? ").strip().lower()
    print()
    search_results = search_contact_with_f_name(f_name)
    if not search_results:
        print("No such contact")
        return update_contact(contacts)
    elif len(search_results) == 1:
        view_contacts(search_results)
        update_helper(search_results)
        return
    elif len(search_results) > 1:
        view_contacts(search_results)
        print("multiple contacts found")
        phone_number = input("What's the phone number you are trying to update? ").strip()
        formatted_phone_number = validate_phone_number(phone_number)
        refined_search_result = search_phone_number(formatted_phone_number)
        if not formatted_phone_number or not refined_search_result:
            print("Invalid phone number")
            return update_contact(contacts)
        elif len(refined_search_result) == 1:
            view_contacts(refined_search_result)
            update_helper(search_results)
            return

def main():

    #make sure a table for contacts exist
    c.execute(
        f'''CREATE TABLE IF NOT EXISTS contacts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        last_name TEXT,
        phone_number TEXT,
        email TEXT)
        ''')

    print("Welcome to the contacts database")
    while True:
        contacts = load_contact()
        print(f" 1. Add a contact\n 2. View contacts\n 3. Update contacts\n 4. Delete Contact\n 5. Search contact using first name\n 6. Exit")
        menu_option = input("What would you like to do? (enter a number): ")
        if menu_option == "1":
            add_contact()
        elif menu_option == "2":
            print()
            view_contacts(contacts)
            time.sleep(5)
        elif menu_option == "3":
            update_contact(contacts)
        elif menu_option == "4":
            delete_contact(contacts)
        elif menu_option == "5":
            first_name = input("Enter first name: ")
            view_contacts(search_contact_with_f_name(first_name))
        elif menu_option == "6":
            conn.commit()
            exit(0)
        else:
            print("Invalid input")
        time.sleep(2)
        print()

if __name__ == "__main__":
    main()
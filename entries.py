"""
Author: Diallo West
Date Created: April 24, 2016
Title: Work log with a Database
Description: 
    Create a command line application that will allow employees to enter their name, time worked, task worked on, and general notes about the task into a database. There should be a way to add a new entry, list all entries for a particular employee, and list all entries that match a date or search term. Print a report of this information to the screen, including the date, title of task, time spent, employee, and general notes."""

from collections import OrderedDict
from datetime import datetime
import os

from peewee import *

db = SqliteDatabase('worklog.db')
entries = []


class Entry(Model):
    pk = PrimaryKeyField()
    employee_name = CharField(max_length=75)
    task_name = CharField(max_length=75)
    time = IntegerField()
    date = DateField(default=datetime.now)
    notes = TextField(null=True)

    class Meta:
        database = db


def initialize():
    db.connect()
    db.create_tables([Entry], safe=True)


def prompt_menu():
    """Shows the main menu"""
    choice = None

    while choice != 'q':
        clear()
        print("Enter 'q' to quit.")
        for key, value in menu.items():
            print('{}) {}'.format(key, value.__doc__))
        choice = input("Action: \n").lower().strip()

        if choice in menu:
            clear()
            menu[choice]()


def new_entry():
    """Create a new entry"""
    clear()
    employee = add_name()
    task_ent = add_task()
    time_ent = add_time()
    date_ent = add_date()
    notes_ent = add_notes()

    entry = {
        'employee_name': employee,
        'task_name': task_ent,
        'time': time_ent,
        'date': date_ent,
        'notes': notes_ent,
    }

    add_entry_summary(entry)

    while True:
        save = input("Would you like to save? [Y/n] \n").lower().strip()
        if save == 'y':
            input('\nEntry was saved. Press ENTER to continue.\n')
            return entry
        else:
            input('\nEntry was not saved. Press ENTER to continue. \n')
            return None


def add_task():
    while True:
        clear()
        task_ent = input("What do you want to call this task?\n").strip()
        if not task_ent:
            input("You must enter a task name. Press enter. ")
        else:
            return task_ent


def add_time():
    while True:
        clear()
        time_ent = input("Enter the number of minutes for the task.\n")
        try:
            int(time_ent)
        except ValueError:
            input("You must enter integers only. Press enter. ")
        else:
            return time_ent


def add_notes():
    """Asks for notes"""
    clear()
    notes_ent = input("Enter your notes.  (ENTER if none)\n")
    return notes_ent


def add_name():
    clear()
    while True:
        employee = input("Enter a name.  Then hit enter,"
                         " hit enter [Q] to go back\n").strip()
        if employee.lower() == 'q':
            prompt_menu()
            break
        elif not employee:
            input("You must enter a name. Press enter.")
        else:
            return employee


def add_date():
    clear()
    while True:
        date_ent = input("Enter a date "
                         "Date format MM/DD/YYYY\n").strip()
        try:
            date_ent = datetime.strptime(date_ent, '%m/%d/%Y').date()
        except ValueError:
            input("Sorry, that's not a valid date.  Use MM/DD/YYYY format.")
            continue
        if date_ent > datetime.now().date():
                input("Sorry you cannot select"
                      " a date in the futue.  Press enter")
                continue
        else:
            return date_ent


def add_entry_summary(entry):
    clear()
    print("Are these entries correct?\n")
    print("""
            Name: {employee_name}
            Task Name: {task_name}
            Time: {time}
            Notes: {notes}
            Date: {date}
            """.format(**entry))


def save_entry():
    """Entry saved in database"""
    entry = new_entry()
    if entry:
        return create_entry(entry)


def create_entry(entry):
    """Creates an entry"""
    Entry.create(**entry)
    return entry


def get_entries():
    """Gets the entries in the database sorted by date"""
    entries = []
    entry = Entry.select().order_by(Entry.date.desc())
    for ent in entry:
        entries.append(ent)
    return entries


def get_search_entries(search):
    """Gets the entries for each search"""
    entries = []
    entry = Entry.select().order_by(Entry.date.desc())
    entry = entry.where(search)
    for ent in entry:
        entries.append(ent)
    return entries


def search_key():
    """Search by keyword"""
    clear()
    print("Search task and notes by a key word.")
    while True:
        print("Enter a word(s) to search by: ")
        enter = input('> ')
        if not enter:
            input("You must enter a word. Press enter")
            continue
        else:
            enter = Entry.task_name.contains(
                enter) | Entry.notes.contains(enter)
            entries = get_search_entries(enter)
            list_entries(entries, enter)
            return entries


def search_date():
    """Search an entry by date"""
    while True:
        clear()
        print("Search by Date\n")
        print(("*" * 20) + "\n")

        print('n')
        enter = add_date()
        enter = Entry.date.contains(enter)
        entries = get_search_entries(enter)
        list_entries(entries, enter)
        return entries


def search_time():
    """Search by employee's time spent working"""
    clear()
    print("Search by Time")
    while True:
        enter = add_time()
        if enter:
            enter = Entry.time == enter
            entries = get_search_entries(enter)
            list_entries(entries, enter)
            return entries


def search_name():
    """Search by employee's name"""
    clear()
    print("Search by employee's name")
    name = add_name()
    name = Entry.employee_name.contains(name)
    entries = get_search_entries(name)
    list_entries(entries, name)
    return entries


def list_entries(entries, search_info):
    """Shows list of entries"""
    clear()
    if entries:
        return view_entry(entries)
    else:
        print('\nNo matches found.')
        response = input("Would you like to make another"
                         " search? Y/n\n").lower().strip()
        if response.lower() != 'y':
            return prompt_menu()
        else:
            clear()
            return lookup()


def view_entry(entries):
    """Displays entries on the screen"""
    index = 0

    while True:
        clear()
        print_entries(index, entries)

        if len(entries) == 1:
            print('\n[E]dit\n[D]elete\n[Q]uit')
            sel = input('> ').lower().strip()

            if sel == 'e':
                return edit_entry(index, entries)
            elif sel == 'd':
                return delete_entry(index, entries)
            elif sel == 'q':
                return None
            else:
                input("Please input a valid command.  Press ENTER.\n")
        else:
            display_option(index, entries)

            nav = input("\nSelect an option. \n").lower().strip()

            if index >= 0 and nav == 'n':
                index += 1
                clear()
            elif index > 0 and nav == 'p':
                index -= 1
                clear()
            elif nav == 'e':
                return edit_entry(index, entries)
            elif nav == 'd':
                return delete_entry(index, entries)
            elif nav == 'q':
                return lookup()
            else:
                input('\nPlease make a valid selection. Press ENTER')


def print_entries(index, entry, display=True):
    """Prints entries"""

    if display:

        print('\n' + '*' * 20 + '\n')
        print('Date: {}\nEmployee: {}\nTask: {}\nTime: {}\nNotes: {}'.format(
            date_to_string(entry[index].date),
            entry[index].employee_name,
            entry[index].task_name,
            entry[index].time,
            entry[index].notes,
        ))


def lookup():
    """Look up a previous entry"""
    choice = None

    while True:
        clear()
        print("Search Entries\n")
        for key, value in search_entries.items():
            print("{}) {}".format(key, value.__doc__))
        choice = input('\nChoose Search\n').lower().strip()

        if choice in search_entries:
            clear()
            search = search_entries[choice]()
            return search


def edit_entry(index, entries):
    """Edit an entry"""
    clear()
    print('Edit Entry\n')
    single_entry(index, entries)
    print('\n[T]ask name\n[D]ate\nTime [S]pent\n[N]otes')
    sel = input('\nChoose an option to edit\n').lower().strip()
    while True:
        clear()
        if sel == 't':
            edit = edit_task(index, entries)
            return edit
        elif sel == 'd':
            edit = edit_date(index, entries)
            return edit
        elif sel == 's':
            edit = edit_time(index, entries)
            return edit
        elif sel == 'n':
            edit = edit_notes(index, entries)
            return edit
        else:
            input('Please make a valid selection. Press ENTER. \n')


def edit_task(index, entry):
    """Edits task name"""
    entry[index].task_name = add_task()
    ent = Entry.get(Entry.pk == entry[index].pk)
    ent.task_name = entry[index].task_name
    ent.save()
    input("Entry Saved!")
    return entry


def edit_date(index, entry):
    """Edits date"""
    entry[index].date = add_date()
    ent = Entry.get(Entry.pk == entry[index].pk)
    ent.date = entry[index].date
    ent.save()
    input("Entry Saved!")
    return entry


def edit_time(index, entry):
    """Edits time"""
    entry[index].time = add_time()
    ent = Entry.get(Entry.pk == entry[index].pk)
    ent.time = entry[index].time
    ent.save()
    input("Entry Saved!")
    return entry


def edit_notes(index, entry):
    """Edits notes"""
    entry[index].notes = add_notes()
    ent = Entry.get(Entry.pk == entry[index].pk)
    ent.notes = entry[index].notes
    ent.save()
    input("Entry Saved!")
    return entry


def delete_entry(index, entries):
    """Delete an entry """
    entry = Entry.get(Entry.pk == entries[index].pk)
    clear()
    print("Delete Entry\n")
    single_entry(index, entries)
    sel = input("Are you sure you want to DELETE? Y/N\n").lower().strip()

    if sel == 'y':
        entry.delete_instance()
        input("Entry deleted. Press Enter")
        return None
    else:
        input("\nEntry not deleted.  Press ENTER. \n")
        return lookup()


def single_entry(index, entries):
    """shows a single entry"""
    print('Date: {}\nEmployee: {}\nTask: {}\nTime: {}\nNotes: {}'.format(
        date_to_string(entries[index].date),
        entries[index].employee_name,
        entries[index].task_name,
        entries[index].time,
        entries[index].notes,
    ))


def date_to_string(date):
    """Convets a datetime to a string"""
    date_time = date.strftime('%m/%d/%Y')
    return date_time


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def display_option(index, entries):
    """Displays a menu for paging through the results"""
    p = "[P]revious entry"
    n = "[N]ext entry"
    e = "[E]dit entry"
    d = "[D]elete entry"
    q = "[Q]uit to menu"

    menu = [p, n, e, d, q]

    if index == 0:
        menu.remove(p)
    elif index == len(entries) - 1:
        menu.remove(n)

    print('\n')
    for option in menu:
        print(option)
    return menu


search_entries = OrderedDict([
    ('n', search_name),
    ('d', search_date),
    ('t', search_time),
    ('k', search_key),
    ('q', prompt_menu),
])

menu = OrderedDict([
    ('n', save_entry),
    ('l', lookup),
])

if __name__ == "__main__":
    initialize()
    prompt_menu()

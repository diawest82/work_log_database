"""Unit test for entries.py of Work log with a Database.  Coverage for both at 65%, coverage for entries.py %56"""

import unittest
import unittest.mock as mock
from datetime import datetime

from playhouse.test_utils import test_database
from peewee import *
import entries
from entries import Entry


TEST_DB = SqliteDatabase(':memory:')
TEST_DB.connect()
TEST_DB.create_tables([Entry], safe=True)


DATA = {
    "employee_name": "Diallo",
    "task_name": "task1",
    "time": '30',
    "date": datetime.strptime("04/18/2017", '%m/%d/%Y').date(),
    "notes": "Hello",
}

DATA2 = {
    "employee_name": "Diallo West",
    "task_name": "task2",
    "time": '30',
    "date": datetime.strptime("04/21/2017", '%m/%d/%Y').date(),
    "notes": "Hello World",
}


class WorklogTests(unittest.TestCase):
    def setUp(self):
        self.entry = self.save_entry(DATA)
        pass

    def save_entry(self, data):
        Entry.create(
            employee_name=DATA["employee_name"],
            task_name=DATA["task_name"],
            time=DATA['time'],
            date=DATA['date'],
            notes=DATA['notes']
        )

    def test_add_name(self):
        with mock.patch('builtins.input', side_effect=['Diallo'],
                        return_value=DATA['employee_name']):
            assert entries.add_name() == DATA['employee_name']

    def test_add_task(self):
        with mock.patch('builtins.input', side_effect=['task1'],
                        return_value=DATA['task_name']):
            assert entries.add_task() == DATA['task_name']

    def test_add_date(self):
        with mock.patch('builtins.input', side_effect=['04/18/2017'],
                        return_value=DATA['date']):
            assert entries.add_date() == DATA['date']

        with mock.patch('builtins.input', side_effect=['2017/04/18'],
                        return_value=DATA['date']):
            self.assertRaises(ValueError)

    def test_add_time(self):
        with mock.patch('builtins.input', side_effect=['30'],
                        return_value=DATA['time']):
            assert entries.add_time() == DATA['time']

    def test_add_notes(self):
        with mock.patch('builtins.input', side_effect=['Hello'],
                        return_value=DATA['notes']):
            assert entries.add_notes() == DATA['notes']

    def test_save_entry(self):
        with mock.patch('builtins.input',
                        side_effect=['Diallo West', 'task1', '30',
                                     '04/18/2017', "Hello", 'y', ''],
                        return_value=DATA):
            assert entries.save_entry()['task_name'] == DATA['task_name']

        with mock.patch('builtins.input',
                        side_effect=['Name', 'task1', '30', '04/18/2017',
                                     "Hello World", 'n', ''],
                        return_value=DATA):
            assert entries.save_entry() == None

    def test_edit_entry(self):
        with test_database(TEST_DB, (Entry,)):
                self.save_entry(DATA)
                self.save_entry(DATA2)
                test = Entry.select()
                index = 0
                ent = []
                for t in test:
                    ent.append(t)

                with mock.patch('builtins.input',
                                side_effect=(['t', 'TASK', ''])):
                    assert entries.edit_entry(
                        index, ent)[index].task_name == 'TASK'

                with mock.patch('builtins.input',
                                side_effect=(['d', '01/01/2017', ''])):
                    assert entries.edit_entry(
                        index, ent)[index].date == datetime.strptime(
                        "2017-01-01", '%Y-%m-%d').date()

                with mock.patch('builtins.input',
                                side_effect=(['s', '75', ''])):
                    assert entries.edit_entry(
                        index, ent)[index].time == '75'

                with mock.patch('builtins.input',
                                side_effect=(['n', 'Hello Notes', ''])):
                    assert entries.edit_entry(
                        index, ent)[index].notes == 'Hello Notes'

    def test_delete_entry(self):
        with test_database(TEST_DB, (Entry,)):
                self.save_entry(DATA)
                self.save_entry(DATA2)
                test = Entry.select()
                index = 0
                ent = []
                for t in test:
                    ent.append(t)

                with mock.patch('builtins.input', side_effect=['y', '']):
                    entries.delete_entry(index, test)
                    self.assertEqual(Entry.task_name, None)

    def test_display_options(self):
        p, n, e, d, q = ("[P]revious entry",
                         "[N]ext entry",
                         "[E]dit entry",
                         "[D]elete entry",
                         "[Q]uit to menu",)

        with test_database(TEST_DB, (Entry,)):
            self.save_entry(DATA)
            Entry.create(**DATA2)
            test = Entry.select()
            index = 0
            menu_test = [n, e, d, q]

            entries.display_option(index, test)
            self.assertNotIn(p, menu_test)


if __name__ == '__main__':
    unittest.main()

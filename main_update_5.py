import calendar
import datetime
import tkinter
import os
from datetime import date, timedelta
from tkinter.ttk import Style


PATH = '\\'.join(os.path.abspath(__file__).split('\\')[:-1]) + '\\save.txt'


def delete_save(line_to_delete):
    global saved_notes
    line_to_delete = line_to_delete
    with open(PATH, encoding='utf-8') as save:
        lines = save.readlines()

    with open(PATH, 'w', encoding='utf-8') as save:
        for line in lines:
            if line_to_delete != line:
                save.write(line)

    saved_notes = get_saved_notes()


def get_saved_notes():
    saved_notes = {}
    try:
        with open(PATH, 'r', encoding='utf-8') as save:
            lines = save.readlines()
            for line in lines:
                year_month, text = line.split(' - ')
                saved_notes[year_month] = saved_notes.get(year_month, []) + [text]
    except FileNotFoundError:
        return saved_notes

    for key, value in saved_notes.items():
        day_notes = {}
        for j in value:
            daynum, note = j.split(':')
            note = note.replace('\n', '')
            day_notes[daynum] = day_notes.get(daynum, []) + [note]
        saved_notes[key] = day_notes
    return saved_notes


class Day:
    def __init__(self, name):
        self.name = name
        self.notes = []
        self.add_saved_notes()

    def write_note(self, message):
        self.notes.append(message)

    def make_note(self):
        new_note = Notebook(self)

    def read_notes(self):
        return self.notes

    def add_saved_notes(self):
        for key, value in current_saved_notes.items():
            if key == self.name:
                for note in value:
                    if note in self.notes:
                        continue
                    self.write_note(note)


class ButtonWithDescription(tkinter.Frame):
    def __init__(self, parent, button_text, label_text, command):
        super(ButtonWithDescription, self).__init__(parent)
        self.button = tkinter.Button(text=button_text, height=5, width=10, command=command)
        self.label = tkinter.Label(text=label_text)

        self.rowconfigure(1)
        self.rowconfigure(2)
        self.columnconfigure(1)
        self.columnconfigure(2)

        self.button.grid(row=1, column=1, columnspan=2, rowspan=2)
        self.label.grid(row=2, column=2)


class DeletableNote(tkinter.Frame):
    def __init__(self, parent, text):
        super(DeletableNote, self).__init__(parent)
        self.save_format_text = f'{" ".join(list(map(str, current_year_month)))} - {parent.master.day.name}:{text}'
        self.save_format_text = self.save_format_text + '\n'
        self.text = text
        self.parent = parent
        self.textbox = tkinter.Text(self, width=33, height=2, wrap=tkinter.WORD)
        self.textbox.bind('<Key>', lambda x: 'break')
        self.textbox.insert(tkinter.END, text)
        self.destroy_button = tkinter.Button(self, width=4, height=2, text='-', command=self.destroy_the_note)

        self.rowconfigure(1, pad=1)
        self.columnconfigure(1, pad=2)
        self.columnconfigure(2, pad=1)

        self.textbox.grid(row=1, column=1)
        self.destroy_button.grid(row=1, column=2)

    def destroy_the_note(self):
        self.destroy()
        delete_save(self.save_format_text)
        self.parent.master.delete_the_textbox(self)
        # self.parent.deletable_notes


class Notebook(tkinter.Toplevel):
    def __init__(self, day):
        super(Notebook, self).__init__(master)
        self.grab_set()

        self.day = day
        self.day_notes = self.day.read_notes()

        self.textframe = tkinter.Frame(self, width=37, height=300)
        self.entry = tkinter.Entry(self, width=30)
        self.exit_button = tkinter.Button(self, text='Выйти', width=6, height=3, command=self.come_back)
        self.done_button = tkinter.Button(self, text='Готово', width=6, height=3, command=self.save_the_note)

        self.initUI()

    def initUI(self):
        self.title('Заметки')
        Style().configure("TButton", padding=(0, 5, 0, 5), font='serif 10')

        for i in range(3):
            self.columnconfigure(i, pad=1)

        for i in range(7):
            self.rowconfigure(i, pad=2)

        self.textframe.columnconfigure(1, pad=1)
        for i in range(5):
            self.textframe.rowconfigure(i, pad=2)

        self.fill_the_notebook()

    def update_textframe(self):
        self.day_notes = self.day.read_notes()
        dn = DeletableNote(self.textframe, self.day_notes[-1])
        dn.grid(row=len(self.day_notes), column=1)

    def fill_the_notebook(self):
        self.entry.grid(row=0, column=0, columnspan=4, ipadx=60)
        self.textframe.grid(row=1, column=0, columnspan=4, rowspan=5)
        # self.textframe.grid_propagate(False)
        if self.day_notes:
            for i, text in enumerate(self.day_notes):
                dn = DeletableNote(self.textframe, text)
                dn.grid(row=i, column=1)
        self.exit_button.grid(row=6, column=0, sticky=tkinter.S + tkinter.W)
        self.done_button.grid(row=6, column=3, sticky=tkinter.S + tkinter.E)

    def save_the_note(self):
        text = self.entry.get()
        with open(PATH, 'a', encoding='utf-8') as save:
            save.write(f'{" ".join(list(map(str, current_year_month)))} - {self.day.name}:{text}\n')
        self.day.write_note(text)
        self.update_textframe()
        self.entry.delete(0, tkinter.END)

    def come_back(self):
        self.destroy()

    def delete_the_textbox(self, deletable_note):
        self.day_notes.remove(deletable_note.text)


class MonthUI(tkinter.Frame):
    def __init__(self, theyear, themonth):
        super().__init__()
        self.wigets = []
        self.initUI(theyear, themonth)

    def initUI(self, theyear, themonth):
        Style().configure("TButton", padding=(0, 5, 0, 5), font='serif 10')

        for i in range(7):
            self.columnconfigure(i, pad=2)

        for i in range(6):
            self.rowconfigure(i, pad=2)

        self.fill_the_month(theyear, themonth)

    def fill_the_month(self, theyear, themonth):
        days_location = self.get_days_location(theyear, themonth)
        for curr_row, week in enumerate(days_location):
            for curr_col, day in enumerate(week):
                new_button = None
                if day != '  ':
                    new_day = Day(day)
                    button_text = current_saved_notes.get(new_day.name, '')
                    if button_text:
                        button_text = f'({len(button_text)})'
                    # button_text = f'{day} {button_text}'
                    button_text = day
                    new_button = tkinter.Button(self, text=button_text, height=5, width=10, command=new_day.make_note)
                    new_button.grid(row=curr_row, column=curr_col)
                self.wigets.append(new_button)

    def get_days_location(self, theyear, themonth):
        result = []
        days_location = calendar.TextCalendar().formatmonth(theyear, themonth).split('\n')[2:-1]
        days_location = list(map(lambda x: x.ljust(20, ' '), days_location))
        for i in days_location:
            days = []
            i = i[0] + i[1] + i[3] + i[4] + i[6] + i[7] + i[9] + i[10] + i[12] + i[13] + i[15] + i[16] + i[18] + i[19]
            days = list(zip(i, i[1:]))[::2]
            days = list(map(lambda x: ''.join(x), days))
            result.append(days)
        return result

    def updateUI(self, theyear, themonth):
        for i in range(len(self.wigets)):
            if self.wigets[i]:
                self.wigets[i].destroy()
        self.wigets.clear()
        self.fill_the_month(theyear, themonth)


class MonthSwitcherUI(tkinter.Frame):
    def __init__(self):
        super().__init__(width=84)
        Style().configure("TButton", padding=(0, 5, 0, 5), font='serif 10')
        for i in range(3):
            self.columnconfigure(i, pad=20)
        self.rowconfigure(0, pad=10)
        self.next_month_button = tkinter.Button(
            self, text='>', width=22, height=1, command=self.next_year_month)
        self.next_month_button.grid(column=2, row=0, sticky=tkinter.E)
        self.previous_month_button = tkinter.Button(
            self, text='<', width=22, height=1, command=self.previous_year_month)
        self.previous_month_button.grid(column=0, row=0, sticky=tkinter.W)
        year_month_date = date(year=current_year_month[0], month=current_year_month[1], day=1)
        self.label = tkinter.Label(self, text=datetime.datetime.strftime(year_month_date, '%Y %B'))
        self.label.grid(column=1, row=0)

    def change_year_month(self, next: bool):
        global current_year_month, calendarUI, monthswitcherUI, current_saved_notes
        current_year_month_date = date(month=current_year_month[1], year=current_year_month[0], day=1)
        delta = timedelta(days=calendar.monthrange(*current_year_month)[1])
        if next:
            new_date = delta + current_year_month_date
        else:
            new_date = current_year_month_date - delta
        current_year_month = (new_date.year, new_date.month)
        current_saved_notes = saved_notes.get(' '.join(list(map(str, current_year_month))), {})
        year_month_date = date(year=current_year_month[0], month=current_year_month[1], day=1)
        self.label.config(text=datetime.datetime.strftime(year_month_date, '%Y %B'))

        calendarUI.updateUI(*current_year_month)

    def next_year_month(self):
        self.change_year_month(True)

    def previous_year_month(self):
        self.change_year_month(False)


class Weekday_Label(tkinter.Frame):
    def __init__(self):
        super(Weekday_Label, self).__init__()
        days = []
        days.append(tkinter.Label(text='Mon'))
        days.append(tkinter.Label(text='Tues'))
        days.append(tkinter.Label(text='Wed'))
        days.append(tkinter.Label(text='Thurs'))
        days.append(tkinter.Label(text='Fri'))
        days.append(tkinter.Label(text='Sat'))
        days.append(tkinter.Label(text='Sun'))

        for i in range(7):
            self.columnconfigure(i, pad=1)
        self.rowconfigure(1)
        for i, day in enumerate(days):
            day.grid(row=1, column=i)
        self.grid()

class App:
    def __init__(self):
        self.update()

    def update(self):
        global current_year_month, master, calendarUI, monthswitcherUI
        current_year_month = date.today().year, date.today().month
        master = tkinter.Tk()
        master.resizable(width=False, height=False)
        calendarUI = MonthUI(*current_year_month)
        monthswitcherUI = MonthSwitcherUI()
        master.mainloop()


current_year_month = date.today().year, date.today().month
saved_notes = get_saved_notes()
current_saved_notes = {}
try:
    current_saved_notes = saved_notes[' '.join(list(map(str, current_year_month)))]
except KeyError:
    pass

master = tkinter.Tk()
master.title("Календарь")
for i in range(1, 4):
    master.rowconfigure(i, pad=1)
for i in range(1, 8):
    master.columnconfigure(i)

# weekday_label = Weekday_Label()
weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
calendarUI = MonthUI(*current_year_month)
monthswitcherUI = MonthSwitcherUI()
# weekday_label.grid(row=1, column=1, columnspan=7)
for i, weekday in enumerate(weekdays):
    label = tkinter.Label(text=weekday)
    label.grid(row=1, column=i + 1)
calendarUI.grid(row=2, column=1, columnspan=7)
monthswitcherUI.grid(row=3, column=1, columnspan=7)
master.mainloop()

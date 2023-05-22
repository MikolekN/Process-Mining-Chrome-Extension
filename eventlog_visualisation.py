import os
import sqlite3
import datetime

import pandas
import pandas as pd
import pm4py
from pm4py.objects.conversion.log import converter as log_converter

ID = 1
events = []
cases = []


class case:
    case_id = 0
    events = []

    def __init__(self, case_events=None):
        global ID, cases
        self.case_id = ID
        ID += 1
        self.events = case_events
        cases.append(self)

    def __str__(self):
        string = []
        for e in self.events:
            string.append(str(e))
        return str(self.case_id) + ") " + " -> ".join(string)


class event:
    event_id = 0
    timestamp = 0
    from_visit = 0
    title = 0
    url = 0
    transition = 0
    duration = 0
    tip = True

    def __init__(self, id, time, from_visit, title, url, transition, duration):
        global events
        self.event_id = id
        self.timestamp = time
        self.from_visit = from_visit
        self.title = title
        self.url = url
        self.transition = transition
        self.duration = duration
        self.tip = True
        process_events(from_visit)
        events.append(self)

    def __str__(self):
        return str(self.event_id)


def process_events(from_visit):
    if from_visit != 0:
        for e in events:
            if e.event_id == from_visit:
                e.tip = False


def get_event(id):
    for e in events:
        if e.event_id == id:
            return e
    return None


def print_events():
    for e in events:
        print(e.event_id, e.from_visit, e.tip)


def print_full_events():
    for e in events:
        print(e.event_id, e.from_visit, e.tip, e.title, e.url, e.transition, e.duration)


def print_eventlog():
    print("Case ID".center(10, ' ')
          + " | " + "Event ID".center(10, ' ')
          + " | " + "From ID".center(10, ' ')
          + " | " + "Timestamp".center(20, ' ')
          + " | " + "Transition".center(12, ' ')
          + " | " + "Duration".center(10, ' ')
          + " | " + "Tip".center(10, ' ')
          + " | " + "Title".center(100, ' ')
          + " | " + "URL".center(200, ' '))
    for c in cases:
        for e in c.events:
            if e == c.events[0]:
                print(str(c.case_id).center(10, ' ')
                      + " | " + str(e.event_id).center(10, ' ')
                      + " | " + str(e.from_visit).center(10, ' ')
                      + " | " + str(e.timestamp).center(20, ' ')
                      + " | " + str(e.transition).center(12, ' ')
                      + " | " + str(e.duration).center(10, ' ')
                      + " | " + str(e.tip).center(10, ' ')
                      + " | " + str(e.title[:100]).ljust(100, ' ')
                      + " | " + str(e.url).ljust(200, ' '))
            else:
                print(" ".center(10, ' ')
                      + " | " + str(e.event_id).center(10, ' ')
                      + " | " + str(e.from_visit).center(10, ' ')
                      + " | " + str(e.timestamp).center(20, ' ')
                      + " | " + str(e.transition).center(12, ' ')
                      + " | " + str(e.duration).center(10, ' ')
                      + " | " + str(e.tip).center(10, ' ')
                      + " | " + str(e.title[:100]).ljust(100, ' ')
                      + " | " + str(e.url).ljust(200, ' '))


def print_cases():
    for c in cases:
        print(c)


def create_cases():
    for e in events:
        c = []
        if e.tip:
            c.append(e)
            current = e
            while current.from_visit != 0:
                current = get_event(current.from_visit)
                c.append(current)
            c.reverse()
            case(c)


def load_events():
    global events
    # path to user's history database (Chrome)
    data_path = os.path.expanduser('~') + "\\AppData\\Local\\Google\\Chrome\\User Data\\Default"
    files = os.listdir(data_path)

    history_db = os.path.join(data_path, 'history')

    # querying the db
    c = sqlite3.connect(history_db)
    cursor = c.cursor()
    select_statement = "SELECT visits.id, urls.title, urls.url, visits.visit_time, visits.from_visit, " \
                       "visits.transition, visits.visit_duration FROM urls, visits WHERE urls.id = visits.url;"
    cursor.execute(select_statement)

    results = cursor.fetchall()  # tuple
    for event_id, title, url, time, from_visit, transition, duration in results:
        event(event_id, time, from_visit, title, url, transition, duration)
    events = events[200:]


def read_column_data_to_export():
    case_ids = []
    event_ids = []
    from_ids = []
    timestamps = []
    transitions = []
    durations = []
    titles = []
    urls = []

    for c in cases:
        for e in c.events:
            case_ids.append(str(c.case_id))
            event_ids.append(e.event_id)
            from_ids.append(e.from_visit)
            timestamps.append(datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=e.timestamp))
            transitions.append(e.transition)
            durations.append(e.duration)
            titles.append(e.title)
            urls.append(e.url)

    return case_ids, event_ids, from_ids, timestamps, transitions, durations, titles, urls


def export_to_csv():
    case_ids, event_ids, from_ids, timestamps, transitions, durations, titles, urls = read_column_data_to_export()
    data = {
        "case_id": case_ids,
        "event_id": event_ids,
        "from_id": from_ids,
        "timestamp": timestamps,
        "transition": transitions,
        "duration": durations,
        "title": titles,
        "url": urls,
    }
    df = pd.DataFrame(data)
    df.to_csv("eventlog_CSV.csv")
    df = pandas.read_csv("eventlog_CSV.csv")
    print(df.to_string())


def export_to_xes():
    case_ids, event_ids, from_ids, timestamps, transitions, durations, titles, urls = read_column_data_to_export()
    data = {
        "case_id": case_ids,
        "event_id": event_ids,
        "from_id": from_ids,
        "timestamp": timestamps,
        "transition": transitions,
        "duration": durations,
        "title": titles,
        "url": urls,
    }
    df = pd.DataFrame(data)
    pm4py.write_xes(df, "eventlog_XES.xes", "case_id")
    df = pm4py.convert_to_dataframe(pm4py.read_xes("eventlog_XES.xes"))
    print(df.to_string())


load_events()
create_cases()
while True:
    print()
    prompt = input("[.] Type:\n[.] <a> to print full events information\n[.] <b> to print events\n[.] <c> to print "
                   "cases\n[.] <d> to print event log\n[.] <e> to export to csv\n[.] <f> to export to xes\n[>] ")
    if prompt == "a":
        print_full_events()
    elif prompt == "b":
        print_events()
    elif prompt == "c":
        print_cases()
    elif prompt == "d":
        print_eventlog()
    elif prompt == "e":
        export_to_csv()
    elif prompt == "f":
        export_to_xes()
    else:
        break

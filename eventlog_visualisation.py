import os
import sqlite3
import datetime
import time

import pandas as pd
import pm4py

filtered = False


class Case:
    ID = 1
    cases = []

    def __init__(self, case_events=None):
        self.case_id = Case.ID
        Case.ID += 1
        self.events = case_events
        Case.cases.append(self)

    def __str__(self):
        event_strings = [str(event) for event in self.events if event.duration != 0 or not filtered]
        return f"{self.case_id}) " + " -> ".join(event_strings) if event_strings else ""


class Event:
    events = []

    def __init__(self, id, t, from_visit, title, url, transition, duration):
        self.event_id = id
        self.timestamp = t
        self.from_visit = from_visit
        self.title = title
        self.url = url
        self.transition = transition
        self.duration = duration
        self.tip = True
        self.process_events(from_visit)
        Event.events.append(self)

    @staticmethod
    def process_events(from_visit):
        if from_visit != 0:
            for event in Event.events:
                if event.event_id == from_visit:
                    event.tip = False

    def __str__(self):
        return str(self.event_id)


def get_event(id):
    for event in Event.events:
        if event.event_id == id:
            return event
    return None


def filter_events_by_duration():
    return [event for event in Event.events if event.duration != 0]


def print_events():
    events = Event.events if not filtered else filter_events_by_duration()
    for event in events:
        print(
            event.event_id,
            event.from_visit,
            event.tip
        )


def print_full_events():
    events = Event.events if not filtered else filter_events_by_duration()
    for event in events:
        print(
            event.event_id,
            event.from_visit,
            event.tip,
            event.title,
            event.url,
            event.transition,
            event.duration
        )


def print_eventlog():
    header = [
        "Case ID".center(10),
        "Event ID".center(10),
        "From ID".center(10),
        "Timestamp".center(20),
        "Transition".center(12),
        "Duration".center(10),
        "Tip".center(10),
        "Title".center(100),
        "URL".center(200)
    ]
    print(" | ".join(header))

    for case in Case.cases:
        j = 0
        for i, event in enumerate(case.events):
            if filtered and event.duration == 0:  # Skip events with duration 0
                if i == j:
                    j += 1
                continue
            row = [
                str(case.case_id).center(10),
                str(event.event_id).center(10),
                str(event.from_visit).center(10),
                str(event.timestamp).center(20),
                str(event.transition).center(12),
                str(event.duration).center(10),
                str(event.tip).center(10),
                str(event.title[:100]).ljust(100),
                str(event.url).ljust(200)
            ]
            if i == j:
                print(" | ".join(row))
            else:
                row[0] = "".center(10)  # Empty space for Case ID in subsequent rows
                print(" | ".join(row))


def print_cases():
    for c in Case.cases:
        if str(c):
            print(c)


def create_cases():
    for e in Event.events:
        c = []
        if e.tip:
            c.append(e)
            current = e
            while current.from_visit != 0:
                current = get_event(current.from_visit)
                if current is None:
                    break
                c.append(current)
            c.reverse()
            Case(c)


def load_events():
    # path to user's history database (Chrome)
    data_path = os.path.expanduser('~') + "\\AppData\\Local\\Google\\Chrome\\User Data\\Default"

    history_db = os.path.join(data_path, 'history')

    # querying the db
    c = sqlite3.connect(history_db)
    cursor = c.cursor()
    select_statement = "SELECT visits.id, urls.title, urls.url, visits.visit_time, visits.from_visit, " \
                       "visits.transition, visits.visit_duration FROM urls, visits WHERE urls.id = visits.url;"
    cursor.execute(select_statement)

    results = cursor.fetchall()  # tuple
    for event_id, title, url, t, from_visit, transition, duration in results:
        Event(event_id, t, from_visit, title, url, transition, duration)


def read_data_to_export():
    case_ids = []
    event_ids = []
    from_ids = []
    timestamps = []
    transitions = []
    durations = []
    titles = []
    urls = []

    for c in Case.cases:
        for e in c.events:
            case_ids.append(str(c.case_id))
            event_ids.append(e.event_id)
            from_ids.append(e.from_visit)
            timestamps.append(datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=e.timestamp))
            transitions.append(e.transition)
            durations.append(e.duration)
            titles.append(e.title)
            urls.append(e.url)

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

    return df


def export_to_csv():
    df = read_data_to_export()
    df.to_csv("eventlog_CSV.csv")
    df = pd.read_csv("eventlog_CSV.csv")
    print(df.to_string())


def export_to_xes():
    df = read_data_to_export()
    pm4py.write_xes(df, "eventlog_XES.xes", "case_id")
    df = pm4py.convert_to_dataframe(pm4py.read_xes("eventlog_XES.xes"))
    print(df.to_string())


def in_the_background():
    while True:
        Case.ID = 1
        Event.events = []
        Case.cases = []
        try:
            load_events()
        except:
            time.sleep(5)
            continue
        create_cases()
        print_eventlog()
        time.sleep(10)


load_events()
create_cases()
while True:
    print()
    print(f"Current output is {'filtered' if filtered else 'not filtered'}")
    prompt = input("[.] Type:\n[.] <a> to print full events information\n[.] <b> to print events\n[.] <c> to print "
                   "cases\n[.] <d> to print event log\n[.] <e> to export to csv\n[.] <f> to export to xes\n[.] <g> to "
                   "continuously print event log (as if it was done in the background)\n[.] <h> to toggle filtering "
                   "out 0 in duration\n[>] ")
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
    elif prompt == "g":
        in_the_background()
    elif prompt == "h":
        filtered = not filtered
    else:
        break

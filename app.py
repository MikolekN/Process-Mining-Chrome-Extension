import json
import pandas as pd
import pm4py
import datetime
import requests as requests

from case.cases import Cases
from event.events import Events, Event


def read_data_to_export(cases):
    case_ids = []
    event_ids = []
    from_ids = []
    timestamps = []
    transitions = []
    durations = []
    titles = []
    urls = []

    for case_index, case in enumerate(cases.cases):
        for event in case.events:
            case_ids.append(str(case_index))
            event_ids.append(event.eventId)
            from_ids.append(event.fromVisit)
            timestamps.append(datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=event.timestamp))
            transitions.append(event.transition)
            durations.append(event.duration)
            titles.append(event.title)
            urls.append(event.url)

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


def export_to_csv(cases):
    df = read_data_to_export(cases)
    df.to_csv("eventlog_CSV.csv")
    df = pd.read_csv("eventlog_CSV.csv")
    print(df.to_string())


def export_to_xes(cases):
    df = read_data_to_export(cases)
    pm4py.write_xes(df, "eventlog_XES.xes", "case_id")
    df = pm4py.convert_to_dataframe(pm4py.read_xes("eventlog_XES.xes"))
    print(df.to_string())


def print_eventlog(cases, filtered):
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

    for case_index, case in enumerate(cases.cases):
        j = 0
        for i, event in enumerate(case.events):
            if filtered and event.duration == 0:  # Skip events with duration 0
                if i == j:
                    j += 1
                continue
            row = [
                str(case_index).center(10),
                str(event.eventId).center(10),
                str(event.fromVisit).center(10),
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


def main():
    response = requests.get('http://localhost:1234/events')
    filtered = False
    cases = Cases()
    events = Events(update_cases=cases.update_cases,
                    initial_events=[Event.deserialize(event) for event in json.loads(response.content.decode())])
    while True:
        print()
        print(f"Current output is {'filtered' if filtered else 'not filtered'}")
        prompt = input("[.] Type:\n[.] <a> to print full events information\n[.] <b> to print events\n[.] <c> to print "
                       "cases\n[.] <d> to print event log\n[.] <e> to export to csv\n[.] <f> to export to xes\n[.] "
                       "<g> to toggle filtering out 0 in duration\n[>] ")
        if prompt == "a":
            events.print_full_events(filtered)
        elif prompt == "b":
            events.print_events(filtered)
        elif prompt == "c":
            cases.print_cases()
        elif prompt == "d":
            print_eventlog(cases, filtered)
        elif prompt == "e":
            export_to_csv(cases)
        elif prompt == "f":
            export_to_xes(cases)
        elif prompt == "g":
            filtered = not filtered
        else:
            break


if __name__ == '__main__':
    main()

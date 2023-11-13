import datetime
import json
import datetime as dt

import pandas as pd
import pm4py
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


def print_cases(events, filtered):
    case_index = 0
    for event in events.events:
        if event.tip:
            case = [event]
            while event.fromVisit != 0:
                event = events.get_event(event.fromVisit)
                case.append(event)
            case.reverse()
            events_string = [str(event) for event in case if not filtered or event.duration != 0]
            print(f"{case_index + 1}) " + (" -> ".join(events_string) if events_string else ""))
            case_index += 1


def import_eventlog_from_xes():
    log = pm4py.read_xes("eventlog_XES.xes")
    return log


def temp():
    log = import_eventlog_from_xes()

    # 1. dfg and directly_follows_graph
    # print('a')
    # dfg, start_activities, end_activities = pm4py.discover_dfg(log, activity_key="title", timestamp_key="timestamp")
    # print('b')
    # print(dfg)
    # print()
    # print()
    # print(start_activities)
    # print()
    # print()
    # print(end_activities)
    # pm4py.write_dfg(dfg, start_activities, end_activities, file_path="dfg.dfg")
    # print('c')
    # pm4py.view_dfg(dfg, start_activities, end_activities)
    # pm4py.save_vis_dfg(dfg, start_activities, end_activities, file_path="dfg.png")

    # # 2. dfg_typed
    # dfg_typed = pm4py.discover_dfg_typed(log, activity_key="title", timestamp_key="timestamp")
    # pm4py.save_vis_dfg(dfg_typed.graph, dfg_typed.start_activities, dfg_typed.end_activities, file_path="dfg_typed.png")
    #
    # # 3. performance_dfg
    # performance_dfg, start_activities, end_activities = pm4py.discover_performance_dfg(log, activity_key='title', timestamp_key='timestamp')
    # # pm4py.view_performance_dfg(performance_dfg, start_activities, end_activities)
    # pm4py.save_vis_performance_dfg(performance_dfg, start_activities, end_activities, file_path="performance_dfg.png")
    #
    # # 4. petri_net_alpha, petri_net_ilp, and petri_net_alpha_plus
    # # Max 2000 values
    petri_net_alpha, im, fm = pm4py.discover_petri_net_alpha(log, activity_key='title', timestamp_key='timestamp')
    # pm4py.write_pnml(petri_net_alpha, im, fm, "petri_net_alpha.pnml")
    pm4py.save_vis_petri_net(petri_net_alpha, im, fm, file_path="petri_net_alpha.png")
    #
    # petri_net_ilp, im, fm = pm4py.discover_petri_net_ilp(log, activity_key='title', timestamp_key='timestamp')
    # pm4py.save_vis_petri_net(petri_net_ilp, im, fm, file_path="petri_net_ilp.png")
    #
    # # petri_net_alpha_plus, im, fm = pm4py.discover_petri_net_alpha_plus(log, activity_key='title', timestamp_key='timestamp')
    # # pm4py.save_vis_petri_net(petri_net_alpha_plus, im, fm, file_path="petri_net_alpha_plus.png")
    #
    # # 5. petri_net_inductive
    # net, initial_marking, final_marking = pm4py.discover_petri_net_inductive(log, activity_key="title", timestamp_key="timestamp")
    # # pm4py.view_petri_net(net, initial_marking, final_marking, format="svg")
    # pm4py.save_vis_petri_net(net, initial_marking, final_marking, file_path="petri_net.png")
    #
    # # 6. petri_net_heuristics
    # petri_net, im, fm = pm4py.discover_petri_net_heuristics(log, activity_key="title", timestamp_key="timestamp")
    # pm4py.save_vis_petri_net(petri_net, im, fm, file_path="petri_net_heu.png")
    #
    # # 7. process_tree_inductive
    # process_tree = pm4py.discover_process_tree_inductive(log, activity_key='title', timestamp_key='timestamp')
    # # pm4py.view_process_tree(process_tree)
    # pm4py.save_vis_process_tree(process_tree, file_path="process_tree.png")
    #
    # # 8. heuristics_net
    # heu_net = pm4py.discover_heuristics_net(log, activity_key='title', timestamp_key='timestamp')
    # # pm4py.view_heuristics_net(heu_net)
    # pm4py.save_vis_heuristics_net(heu_net, file_path="heu_net.png")
    #
    # # 9. minimum_self_distance
    # msd = pm4py.derive_minimum_self_distance(log, activity_key='title', timestamp_key='timestamp')
    #
    # # 10. footprints
    # # footprints = pm4py.discover_footprints(log, )
    # # pm4py.save_vis_footprints(footprints, file_path="footprints.png")
    #
    # # 11. eventually_follows_graph
    # efg = pm4py.discover_eventually_follows_graph(log, activity_key='title', timestamp_key='timestamp')
    #
    # # 12. bpmn_inductive
    # process_model = pm4py.discover_bpmn_inductive(log, activity_key="title", timestamp_key="timestamp")
    # # pm4py.view_bpmn(process_model)
    # pm4py.save_vis_bpmn(process_model, file_path="process_model.png")
    #
    # # 13. transition_system
    # ts = pm4py.discover_transition_system(log, activity_key="title", timestamp_key="timestamp")
    # pm4py.save_vis_transition_system(ts, file_path="ts.png")
    #
    # # 14. prefix_tree
    # prefix_tree = pm4py.discover_prefix_tree(log, activity_key="title", timestamp_key="timestamp")
    # pm4py.save_vis_prefix_tree(prefix_tree, file_path="prefix_tree.png")
    #
    # # 15. temporal_profile
    # temporal_profile = pm4py.discover_temporal_profile(log, activity_key="title", timestamp_key="timestamp")


def main():
    response = requests.get('http://localhost:1234')
    filtered = False
    cases = Cases()
    events = Events(update_cases=cases.update_cases,
                    initial_events=[Event.deserialize(event) for event in json.loads(response.content.decode())])

    while True:
        print()
        print(f"Current output is {'filtered' if filtered else 'not filtered'}")
        prompt = input("[.] Type:\n[.] <a> to print full events information\n[.] <b> to print events\n[.] <c> to print "
                       "cases\n[.] <d> to print event log\n[.] <e> to export to csv\n[.] <f> to export to xes\n[.] "
                       "<g> to toggle filtering out 0 in duration\n[.] <h> to print cases using just events list\n"
                       "[.] <i> to #TEMP#\n[>] ")
        if prompt == "a":
            events.print_full_events(filtered)
        elif prompt == "b":
            events.print_events(filtered)
        elif prompt == "c":
            cases.print_cases(filtered)
        elif prompt == "d":
            print_eventlog(cases, filtered)
        elif prompt == "e":
            export_to_csv(cases)
        elif prompt == "f":
            export_to_xes(cases)
        elif prompt == "g":
            filtered = not filtered
        elif prompt == "h":
            print_cases(events, filtered)
        elif prompt == "i":
            temp()
        else:
            break


# if __name__ == '__main__':
#     main()


event_log = pm4py.read_xes("eventlog_XES.xes")
process_tree = pm4py.discovery.discover_process_tree_inductive(event_log, activity_key='title', timestamp_key='timestamp')
# pm4py.view_process_tree(process_tree)
bpmn_model = pm4py.convert_to_bpmn(process_tree)
pm4py.view_bpmn(bpmn_model)
pm4py.save_vis_bpmn(bpmn_model, 'bpmn.png')
# dfg, start_activities, end_activities = pm4py.discover_dfg(event_log, activity_key='title', timestamp_key='timestamp')
# pm4py.view_dfg(dfg, start_activities, end_activities)
# pm4py.save_vis_dfg(dfg, start_activities, end_activities, 'dfg1.png')



from event.events import Event


class Case:
    def __init__(self, case_events=None):
        self.events = []
        if case_events is not None:
            if isinstance(case_events, Event):
                self.events = [case_events]
            elif isinstance(case_events, list):
                if not all(isinstance(event, Event) for event in case_events):
                    raise ValueError("All events in a case must be of type Event.")
                self.events = case_events
            else:
                raise ValueError("Invalid input in Case initialization.")

    def toString(self, filtered):
        events_string = [str(event) for event in self.events if not filtered or event.duration != 0]
        return " -> ".join(events_string) if events_string else ""


class Cases:
    def __init__(self, initial_cases=None):
        self.cases = []
        if initial_cases is not None:
            if isinstance(initial_cases, Case):
                self.cases = [initial_cases]
            elif isinstance(initial_cases, list):
                if not all(isinstance(case, Case) for case in initial_cases):
                    raise ValueError("All initial cases must be of type Case.")
                self.cases = initial_cases
            else:
                raise ValueError("Invalid input in Cases initialization.")

    def append(self, case):
        if isinstance(case, Case):
            self.cases.append(case)
        elif isinstance(case, list):
            self.cases.extend(case)
        else:
            raise ValueError("Item to append must be of type Case or list of Case.")

    def remove(self, case):
        self.cases.remove(case)

    def update_cases(self, event):
        added = False
        if event.fromVisit != 0:
            for case in self.cases:
                if event.fromVisit == case.events[-1].eventId:
                    added = True
                    case.events.append(event)
                    break

                for index, e in enumerate(case.events):
                    if e.eventId == event.fromVisit:
                        added = True
                        events = case.events[:index+1]
                        events.append(event)
                        self.append(Case(events))
                        break

                if added:
                    break
        if not added:
            self.cases.append(Case(event))

    def print_cases(self, filtered=False):
        for case_index, case in enumerate(self.cases):
            print(f"{case_index + 1}) " + case.toString(filtered))

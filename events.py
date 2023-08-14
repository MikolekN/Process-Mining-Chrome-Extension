class Event:
    def __init__(self, event_id, timestamp, from_visit, title, url, transition, duration):
        self.event_id = event_id
        self.timestamp = timestamp
        self.from_visit = from_visit
        self.title = title
        self.url = url
        self.transition = transition
        self.duration = duration
        self.tip = True

    def __str__(self):
        return str(self.event_id)


class Events:
    def __init__(self, update_cases=None, initial_events=None):
        self.events = []
        self.update_cases = update_cases
        if initial_events is not None:
            if isinstance(initial_events, Event):
                self.events = [initial_events]
            elif isinstance(initial_events, list):
                if not all(isinstance(event, Event) for event in initial_events):
                    raise ValueError("All initial events must be of type Event.")
                self.events = initial_events
            else:
                raise ValueError("Invalid input in Events initialization.")
            self.process_events()

    def append(self, event):
        if isinstance(event, Event):
            self._append_single_event(event)
        elif isinstance(event, list):
            self._append_multiple_events(event)
        else:
            raise ValueError("Item to append must be of type Event or list of Event.")

    def _append_single_event(self, event):
        self.events.append(event)
        self._update_tip(event)
        if self.update_cases:
            self.update_cases(event)

    def _append_multiple_events(self, events):
        if not all(isinstance(event, Event) for event in events):
            raise ValueError("All events to append must be of type Event.")
        self.events.extend(events)
        for event in events:
            self._update_tip(event)
            if self.update_cases:
                self.update_cases(event)

    def _update_tip(self, event):
        if event.from_visit != 0:
            e = self.get_event(event.from_visit)
            if e is not None:
                e.tip = False

    def get_event(self, event_index):
        for event in self.events:
            if event.event_id == event_index:
                return event
        return None

    def filter_by_duration(self):
        return [event for event in self.events if event.duration != 0]

    def print_events(self, filtered):
        events = self.events if not filtered else self.filter_by_duration()
        for event in events:
            print(
                event.event_id,
                event.from_visit,
                event.tip
            )

    def print_full_events(self, filtered):
        events = self.events if not filtered else self.filter_by_duration()
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

    def process_events(self):
        for event in self.events:
            self._update_tip(event)

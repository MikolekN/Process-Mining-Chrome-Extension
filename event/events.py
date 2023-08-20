class Event:
    def __init__(self, eventId, timestamp, fromVisit, title, url, transition, duration, tip=True):
        self.eventId = int(eventId)
        self.timestamp = int(timestamp)
        self.fromVisit = int(fromVisit)
        self.title = title
        self.url = url
        self.transition = transition
        self.duration = int(duration)
        self.tip = bool(tip)

    def __str__(self):
        return str(self.eventId)

    def serialize(self):
        return {
            "eventId": self.eventId,
            "timestamp": self.timestamp,
            "fromVisit": self.fromVisit,
            "title": self.title,
            "url": self.url,
            "transition": self.transition,
            "duration": self.duration,
            "tip": self.tip
        }

    @classmethod
    def deserialize(cls, data):
        return Event(eventId=data['eventId'],
                     timestamp=data['timestamp'],
                     fromVisit=data['fromVisit'],
                     title=data['title'],
                     url=data['url'],
                     transition=data['transition'],
                     duration=data['duration'],
                     tip=data['tip'])


class Events:
    def __init__(self, initial_events=None, update_cases=None):
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
        if event.fromVisit != 0:
            e = self.get_event(event.fromVisit)
            if e is not None:
                e.tip = False

    def get_event(self, event_index):
        for event in self.events:
            if event.eventId == event_index:
                return event
        return None

    def filter_by_duration(self):
        return [event for event in self.events if event.duration != 0]

    def print_events(self, filtered):
        events = self.events if not filtered else self.filter_by_duration()
        for event in events:
            print(
                event.eventId,
                event.fromVisit,
                event.tip
            )

    def print_full_events(self, filtered):
        events = self.events if not filtered else self.filter_by_duration()
        for event in events:
            print(
                event.eventId,
                event.fromVisit,
                event.tip,
                event.title,
                event.url,
                event.transition,
                event.duration
            )

    def process_events(self):
        for event in self.events:
            self._update_tip(event)
            if self.update_cases:
                self.update_cases(event)

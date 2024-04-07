from object_tracker.tracker import Tracker


class TrackerMixin:
    tracker_attr = 'tracker'

    def __setattr__(self, attr, value) -> None:
        if not hasattr(self, self.tracker_attr):
            raise RuntimeError(f"TrackerMixin requires a '{self.tracker_attr}' attribute")

        tracker: Tracker = getattr(self, self.tracker_attr)
        if not tracker or not isinstance(tracker, Tracker):
            raise RuntimeError(f"TrackerMixin requires a valid Tracker object in '{self.tracker_attr}' attribute")

        curr = getattr(self, attr, value)
        super().__setattr__(attr, value)

        if tracker.is_active():
            tracker.track(attr=attr, old=curr, new=value)
            if tracker.auto_notify:
                tracker.notify_observers(attr, curr, value)
        return

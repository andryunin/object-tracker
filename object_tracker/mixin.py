"""
Copyright (c) Saurabh Pujari
All rights reserved.

This source code is licensed under the BSD-style license found in the LICENSE file in the root directory of this source tree.
"""

from object_tracker.tracker import Tracker


class TrackerMixin:
    tracker_attr = 'tracker'

    def __setattr__(self, attr, value) -> None:
        tracker: Tracker = getattr(self, self.tracker_attr, None)

        if tracker is None:
            if attr == self.tracker_attr:
                super().__setattr__(attr, value)
                return
            raise RuntimeError(f"TrackerMixin requires a '{self.tracker_attr}' attribute")

        if not isinstance(tracker, Tracker):
            raise RuntimeError(f"TrackerMixin requires a valid Tracker object in '{self.tracker_attr}' attribute")

        curr = getattr(self, attr, value)
        super().__setattr__(attr, value)

        if tracker.is_active():
            tracker.track(attr=attr, old=curr, new=value)
            if tracker.auto_notify:
                tracker.notify_observers(attr, curr, value)
        return

"""
Copyright (c) Saurabh Pujari
All rights reserved.

This source code is licensed under the BSD-style license found in the LICENSE file in the root directory of this source tree.
"""

import logging
from object_tracker.tracker import Tracker

logger = logging.getLogger(__name__)


class TrackerMixin:
    """
    Mixin class for tracking attribute changes.

    This mixin allows a class to automatically track changes to its attributes.
    It uses the `Tracker` object, stored in `tracker_attr`, to record changes and optionally notify observers.

    Until a tracker is set and activated, the mixin will behave like a normal class.

    ```
    from object_tracker import TrackerMixin, Tracker
    
    class User(TrackerMixin):
        def __init__(self, name, age):
            self.name = name
            self.age = age
            self.tracker = Tracker()
    ```

    Attributes:
        tracker_attr (str): The attribute holding the Tracker object.
    """

    tracker_attr: str = 'tracker'

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        logger.debug(f"TrackerMixin initialized for {self}")

    def __track_changes(self, attr, value, tracker=None) -> None:
        if attr == self.tracker_attr:
            if not isinstance(value, Tracker):
                raise RuntimeError(
                    f"TrackerMixin requires a valid Tracker object in '{self.tracker_attr}' attribute")
            return
        
        tracker: Tracker = getattr(self, self.tracker_attr, None)
        if tracker is None:
            return None
        
        if tracker.should_track(attr):
            curr = getattr(self, attr, value)
            tracker.track(attr=attr, old=curr, new=value)
        return

    def __setattr__(self, attr, value) -> None:
        self.__track_changes(attr, value)
        super().__setattr__(attr, value)

    def __setitem__(self, attr, value) -> None:
        self.__track_changes(attr, value)
        super().__setitem__(attr, value)

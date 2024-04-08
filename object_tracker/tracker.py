"""
Copyright (c) Saurabh Pujari
All rights reserved.

This source code is licensed under the BSD-style license found in the LICENSE file in the root directory of this source tree.
"""

import logging
from copy import deepcopy
from typing import Callable, Dict, List

from object_tracker.exceptions import InitialStateMissingException
from object_tracker.changelog import ChangeLog

logger = logging.getLogger(__name__)


ObserverType = Callable[[str, object, object], None]


class Tracker:
    """
    The Tracker class is responsible for tracking changes to an object's attributes.

    This class can be used in 3 ways - 
    1. By itself to track changes to an object's attributes.
    2. Along with the TrackerMixin class to automatically track changes to an object's attributes.
    3. Manually by calling the track method to track changes to an attribute.

    ```
    from object_tracker import Tracker

    # Track changes to an object's attributes.
    class MyClass:
        pass
    
    obj = MyClass()
    tracker = Tracker(obj)
    obj.attribute = 'new_value'
    print(tracker.has_changed(obj))


    # Use with the TrackerMixin class to automatically track an object's attributes.
    class MyClass(TrackerMixin):
        def __init__(self):
            self.tracker = Tracker()

    obj = MyClass()
    obj.attribute = 'new_value'
    print(obj.tracker.has_changed())


    # Manually calling the track method to track changes to an attribute.
    tracker = Tracker()
    tracker.track('attribute', 'old_value', 'new_value')
    print(tracker.has_attribute_changed('attribute'))
    ```
    """

    def __init__(
        self,
        initial_state: any = None,
        attributes: List[str] = None,
        observers: List[ObserverType] = None,
        attribute_observer_map: Dict[str, List[ObserverType]] = None,
        auto_notify: bool = True,
    ) -> None:
        
        self.log = ChangeLog() # init query log
        self.attributes = attributes # if it is None -> track all attributes
        self.observers = observers or []
        self.auto_notify = auto_notify
        self.attribute_observer_map = attribute_observer_map or {}
        # needed when this Tracker class is used as a standalone class
        self.initial_state = deepcopy(initial_state) if initial_state else None
        logger.debug(f"Tracker instance created: {self}")

    def __str__(self) -> str:
        return self.log.__str__()
    
    def __repr__(self) -> str:
        return self.log.__repr__()
    
    def __len__(self) -> int:
        return len(self.log.log)

    def _call_observers(self, attr, old, new, observers: List[ObserverType]) -> None:
        for observer in observers:
            observer(attr, old, new)

    def notify_observers(self, attr, old, new) -> None:
        """
        Notifies all observers 

        if auto_notify is False, this will have to be invoked manually.
        """
        if self.attribute_observer_map:
            observers = self.attribute_observer_map.get(attr, [])
            self._call_observers(attr, old, new, observers)
            logger.debug(f"Attribute Observers notified for change in {attr}")
        
        if self.observers:
            self._call_observers(attr, old, new, self.observers)
            logger.debug(f"Common Observers notified for change in {attr}")

    def should_track(self, attr) -> bool:
        """
        Checks if the attribute can be tracked
        """
        if self.attributes is None:
            return True
        return attr in self.attributes

    def set_initial_state(self, obj) -> None:
        """
        creates a deepcopy of the current object 
            -> needed when tracker is used independently without a mixin for __setattr__
        """
        self.initial_state = deepcopy(obj)
        logger.debug(f"Initial state set for {self}")

    def to_dict(self) -> dict:
        """
        Returns the log as a dictionary
        """
        return self.log.to_dict()

    def has_attribute_changed(self, attr, obj=None) -> bool:
        """
        Checks if an attribute has changed by verifying against the log
        """
        if obj:
            if not self.initial_state:
                raise InitialStateMissingException()
            return getattr(self.initial_state, attr, None) != getattr(obj, attr, None)

        return self.log.has_changes(attr)

    def has_changed(self, obj=None) -> bool:
        """
        Checks if any attribute of the object has been changed by verifying against the log

        If obj is provided, it will compare the object with the initial_state. If not, it will check the log
        """
        if obj:
            if not self.initial_state:
                raise InitialStateMissingException()
            return obj.__dict__ != self.initial_state.__dict__

        attrs = self.log.get_unique_attributes()
        return any([self.log.has_changes(attr) for attr in attrs])
    
    def track(self, attr, old, new, raise_excp=True) -> None:
        """
        Tracks an attribute change. Untracked if the old and new values are the same
        """            
        if old == new:
            return
        self.log.push(attr=attr, old=old, new=new)
        if self.auto_notify:
            self.notify_observers(attr, old, new)

"""
Copyright (c) Saurabh Pujari
All rights reserved.

This source code is licensed under the BSD-style license found in the LICENSE file in the root directory of this source tree.
"""

from copy import deepcopy
from object_tracker.exceptions import InitialStateMissingException
from object_tracker.query_log import QueryLog


class Tracker:
    """

    The Tracker

    """

    def __init__(
        self,
        initial_state=None,
        attributes=None,
        observers=None,
        attribute_observer_map=None,
        auto_notify=True,
        active=False
    ) -> None:
        
        self.log = QueryLog() # init query log
        self.attributes = attributes or []
        self.observers = observers or []
        self.auto_notify = auto_notify
        self.attribute_observer_map = attribute_observer_map or {}
        # needed when this Tracker class is used as a standalone class
        self.initial_state = deepcopy(initial_state) if initial_state else None
        self.active = active or False

    def __str__(self) -> str:
        return self.log.__str__()
    
    def __repr__(self) -> str:
        return self.log.__repr__()
    
    def __len__(self) -> int:
        return len(self.log.log)

    def _call_observers(self, attr, old, new, observers: list):
        for observer in observers:
            observer(attr, old, new)

    def notify_observers(self, attr, old, new) -> None:
        """

        Notifies all observers 

        if self.auto_notify is False
        This method will have to be called manually

        """
        if self.attribute_observer_map:
            observers = self.attribute_observer_map.get(attr, [])
            self._call_observers(attr, old, new, observers)
            return
        
        if self.observers:
            if self.attributes and attr not in self.attributes:
                return 
            else:
                self._call_observers(attr, old, new, self.observers)

    def activate(self):
        """
        Activates the tracker - now it can track changes without raising exceptions
        """
        if not self.active:
            self.active = True

    def is_active(self) -> bool:
        """
        Returns the state of the tracker
        """
        return self.active
    
    def raise_excp_if_not_active(self):
        """
        Raises exception if the tracker is not active
        """
        if not self.active:
            raise InitialStateMissingException("Tracker not active - use tracker.start() to activate it")

    def set_initial_state(self, obj) -> None:
        """
        creates a deepcopy of the current object 
            -> needed when tracker is used independently without a mixin for __setattr__
        """
        self.initial_state = deepcopy(obj)

    def print(self):
        """
        Utility std print fn
        """
        self.log.print()

    def has_attribute_changed(self, attr, obj=None) -> bool:
        """
        Checks if an attribute has changed by verifying against the log
        """

        if obj:
            if not self.initial_state:
                raise InitialStateMissingException()
            return getattr(self.initial_state, attr, None) != getattr(obj, attr, None)

        last = None

        for i in range(len(self.log.log) - 1, -1, -1):
            if attr != self.log.log[i].attr:
                continue
            if not last:
                last = self.log.log[i]
                break

        if not last:
            return False

        return last.old != last.new

    def has_changed(self, obj=None) -> bool:
        """
        Checks if any attribute of the object has been changed by verifying against the log
        """
        if obj:
            if not self.initial_state:
                raise InitialStateMissingException()
            return obj.__dict__ != self.initial_state.__dict__

        seen = set()
        for entry in self.log.log:
            if entry.attr in seen:
                continue
            if self.has_attribute_changed(entry.attr):
                return True
            seen.add(entry.attr)
        return False
    
    def track(self, attr, old, new):
        """
        Tracks an attribute change
        """
        self.raise_excp_if_not_active()
        self.log.push(attr=attr, old=old, new=new)

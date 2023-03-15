"""
Copyright (c) Saurabh Pujari
All rights reserved.

This source code is licensed under the BSD-style license found in the LICENSE file in the root directory of this source tree.
"""

from copy import deepcopy
import inspect
from .changelog import ObjectChangeLog    


class ObjectTracker:
    """
    A tracker to see if an object has changed 

    Usage : 

        def observer(attr, old, new):
            print(f"Observer : {attr} -> {old} - {new}")

        class User(ObjectTracker):
            def __init__(self, name) -> None:
                self._observers = [observer,]
                self.name = name


        user = User("A")
        print(user._has_changed()) # False

        user.name = "B"
        # Observer : name -> A - B

        print(user._has_changed()) # True
        
    """

    # Class variables of the tracker 
    # In the case where ObjectTracker's __init__ method is not called
    # The class variables will be used. This will only work with Singletons 
    # Otherwise there will be overwrites/loss of data due to a common changelog
    _observers = []
    _auto_notify = True
    _ignore_init = True
    _changelog = ObjectChangeLog() # class common changelog
    _observable_attributes = []
    _attribute_observer_map = {}
    _initial_state = None
    _tracker_attrs = [
        '_observers', 
        '_auto_notify', 
        '_changelog', 
        '_observable_attributes', 
        '_attribute_observer_map', 
        '_initial_state'
        '_tracker_attrs'
    ]

    def __init__(self, **kwargs) -> None:
        """
            Initialise all instance properties for the tracker
        """
        self._observers = kwargs.get("observers", [])
        self._auto_notify = kwargs.get("auto_notify", True)
        self._ignore_init = kwargs.get("ignore_init", True)
        self._changelog = ObjectChangeLog() # Instance changelog
        self._observable_attributes = kwargs.get("observable_attributes", [])
        self._attribute_observer_map = kwargs.get("attribute_observer_map", {})
        self._initial_state = kwargs.get("initial_state")


    def __setattr__(self, attr, value) -> None:
        """
            Overrides __setattr__ to track history and notify observers
        """
        curr = getattr(self, attr, value)
        super().__setattr__(attr, value)

        # get previous frame
        caller_frame = inspect.currentframe().f_back

        # CPython implementation detail: 
        #
        # https://docs.python.org/3/library/inspect.html#inspect.currentframe
        #
        # This function relies on Python stack frame support in the interpreter, 
        # which isn’t guaranteed to exist in all implementations of Python. 
        # If running in an implementation without Python stack frame support this function returns None.

        if caller_frame:
            caller_fn = caller_frame.f_code.co_name
            if (
                caller_frame.f_locals['self'].__class__ == self.__class__
                and '__init__' in caller_fn
                and self._ignore_init
            ):
                # Ignore changes made in the __init__ fn of the same class if self._ignore_init
                return

        self._changelog.push(
            attr=attr, 
            old=curr, 
            new=value
        )

        if self._auto_notify:
            self._notify_observers(attr, curr, value)

    def _call_observers(self, attr, old, new, observers: list):
        for observer in observers:
            observer(attr, old, new)

    def _notify_observers(self, attr, old, new):
        """
            Notifies all observers 

            if self._auto_notify is False
            This method will have to be called manually
        """
        if self._attribute_observer_map:
            observers = self._attribute_observer_map.get(attr, [])
            self._call_observers(attr, old, new, observers)
            return
        
        if self._observers:
            if self._observable_attributes and attr not in self._observable_attributes:
                return 
            else:
                self._call_observers(attr, old, new, self._observers)

    def _has_attribute_changed(self, attr):
        """
            print(obj._has_attribute_changed('name'))

            Returns a bool on whether the given attribute has changed or not
        """
        if self._initial_state:
            return getattr(self._initial_state, attr, None) != getattr(self, attr, None)
        return self._changelog.has_attribute_changed(attr)

    def _has_changed(self):
        """
            print(obj._has_changed('name'))

            Returns a bool on whether the object as a whole has changed or not
        """
        if self._initial_state:
            curr_dict = deepcopy(self.__dict__)
            curr_dict.pop('_initial_state')
            return curr_dict != self._initial_state.__dict__
        return self._changelog.has_changed()
    
    def _track_initial_state(self):
        """
            creates a deepcopy of the current object for faster 'has_changed' comparision later
        """
        self._initial_state = deepcopy(self)

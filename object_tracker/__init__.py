"""
The object_tracker package provides classes to track changes to an object's attributes

```
from object_tracker import TrackerMixin, Tracker

# Eg. 1
class User(TrackerMixin):
    def __init__(self, name, age):
        self.name = name
        self.age = age
        self.tracker = Tracker()

user = User(name='Alice', age=30)
user.name = 'Bob'
print(user.tracker.has_changed()) # True


# Eg. 2
class MyClass:
        pass
    
obj = MyClass()
tracker = Tracker(obj)
obj.attribute = 'new_value'
print(tracker.has_changed(obj)) # True


# Eg. 3
tracker = Tracker()
tracker.track('attribute', 'old_value', 'new_value')
print(tracker.has_attribute_changed('attribute')) # True

```

Copyright (c) Saurabh Pujari
All rights reserved.

This source code is licensed under the BSD-style license found in the LICENSE file in the root directory of this source tree.
"""

import inspect
import logging
from .exceptions import InitialStateMissingException, InvalidChangeLogOperationException
from .changelog import Entry, ChangeLog
from .tracker import Tracker


__all__ = [
    'Entry',
    'InitialStateMissingException',
    'InvalidChangeLogOperationException',
    'TrackerMixin',
    'ChangeLog',
    'Tracker'
]

logger = logging.getLogger(__name__)


class TrackerMixin:
    """
    Mixin class for tracking attribute changes.
    Overrides the `__setattr__` and `__setitem__` methods to track changes.

    It uses the `Tracker` object, stored in `tracker_attr`, to record changes.

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
        logger.debug(f"Tracker initialized for {self}")

    def __track_changes(self, attr, value, tracker=None) -> None:
        if attr == self.tracker_attr:
            return

        tracker: Tracker = getattr(self, self.tracker_attr, None)
        if tracker is None:
            return None

        if tracker.should_track(attr):
            curr = getattr(self, attr, value)
            stack = None
            if tracker.store_call_stack():
                stack = filter(
                    lambda f: not __file__.startswith(f.filename), inspect.stack()
                )
            tracker.track(attr=attr, old=curr, new=value, stack=stack)

        return

    def __setattr__(self, attr, value) -> None:
        self.__track_changes(attr, value)
        super().__setattr__(attr, value)

    def __setitem__(self, attr, value) -> None:
        self.__track_changes(attr, value)
        super().__setitem__(attr, value)


def track(
    *attributes,
    observers: list = None,
    attribute_observer_map: dict = None,
    auto_notify: bool = True,
    stack_trace: bool = True,
    tracker_attribute: str = 'tracker',
    changes_only: bool = False,
):
    """
    Decorator for tracking attribute changes in a class.

    ```
    from object_tracker import track

    @track('name', 'age')
    class User:
        def __init__(self, name, age):
            self.name = name
            self.age = age

    user = User('Alice', 30)
    user.name = 'Bob'
    print(user.tracker.has_changed('name')) # True
    ```

    Args:
        *attributes: The attributes to track.
        observers (list, optional): The observers to notify when an attribute changes.
        attribute_observer_map (dict, optional): A map of attributes to observers.
        auto_notify (bool, optional): Whether to automatically notify observers when an attribute changes.
        tracker_attribute (str, optional): The attribute holding the Tracker object.

    Returns:
        The decorated class with attribute tracking.
    """
    def decorator(cls):
        class Tracked(TrackerMixin, cls):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.tracker_attr = tracker_attribute or self.tracker_attr
                setattr(
                    self,
                    self.tracker_attr, 
                    Tracker(
                        initial_state=self,
                        attributes=attributes,
                        observers=observers,
                        attribute_observer_map=attribute_observer_map,
                        auto_notify=auto_notify,
                        stack_trace=stack_trace,
                        changes_only=changes_only,
                    ),
                )

        Tracked.__name__ = cls.__name__
        Tracked.__module__ = cls.__module__
        Tracked.__doc__ = cls.__doc__
        return Tracked

    return decorator

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

from .exceptions import InitialStateMissingException, InvalidQueryLogOperationException
from .mixin import TrackerMixin
from .query_log import Entry, QueryLog
from .tracker import Tracker


__all__ = [
    'Entry',
    'InitialStateMissingException',
    'InvalidQueryLogOperationException',
    'TrackerMixin',
    'QueryLog',
    'Tracker'
]

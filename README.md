<p align="center">
    <img src="https://github.com/saurabh0719/object-tracker/assets/42310348/e927be52-f48e-4098-be93-d292570a018e" width ="600">
</p>

<br>

A pure python object state tracker. Monitor all changes in your object's lifecycle, query the history changelog, and trigger callback functions to capture them. :pencil:

```sh
$ pip install object-tracker
```

<div align="center">
    <strong><a href="https://github.com/saurabh0719/object-tracker">Github</a> | <a href="https://saurabh0719.github.io">Website</a> | <a href="https://github.com/saurabh0719/object-tracker/releases">Release notes</a> </strong>
</div>

Tested for python `3.7` and above.

<span id="features"></span>
## Key Features

-  Determine if a python object has changed state during it's lifecycle.
-  Investigate change history by querying a structured changelog.
-  Trigger callback functions whenever an (or any) attribute has changed.
-  Use it as a decorator, a class mixin or on its own.

<hr>

<span id="contents"></span>
## Table of Contents :
* [Key Features](#features)
* [Basic Usage](#usage)   
* [How does it work?](#how)
* [API](#trackerapi)
* [Tests](#tests)
* [Release notes](#releases)
* [License](#license) 


<span id="usage"></span>
## Basic Usage 

Use the `@track` decorator to track an object's attributes.

```python

from object_tracker import track

def observer(attr, old, new):
    print(f"Observer : {attr} -> {old} - {new}")

@track('name', 'age', observers=[observer,])
class User:
    def __init__(self, name, age):
        self.name = name
        self.age = age

user = User(name='Alice', age=30)
user.name = 'Bob'
# Observer : name -> Alice - Bob
print(user.tracker.has_changed()) 
# True
print(user.tracker.has_attribute_changed('name'))
# True

```

Or use the `Tracker` class 

```python

class MyClass:
        pass
    
obj = MyClass()
tracker = Tracker(obj)
obj.attribute = 'new_value'
print(tracker.has_changed(obj))
# True

```

Or use it with the mixin class `TrackerMixin`

```python

from object_tracker import TrackerMixin, Tracker
    
class User(TrackerMixin):
    def __init__(self, name, age):
        self.name = name
        self.age = age
        self.tracker = Tracker()

```

<span id="help"></span>
## How does it work?

The decorator `@track` and the mixin `TrackerMixin` implement the `__setattr__` and `__setitem__` dunder methods to intercept and log a change to an attribute. 

The tracker is an instance of the `Tracker` class which logs all changes to the `ChangeLog`

The entire module is roughly 310 LOC, don't hesitate to read from source directly!

[Go back to the table of contents](#contents)


<span id="trackerapi"></span>
## API

## @track

```python
def track(
    *attributes: List[str],
    observers: List[ObserverType] = None,
    attribute_observer_map: Dict[str, List[ObserverType]] = None,
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
        *attributes: 
            The attributes to track.

        observers (list, optional): 
            The observers to notify when an attribute changes. Default is None.

        attribute_observer_map (dict, optional): 
            A map of attributes to observers.Default is None.

        auto_notify (bool, optional):
            Whether to automatically notify observers when an attribute changes.
            Default is True.

        stack_trace (bool, optional):
            Whether to store the call stack when an attribute changes. Default is True.

        tracker_attribute (str, optional):
            The attribute holding the Tracker object. Default is 'tracker'.

        changes_only (bool, optional):
            Whether to track only changes to attributes or all assignments.
            Default is False.

    Returns:
        The decorated class with attribute tracking.
    """
```

[Go back to the table of contents](#contents)


## TrackerMixin

```python
class TrackerMixin:
    """
    Mixin class for tracking attribute changes.
    Overrides the `__setattr__` and `__setitem__` methods to track changes.

    It uses the `Tracker` object, stored in `tracker_attr`, to record changes.
    Modify the `tracker_attr` attribute to change the attribute name.

    ```
    from object_tracker import TrackerMixin, Tracker
    
    class User(TrackerMixin):
        def __init__(self, name, age):
            self.name = name
            self.age = age
            self.tracker = Tracker()
    ```

    Attributes:
        tracker_attr (str):
            The attribute holding the Tracker object. Default is `tracker`.
    """
```

[Go back to the table of contents](#contents)


## Tracker

```python
class Tracker:
    """
    The Tracker class is responsible for tracking changes to an object's attributes.
    ```
    from object_tracker import Tracker

    # Track changes to an object's attributes.
    class MyClass:
        pass
    
    obj = MyClass()
    tracker = Tracker(obj)
    obj.attribute = 'new_value'
    print(tracker.has_changed(obj))


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
        stack_trace: bool = True,
        changes_only: bool = False,
    ) -> None:
        """
        Initializes the Tracker instance.

        Args:
            initial_state (any):
                The initial state of the object to be tracked. Default is None.

            attributes (List[str]): 
                The attributes to track. Default is None ie. all attributes are tracked.

            observers (List[ObserverType]):
                The list of observers to notify on attribute change. Default is None.

            attribute_observer_map (Dict[str, List[ObserverType]]):
                A map of attributes to observers. Default is None.

            auto_notify (bool):
                Whether to automatically notify observers on attribute change.
                Default is True.

            stack_trace (bool):
                Whether to store the call stack when an attribute changes.
                Default is True.

            changes_only (bool):
                Whether to track only the attributes that have changed.
                Default is False.

        Attributes:
            log (ChangeLog):
                The log to store attribute changes.
        """
```

[Go back to the table of contents](#contents)


## ChangeLog

The `tracker` instance has the `log` inside it containing a list of `Entry` objs

Each `Entry` in a change log has -
-   `attr` - The attribute that was changed
-   `old` - copy of the old value
-   `new` - copy of the new value
-   `timestamp` - UTC datetime
-   `stack` - a list of `frames` from inspect leading up to the change.


```python
class ChangeLog:
    """
    The ChangeLog class is responsible for storing and managing a log of attribute changes.

    This class provides methods to add new entries to the log, filter the log based on attribute names, 
    exclude certain attributes from the log, and clear the log.

    Methods:

    - push(attr, old, new, stack=None): Pushes a new entry to the log.

    - filter(*attrs, changes_only=False): Filters the log based on the given attributes.

    - exclude(*attrs, changes_only=False): Excludes the given attributes from the log.

    - first(): Returns the first log entry.

    - last(): Returns the last log entry.

    - all(): Returns all log entries.

    - count(): Returns the number of log entries.

    - replay(): A generator to print the logs in a human-readable format.

    - get_unique_attributes(): Returns all attributes in the log.

    - has_changed(attr): Checks if any attribute of the object has been changed by verifying against the log.

    - reset_buffer(): Resets the buffer.

    Eg.

        The `tracker` obj has the `log` attribute which is an instance of the `ChangeLog` class.

        tracker.log.filter('name', 'age') -> Returns logs for 'name' and 'age' attributes

        tracker.log.exclude('name') -> Excludes logs for 'name' attribute

        tracker.log.first() -> Returns the first log entry

        tracker.filter('name').count() -> Returns the number of log entries for 'name' attribute
    """
```


[Go back to the table of contents](#contents)


<span id="examples"></span>
## Examples

The `replay()` method was repurposed from ![Madison May's tracker](https://github.com/madisonmay/tracker).

```python
from object_tracker import track

@track('name', 'age')
class User:
    def __init__(self, name, age):
        self.name = name
        self.age = age

user = User(name='Alice', age=30)
user.name = 'Bob'
user.name = 'John'
user.age = 31

print("\n Has object changed - ", user.tracker.has_changed()) # True
print("\n Has 'name' changed - ", user.tracker.has_attribute_changed('name')) # True
print("\n Num of changes in 'name' - ", user.tracker.log.filter('name').count()) # 2
print("\n Num of changes in 'age' - ", user.tracker.log.filter('age').count()) # 1

print("\n All logs - ")
for log in user.tracker.log.replay():
    print(log)

```

Output - 

```

 Has object changed -  True

 Has 'name' changed -  True

 Num of changes in 'name' -  2

 Num of changes in 'age' -  1

 All logs - 
--------------------------------------------------
name = 'Bob'

    trial.py: 10 - <module>
    user.name = 'Bob'

--------------------------------------------------
name = 'John'

    trial.py: 11 - <module>
    user.name = 'John'

--------------------------------------------------
age = 31

    trial.py: 12 - <module>
    user.age = 31

```

<hr>

<span id="tests"></span>
## Tests 

Run this command inside the base directory to execute all tests inside the `tests` folder:

```sh
$ python -m unittest -v
```

[Go back to the table of contents](#contents)

<hr>

<span id="releases"></span>
## Release notes 

* Latest - `v2.0.0` 

View object-tracker's detailed [release history](https://github.com/saurabh0719/object-tracker/releases/).

[Go back to the table of contents](#contents)

<hr>

<span id="license"></span>
## License

```
Copyright (c) Saurabh Pujari
All rights reserved.

This source code is licensed under the BSD-style license found in the LICENSE file in the root directory of this source tree.
```

[Go back to the table of contents](#contents)

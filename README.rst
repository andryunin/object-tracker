object-tracker
--------------

A pure python object state tracker. Monitor all changes in your object's lifecycle, query the history changelog, and trigger callback functions to capture them.

View the `Github repository <https://github.com/saurabh0719/object-tracker>`__ and the `official docs <https://github.com/saurabh0719/object-tracker#README>`__.

.. code:: sh

    $ pip install object-tracker

Tested for python 3.6, 3.7 and above.

Key Features
------------

-  Determine if a python object has changed state during it's lifecycle.
-  Investigate change history by querying a structured changelog.
-  Trigger callback functions whenever an (or any) attribute has changed.
-  Use it as a decorator, a class mixin or on its own.

License
-------

::

    Copyright (c) Saurabh Pujari
    All rights reserved.

    This source code is licensed under the BSD-style license found in the LICENSE file in the root directory of this source tree.


Usage :
~~~~~~~~~~~~~

Use the `@track` decorator to track an object's attributes.

.. code:: python

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

Or use the `Tracker` class 

.. code:: python

    class MyClass:
        pass
    
    obj = MyClass()
    tracker = Tracker(obj)
    obj.attribute = 'new_value'
    print(tracker.has_changed(obj))
    # True


Or use it with the mixin class `TrackerMixin`:


.. code:: python

   from object_tracker import TrackerMixin, Tracker
    
    class User(TrackerMixin):
        def __init__(self, name, age):
            self.name = name
            self.age = age
            self.tracker = Tracker()

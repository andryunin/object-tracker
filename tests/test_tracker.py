"""
python -m unittest tests.test_tracker -v
"""

import unittest
from object_tracker import InitialStateMissingException, Tracker, TrackerMixin

def observer(attr, old, new):
    return attr, old, new

# Demo object for testing
class User(TrackerMixin):
    def __init__(self, name, age) -> None:
        self.name = name
        self.age = age
        self.tracker = Tracker(observers=[observer,])

class UntrackedUser:
    def __init__(self, name, age) -> None:
        self.name = name
        self.age = age

class TestTracker(unittest.TestCase):
    def setUp(self):
        pass

    def test_ops(self):
        user = User("A", 100)
        self.assertFalse(user.tracker.has_attribute_changed('name'))
        self.assertFalse(user.tracker.has_changed())
        user.name = "B"
        self.assertTrue(user.tracker.has_attribute_changed('name'))
        self.assertTrue(user.tracker.has_changed())
        user.tracker.log.delete()

    def test_query(self):
        user = User("A", 100)
        self.assertFalse(user.tracker.has_changed())
        user.name = "B"
        user.age = 20
        self.assertEqual(user.tracker.log.count(), 2)
        self.assertEqual(user.tracker.log.filter('name').count(), 1)
        self.assertEqual(user.tracker.log.filter('name', 'age').count(), 2)

        qs = user.tracker.log.exclude('name').all()

        self.assertEqual(qs[0].attr, 'age')

        # Tests for first() and last()
        user.name = "C"
        user.age = 30
        self.assertEqual(user.tracker.log.first().new, "B")
        self.assertEqual(user.tracker.log.first().old, "A")
        self.assertEqual(user.tracker.log.last().new, 30)
        self.assertEqual(user.tracker.log.last().old, 20)

        self.assertEqual(user.tracker.log.filter('name').count(), 2)
        self.assertEqual(user.tracker.log.filter('name').first().new, "B")
        self.assertEqual(user.tracker.log.filter('name').last().new, "C")

        user.tracker.log.exclude('name').delete()
        self.assertEqual(user.tracker.log.count(), 2)
        self.assertEqual(user.tracker.log.log[0].attr, 'name')

        user.tracker.log.delete()
        self.assertEqual(user.tracker.log.count(), 0)

    def test_tracker_only(self):
        user = UntrackedUser("A", 100)
        tracker = Tracker()
        self.assertEqual(tracker.initial_state, None)
        self.assertRaises(InitialStateMissingException, tracker.has_changed, user)
        tracker = Tracker(initial_state=user)
        self.assertFalse(tracker.has_changed(user))
        user.name = "B"
        self.assertTrue(tracker.has_changed(user))
        self.assertTrue(tracker.has_attribute_changed('name', user))


class TestObjectTracker(unittest.TestCase):
    def setUp(self):
        pass

    def test_change(self):
        user = User("A", 100)
        self.assertFalse(user.tracker.has_changed())
        user.name = "B"
        self.assertTrue(user.tracker.has_changed())

    def test_attribute_change(self):
        user = User("A", 100)
        self.assertFalse(user.tracker.has_attribute_changed('name'))
        user.name = "B"
        self.assertTrue(user.tracker.has_attribute_changed('name'))

    def test_defaults(self):
        user = User("A", 100)
        self.assertTrue(user.tracker.active)
        self.assertTrue(user.tracker.auto_notify)
        self.assertEqual(len(user.tracker.log), 0)

        user_2 = User("B", 50)
        assert user.name == "A"
        assert user_2.name == "B"
        assert user_2.age == 50

        self.assertEqual(len(user.tracker.observers), 1)
        assert callable(user.tracker.observers[0])

    def test_track_initial_state(self):
        user = User("A", 100)
        user.tracker.set_initial_state(user)
        self.assertFalse(user.tracker.has_changed())
        self.assertFalse(user.tracker.has_attribute_changed('name'))
        user.name = "B"
        self.assertTrue(user.tracker.has_changed())
        self.assertTrue(user.tracker.has_attribute_changed('name'))

    def test_ignore_init(self):
        user = User("A", 100)
        assert user.tracker.has_changed() is False
        user.name = "B"
        assert user.tracker.has_changed() is True
        user.tracker.log.delete()
        
        class Example:
            def __init__(self, name, age) -> None:
                self.user = User(name, age)
                assert self.user.tracker.has_changed() is False
                self.user.name = "B"
                assert self.user.tracker.has_changed() is True

        Example("A", 50)

    def test_activate_deactivate(self):
        user = User("A", 100)
        self.assertTrue(user.tracker.is_active())

        user.name = "B"
        self.assertTrue(user.tracker.has_changed())
        self.assertEqual(len(user.tracker.log), 1)

        user.tracker.deactivate()
        self.assertFalse(user.tracker.is_active())
        user.name = "C"
        self.assertEqual(len(user.tracker.log), 1)

        user.tracker.activate()
        self.assertTrue(user.tracker.is_active())
        user.name = "D"
        self.assertEqual(len(user.tracker.log), 2)

        self.assertEqual(user.tracker.log.last().new, "D")
        self.assertEqual(user.tracker.log.last().old, "C")
        self.assertEqual(user.tracker.log.first().new, "B")
        self.assertEqual(user.tracker.log.first().old, "A")
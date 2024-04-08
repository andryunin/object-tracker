# """
# Copyright (c) Saurabh Pujari
# All rights reserved.

# This source code is licensed under the BSD-style license found in the LICENSE file in the root directory of this source tree.
# """

from typing import List, Optional, Set
from collections import namedtuple
from datetime import datetime, timezone
from object_tracker.exceptions import InvalidChangeLogOperationException


class Entry(namedtuple('Entry', ['attr', 'old', 'new', 'timestamp'])):
    """
    The Entry class is a named tuple that represents a single log entry in the ChangeLog.
    """
    def __new__(cls, attr, old, new):
        return super().__new__(cls, attr, old, new, datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            'attr': self.attr,
            'old': self.old,
            'new': self.new,
            'timestamp': self.timestamp.isoformat(),
        }


class ChangeLog:
    """
    The ChangeLog class is responsible for storing and managing a log of attribute changes.

    This class provides methods to add new entries to the log, filter the log based on attribute names, 
    exclude certain attributes from the log, and clear the log.
    """

    def __init__(self) -> None:
        self.log: List[Entry] = []
        self.buffer: List[Entry] = []

    def __str__(self) -> str:
        return f"ChangeLog: {len(self.log)}"
    
    def __len__(self) -> int:
        return len(self.log)
    
    def __iter__(self):
        return iter(self.log)

    def to_dict(self) -> dict:
        return [entry.to_dict() for entry in self.log]
    
    def reset_buffer(self):
        if self.buffer:
            self.buffer = []

    def get_selected_logs(self) -> List[Entry]:
        logs = self.buffer if self.buffer else self.log
        self.reset_buffer()
        return logs

    def apply_filters(self, attrs, exclude=False) -> 'ChangeLog':
        """
        applies filters on the log and saves it in the buffer
        """
        if not isinstance(attrs, (list, tuple, set)):
            raise InvalidChangeLogOperationException(
                "filter/exclude method needs a sequence of attributes as arguments"
            )

        if exclude:
            self.buffer = [entry for entry in self.log if entry.attr not in attrs]
        else:
            self.buffer = [entry for entry in self.log if entry.attr in attrs]

        return self

    def filter(self, *attrs) -> 'ChangeLog':
        """
        eg: obj.filter('name', 'age').all()
        """
        if not attrs:
            raise InvalidChangeLogOperationException("filter method needs atleast one attribute")
        return self.apply_filters(attrs)
    
    def exclude(self, *attrs) -> 'ChangeLog':
        """
        eg: obj.exclude('name').all()
        """
        if not attrs:
            return InvalidChangeLogOperationException("exclude method needs atleast one attribute")
        return self.apply_filters(attrs, True)
    
    def first(self) -> Optional[Entry]:
        logs = self.get_selected_logs()
        return logs[0] if logs else None

    def last(self) -> Optional[Entry]:
        logs = self.get_selected_logs()
        return logs[-1] if logs else None
    
    def all(self) -> List[Entry]:
        logs = self.get_selected_logs()
        return logs

    def delete(self) -> None:
        if self.buffer:
            self.log = [entry for entry in self.log if entry not in self.buffer]
        else:
            self.log = []
        self.reset_buffer()

    def count(self) -> int:
        return len(self.get_selected_logs())

    def push(self, attr, old, new) -> None:
        """
        Pushes a new entry to the log
        """
        self.log.append(
            Entry(
                attr=attr, 
                old=old, 
                new=new
            )
        )

    def get_unique_attributes(self) -> Set[str]:
        """
        Returns all attributes in the log
        """
        log = self.get_selected_logs()
        return set([entry.attr for entry in log])

    def get_last_change(self, attr=None) -> Optional[Entry]:
        """
        Returns the last valid change in the log
        """
        log = self.get_selected_logs()
        for i in range(len(log) - 1, -1, -1):
            if attr is not None and log[i].attr != attr:
                continue
            return log[i]
        return None

    def get_first_change(self, attr=None) -> Optional[Entry]:
        """
        Returns the first valid change in the log
        """
        log = self.get_selected_logs()
        for i in range(len(log)):
            if attr is not None and log[i].attr != attr:
                continue
            return log[i]
        return None

    def has_changes(self, attr) -> bool:
        """
        Checks if an attribute has changed by verifying against the log
        """
        return True if self.get_last_change(attr) else False

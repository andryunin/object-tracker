# """
# Copyright (c) Saurabh Pujari
# All rights reserved.

# This source code is licensed under the BSD-style license found in the LICENSE file in the root directory of this source tree.
# """

from typing import List, Optional, Set
from collections import namedtuple
from datetime import datetime, timezone
from object_tracker.exceptions import InvalidQueryLogOperationException


class Entry(namedtuple('Entry', ['attr', 'old', 'new', 'timestamp'])):
    """
    The Entry class is a named tuple that represents a single log entry in the QueryLog.
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


class QueryLog:
    """
    The QueryLog class is responsible for storing and managing a log of attribute changes.

    This class provides methods to add new entries to the log, filter the log based on attribute names, 
    exclude certain attributes from the log, and clear the log.
    """

    def __init__(self) -> None:
        self.log: List[Entry] = []
        self.buffer: List[Entry] = []

    def _reset_buffer(self):
        if self.buffer:
            self.buffer = []

    def _get_active_logs(self) -> List[Entry]:
        return self.buffer if self.buffer else self.log

    def __str__(self) -> str:
        return f"QueryLog -> BUFFER {len(self.buffer)} LOG {len(self.log)}"
    
    def __repr__(self) -> str:
        return str({'log': len(self.log), 'buffer': len(self.buffer)})
    
    def __len__(self) -> int:
        return len(self._get_active_logs())
    
    def __iter__(self):
        return iter(self._get_active_logs())

    def to_dict(self) -> dict:
        return {
            'log': [entry.to_dict() for entry in self.log],
            'buffer': [entry.to_dict() for entry in self.buffer],
        }

    def _filter(self, entry: Entry, attrs) -> bool:
        return entry.attr in attrs if attrs else True

    def _process_filter(self, attrs=None, exclude=False) -> 'QueryLog':
        """
        Processes filter attrs and saves it in the buffer
        """
        if attrs is None:
            _attrs = []
        elif isinstance(attrs, str):
            _attrs = set(attrs)
        else:
            if not isinstance(attrs, (list, tuple, set)):
                raise InvalidQueryLogOperationException(
                    "filter/exclude method needs a sequence of attributes as arguments"
                )
            _attrs = set(attrs) if not isinstance(attrs, set) else attrs

        if exclude:
            self.buffer = [item for item in self.log if not self._filter(item, _attrs)]
        else:
            self.buffer = [item for item in self.log if self._filter(item, _attrs)]

        return self

    def filter(self, *attrs) -> 'QueryLog':
        """
        eg: obj.filter('name', 'age').fetch()
        """
        if not attrs:
            raise InvalidQueryLogOperationException("filter method needs atleast one attribute")
        return self._process_filter(attrs)
    
    def exclude(self, *attrs) -> 'QueryLog':
        """
        eg: obj.exclude('name').fetch()
        """
        if not attrs:
            return InvalidQueryLogOperationException("exclude method needs atleast one attribute")
        return self._process_filter(attrs, True)
    
    def first(self) -> Optional[Entry]:
        logs = self._get_active_logs()
        self._reset_buffer()
        return logs[0] if logs else None

    def last(self) -> Optional[Entry]:
        logs = self._get_active_logs()
        self._reset_buffer()
        return logs[-1] if logs else None
    
    def fetch(self) -> List[Entry]:
        logs = self._get_active_logs()
        self._reset_buffer()
        return logs

    def flush(self) -> None:
        if self.buffer:
            self.log = [item for item in self.log if item not in self.buffer]
        else:
            self.log = []
        self._reset_buffer()

    def count(self) -> int:
        cnt = self.__len__()
        self._reset_buffer()
        return cnt

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
        log = self._get_active_logs()
        self._reset_buffer()
        return set([item.attr for item in log])

    def get_last_change(self, attr=None) -> Optional[Entry]:
        """
        Returns the last valid change in the log
        """
        log = self._get_active_logs()
        for i in range(len(log) - 1, -1, -1):
            if attr is not None and log[i].attr != attr:
                continue
            return log[i]
            
        self._reset_buffer()
        return None

    def get_first_change(self, attr=None) -> Optional[Entry]:
        """
        Returns the first valid change in the log
        """
        log = self._get_active_logs()
        for i in range(len(log)):
            if attr is not None and log[i].attr != attr:
                continue
            return log[i]
        
        self._reset_buffer()
        return None

    def has_changes(self, attr) -> bool:
        """
        Checks if an attribute has changed by verifying against the log
        """
        return True if self.get_last_change(attr) else False

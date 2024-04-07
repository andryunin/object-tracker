"""
Copyright (c) Saurabh Pujari
All rights reserved.

This source code is licensed under the BSD-style license found in the LICENSE file in the root directory of this source tree.
"""

from object_tracker.entry import Entry
from object_tracker.exceptions import InvalidQueryLogOperationException


class QueryLog:
    """
    The QueryLog class is responsible for storing and managing a log of attribute changes.

    This class provides methods to add new entries to the log, filter the log based on attribute names, 
    exclude certain attributes from the log, and clear the log.
    """

    def __init__(self) -> None:
        self.log = []
        self.buffer = []

    def __str__(self) -> str:
        return f"QueryLog -> BUFFER {len(self.buffer)} LOG {len(self.log)}"
    
    def __repr__(self) -> str:
        return str({'log': len(self.log), 'buffer': len(self.buffer)})
    
    def __len__(self) -> int:
        return len(self.buffer) if self.buffer else len(self.log)
    
    def __iter__(self):
        return iter(self.buffer) if self.buffer else iter(self.log)
    
    def print(self):
        if self.buffer:
            print(self.buffer)
            return
        print(self.log)

    def _filter(self, entry: Entry, attrs):
        return entry.attr in attrs if attrs else True

    def _process_filter(self, attrs=None, exclude=False):
        """
        Processes filter attrs and saves it in the buffer

        - exclude = True for exluding attrs
        """
        if attrs is None:
            _attrs = []
        elif isinstance(attrs, str):
            _attrs = [attrs]
        else:
            _attrs = attrs

        if exclude:
            self.buffer = [item for item in self.log if not self._filter(item, _attrs)]
        else:
            self.buffer = [item for item in self.log if self._filter(item, _attrs)]

        return self

    def filter(self, *attrs):
        """
            obj.filter(['name',]).fetch()

            - Includes given attributes in the result log
            - Stores temporary filtered result in self.buffer
        """
        if not attrs:
            raise InvalidQueryLogOperationException("filter method needs atleast one attribute")
        return self._process_filter(attrs)
    
    def exclude(self, *attrs):
        """
            obj.exclude(['name',]).fetch()

            - Encludes given attributes in the result log
            - Stores temporary filtered result in self.buffer
        """
        if not attrs:
            return InvalidQueryLogOperationException("exclude method needs atleast one attribute")
        return self._process_filter(attrs, True)
    
    def fetch(self) -> list:
        return self.buffer or self.log

    def flush(self) -> None:
        if self.buffer:
            self.log = [item for item in self.log if item not in self.buffer]
        else:
            self.log = []
        self.buffer = []

    def count(self) -> None:
        return self.__len__()

    def push(self, attr, old, new) -> None:
        """
            Pushes a new structured log entry 
        """
        self.log.append(
            Entry(
                attr=attr, 
                old=old, 
                new=new
            )
        )

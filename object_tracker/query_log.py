"""
Copyright (c) Saurabh Pujari
All rights reserved.

This source code is licensed under the BSD-style license found in the LICENSE file in the root directory of this source tree.
"""

from object_tracker.entry import Entry
from object_tracker.exceptions import InvalidQueryLogOperationException


class QueryLog:
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

    def _process_filter(self, attrs, exclude=False):
        """
        Processes filter attrs and saves it in the buffer

        - exclude = True for exluding attrs
        """
        _attrs = None
        if attrs:
            if isinstance(attrs, list):
                _attrs = attrs

            elif isinstance(attrs, str):
                _attrs = [attrs,]

        if exclude:
            self.buffer = list(filter(lambda x: not self._filter(x, _attrs), self.log))
        else:
            self.buffer = list(filter(lambda x: self._filter(x, _attrs), self.log))

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
            for item in self.buffer:
                self.log.remove(item)
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

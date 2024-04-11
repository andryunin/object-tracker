"""
Copyright (c) Saurabh Pujari
All rights reserved.

This source code is licensed under the BSD-style license found in the LICENSE file in the root directory of this source tree.
"""

import copy
import textwrap
from typing import List, Optional, Set
from collections import namedtuple
from datetime import datetime, timezone
from object_tracker.exceptions import InvalidChangeLogOperationException


yellow = lambda x: f"\033[93m{x}\033[0m"
green = lambda x: f"\033[92m{x}\033[0m"
cyan = lambda x: f"\033[96m{x}\033[0m"
gray = lambda x: f"\033[90m{x}\033[0m"
normal = lambda x: f"\033[0m{x}\033[0m"


class Frame(namedtuple('Frame', ['filename', 'lineno', 'function', 'code'])):
    """
    The Frame class is a named tuple that represents a single frame in the stack trace.
    """
    def __new__(cls, frame):
        return super().__new__(
            cls,
            filename=frame.filename,
            lineno=frame.lineno,
            function=frame.function,
            code=frame.code_context[0].strip() if frame.code_context else None
        )
    
    def to_dict(self) -> dict:
        return {
            'filename': self.filename,
            'lineno': self.lineno,
            'function': self.function,
            'code': self.code
        }

    def __str__(self):
        return f"{self.filename}: {self.lineno}, {self.function}\n{self.code}"


class Entry(namedtuple('Entry', ['attr', 'old', 'new', 'timestamp', 'stack'])):
    """
    The Entry class is a named tuple that represents a single log entry in the ChangeLog.
    """
    def __new__(cls, attr, old, new, stack: List[Frame] = None):
        if stack:
            stack = [Frame(frame) for frame in stack]

        return super().__new__(
            cls,
            attr=attr,
            old=old,
            new=new,
            timestamp=datetime.now(timezone.utc),
            stack=stack
        )

    def to_dict(self) -> dict:
        return {
            'attr': self.attr,
            'old': self.old,
            'new': self.new,
            'timestamp': self.timestamp.isoformat(),
            'stack': [frame.to_dict() for frame in self.stack]
        }
    
    def is_a_change(self) -> bool:
        return self.old != self.new


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

    def apply_filters(self, attrs=None, exclude=False, changes_only=False) -> 'ChangeLog':
        """
        applies filters on the log and saves it in the buffer
        """
        if attrs and not isinstance(attrs, (list, tuple, set)):
            raise InvalidChangeLogOperationException(
                "filter/exclude method needs a sequence of attributes as arguments"
            )

        if attrs:
            if exclude:
                self.buffer = [entry for entry in self.log if entry.attr not in attrs]
            else:
                self.buffer = [entry for entry in self.log if entry.attr in attrs]

        if changes_only:
            self.buffer = [entry for entry in self.buffer if entry.is_a_change()]

        return self

    def filter(self, *attrs, changes_only=False) -> 'ChangeLog':
        """
        eg: obj.filter('name', 'age').all()
        """
        if not attrs:
            raise InvalidChangeLogOperationException("filter method needs atleast one attribute")
        return self.apply_filters(attrs, False, changes_only)
    
    def exclude(self, *attrs, changes_only=False) -> 'ChangeLog':
        """
        eg: obj.exclude('name').all()
        """
        if not attrs:
            return InvalidChangeLogOperationException("exclude method needs atleast one attribute")
        return self.apply_filters(attrs, True, changes_only)
    
    def first(self) -> Optional[Entry]:
        logs = self.get_selected_logs()
        return logs[0] if logs else None

    def last(self) -> Optional[Entry]:
        logs = self.get_selected_logs()
        return logs[-1] if logs else None
    
    def all(self) -> List[Entry]:
        return self.get_selected_logs()

    def count(self) -> int:
        return len(self.get_selected_logs())

    def push(self, attr, old, new, stack=None) -> None:
        """
        Pushes a new entry to the log
        """
        self.log.append(
            Entry(
                attr=attr, 
                old=copy.deepcopy(old), 
                new=copy.deepcopy(new),
                stack=stack
            )
        )

    def get_unique_attributes(self) -> Set[str]:
        """
        Returns all attributes in the log
        """
        log = self.get_selected_logs()
        return set([entry.attr for entry in log])
    
    def get_first_log_for_attribute(self, attr, reverse=False):
        """
        Helper function to get a log entry.
        """
        range_func = reversed if reverse else iter
        for i in range_func(range(len(self.log))):
            if self.log[i].attr != attr:
                continue
            if self.log[i].is_a_change():
                return self.log[i]
        return None
    
    def has_changed(self, attr) -> bool:
        """
        Checks if any attribute of the object has been changed by verifying against the log
        """
        first = self.get_first_log_for_attribute(attr)
        last = self.get_first_log_for_attribute(attr, reverse=True)

        if not first and not last:
            return False
        if not first or not last:
            return True
        if first.old != last.new:
            return True
        return False

    def replay(self):
        """
        A Generator to print the logs in a human readable format
        For selected logs, it will show the frame by frame changes of the object
        """
        logs = self.get_selected_logs()
        for log in logs:
            divider = "-" * 50
            is_str = isinstance(log.new, str)
            formatted_val = f"'{green(log.new)}'" if is_str else green(log.new)
            text = f"{divider}\n{yellow(log.attr)} = {formatted_val}\n"

            for i, frame in enumerate(log.stack):
                if i == 0:
                    text += textwrap.indent(
                        f"\n{frame.filename}: {frame.lineno} - {frame.function}\n{cyan(frame.code)}\n", '    '
                    )
                else:
                    text += textwrap.indent(
                        f"\n{gray(f'{frame.filename}: {frame.lineno} - {frame.function}')}\n{gray(frame.code)}\n", '    '
                    )

            yield text

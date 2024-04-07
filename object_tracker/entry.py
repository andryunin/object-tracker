"""
Copyright (c) Saurabh Pujari
All rights reserved.

This source code is licensed under the BSD-style license found in the LICENSE file in the root directory of this source tree.
"""

from datetime import datetime, timezone


class Entry: 
    """
    The Entry class represents a single record in the attribute change log.
    
    Attributes:
        attr (str): The name of the attribute that changed.
        old (any): The old value of the attribute.
        new (any): The new value of the attribute.
        timestamp (datetime): The UTC datetime object of when the change occurred.
    """

    def __init__(self, attr, old, new) -> None:
        self.attr = attr
        self.old = old
        self.new = new 
        self.timestamp = datetime.now(timezone.utc)

    def print(self):
        return print(self.__dict__)
    
    def __str__(self) -> str:
        return f"{self.timestamp} - Attribute '{self.attr}' : '{self.old}' --> '{self.new}'"

    def __repr__(self) -> str:
        return str({'attr': self.attr, 'old': self.old, 'new': self.new, 'timestamp': self.timestamp})

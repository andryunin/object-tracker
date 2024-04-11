"""
Copyright (c) Saurabh Pujari
All rights reserved.

This source code is licensed under the BSD-style license found in the LICENSE file in the root directory of this source tree.
"""
from typing import Callable


ObserverType = Callable[[str, object, object], None]

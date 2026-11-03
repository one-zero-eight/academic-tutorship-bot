"""Fixes error 'no module: src'"""

import pathlib
import sys

root_path = pathlib.Path(__file__).parent.parent

sys.path.append(str(root_path.absolute()))

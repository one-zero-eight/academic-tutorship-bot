import sys

from src.utils.colors import *

USE_COLOR = sys.stdout.isatty()
"Determines if ANSI color codes should be used in terminal"

NAMED_PIPE_PATH = "/tmp/atb-admin-pipe"

DEFAULT_PROMPT = "atb > "
COLORED_PROMPT = f"atb {GREEN}>{RESET} "
PROMPT = COLORED_PROMPT if USE_COLOR else DEFAULT_PROMPT

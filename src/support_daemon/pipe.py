import os
from contextlib import contextmanager

from src.support_daemon.config import NAMED_PIPE_PATH


class Pipe:
    def __init__(self, path: str):
        self.__path = path

    def receive(self) -> str:
        if not os.path.exists(self.__path):
            raise BrokenPipeError(f'"{self.__path}" does not exist')
        with open(NAMED_PIPE_PATH) as file:
            query = file.read().strip()
        return query

    def send(self, data: str):
        with open(NAMED_PIPE_PATH, "w") as file:
            file.write(data)


@contextmanager
def maintain_pipe():
    """
    Creates pipe at `NAMED_PIPE_PATH` to listen connections from there
    """
    if os.path.exists(NAMED_PIPE_PATH):
        print(f'"{NAMED_PIPE_PATH}" already exists, removing...')
        os.remove(NAMED_PIPE_PATH)
    try:
        os.mkfifo(NAMED_PIPE_PATH)
        yield Pipe(NAMED_PIPE_PATH)
    except KeyboardInterrupt:
        pass
    finally:
        os.remove(NAMED_PIPE_PATH)


@contextmanager
def connect_pipe():
    """
    Seeks for pipe at `named_pipe_path` to send connections there
    """
    if not os.path.exists(NAMED_PIPE_PATH):
        raise FileNotFoundError(f'"{NAMED_PIPE_PATH}" missing, support daemon not started?')
    try:
        yield Pipe(NAMED_PIPE_PATH)
    except Exception:
        pass

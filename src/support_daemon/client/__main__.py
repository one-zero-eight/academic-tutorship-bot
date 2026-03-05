from src.support_daemon.config import PROMPT
from src.support_daemon.pipe import connect_pipe


def start():
    try:
        with connect_pipe() as pipe:
            while True:
                query = input(PROMPT)
                pipe.send(query)
                response = pipe.receive()
                print(response)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    start()

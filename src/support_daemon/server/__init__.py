import multiprocessing as mp

from src.support_daemon.pipe import maintain_pipe

from .logic import process_query


def _main_loop():
    with maintain_pipe() as pipe:
        print("Support daemon waiting for tasks")
        while True:
            try:
                query = pipe.receive()
                response = process_query(query)
                pipe.send(response)
                print(response)
            except (EOFError, BrokenPipeError):
                print("Pipe closed, shutting down support daemon...")
                break


class SupportDaemon:
    _process: mp.Process | None = None

    def start(self):
        """Starts support daemon in separate process"""
        self._process = mp.Process(target=_main_loop, daemon=True)
        self._process.start()

    def stop(self):
        """Stops support daemon"""
        if self._process and self._process.is_alive():
            print("\nStopping support daemon...")
            self._process.terminate()
            self._process.join(timeout=2)
            if self._process.is_alive():
                print("Daemon didn't terminate gracefully, force killing...")
                self._process.kill()
                self._process.join()
            self._process = None

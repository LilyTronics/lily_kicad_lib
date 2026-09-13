"""
Base controller for the tools.
"""

import threading
import time
import traceback


class ControllerBase:

    UPDATE_INTERVAL = 1

    def __init__(self, window):
        self.view = window
        self._stop_event = threading.Event()
        self._update_thread = threading.Thread(target=self._update)
        self._update_thread.daemon = True
        self._update_thread.start()

    ###########
    # Private #
    ###########

    def _update(self):
        while not self._stop_event.is_set():
            try:
                self.update()
            except NotImplementedError:
                # Update method not implemented, abort updates
                self._stop_event.set()
            except Exception:
                print(f"Error in update thread in {self.__class__.__name__}:\n"
                      f"{traceback.format_exc().strip()}")
            time.sleep(1)

    ##########
    # Public #
    ##########

    def stop(self):
        if self._update_thread.is_alive():
            self._stop_event.set()
            self._update_thread.join()

    #############
    # Overrride #
    #############

    def update(self):
        raise NotImplementedError("This should be implemented in the derived class")


if __name__ == "__main__":

    class ControllerTest(ControllerBase):

        def update(self):
            print("Update")

    c = ControllerTest(None)
    time.sleep(3)
    c.stop()

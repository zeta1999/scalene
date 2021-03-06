import selectors
import threading
from scalene.scalene_profiler import Scalene
import sys
from typing import Any, List, NamedTuple, Optional, Tuple


@Scalene.shim
def replacement_poll_selector(scalene: Scalene) -> None:
    class ReplacementPollSelector(selectors.PollSelector):
        def select(
            self, timeout: Optional[float] = -1
        ) -> List[Tuple[selectors.SelectorKey, int]]:
            tident = threading.get_ident()
            start_time = scalene.get_wallclock_time()
            if not timeout or timeout < 0:
                interval = sys.getswitchinterval()
            else:
                interval = min(timeout, sys.getswitchinterval())
            while True:
                scalene.set_thread_sleeping(tident)
                selected = super().select(interval)
                scalene.reset_thread_sleeping(tident)
                if selected:
                    return selected
                end_time = scalene.get_wallclock_time()
                if timeout and timeout != -1:
                    if end_time - start_time >= timeout:
                        return []  # None

    selectors.PollSelector = ReplacementPollSelector

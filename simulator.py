"""
simulator.py
------------
Core logic for a simplified Suzuki-Kasami Mutual Exclusion Algorithm simulator.
(Teaching/demo simulation for an MCA mini-project — logic verified independently.)

- Every process keeps a Request Number RN[i] -> how many times it has
  requested the critical section (CS).
- The TOKEN carries:
    * LN[i]  -> last request number of process i that was granted CS
    * queue  -> a FIFO list of processes waiting for the token
- A process can enter CS only if it holds the token.
- When the token holder is done, it checks the queue and passes the
  token to the next waiting process (if any).
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict

NUM_PROCESSES = 4


@dataclass
class SuzukiKasami:
    n: int = NUM_PROCESSES
    RN: List[int] = field(default_factory=lambda: [0] * NUM_PROCESSES)
    token_LN: List[int] = field(default_factory=lambda: [0] * NUM_PROCESSES)
    token_queue: List[int] = field(default_factory=list)
    current_holder: int = 0
    in_cs: bool = False
    logs: List[Dict] = field(default_factory=list)

    total_requests: int = 0
    total_token_transfers: int = 0
    total_cs_entries: int = 0

    def _log(self, event: str, process: int, detail: str = ""):
        self.logs.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "event": event,
            "process": f"P{process}",
            "detail": detail,
        })

    def request_cs(self, i: int):
        self.RN[i] += 1
        self.total_requests += 1
        self._log("REQUEST", i, f"RN[{i}] = {self.RN[i]}")
        self._try_grant()

    def next_step(self):
        if self.in_cs:
            self.exit_cs()
        else:
            self._try_grant()

    def exit_cs(self):
        i = self.current_holder
        if not self.in_cs:
            return
        self.token_LN[i] = self.RN[i]
        self.in_cs = False
        self._log("EXIT CS", i)
        self._try_grant()

    def reset(self):
        self.__init__()

    def _try_grant(self):
        if self.in_cs:
            return
        h = self.current_holder
        if self.RN[h] > self.token_LN[h]:
            self._enter_cs(h)
            return
        for j in range(self.n):
            if j != h and self.RN[j] > self.token_LN[j] and j not in self.token_queue:
                self.token_queue.append(j)
        if self.token_queue:
            nxt = self.token_queue.pop(0)
            self._transfer_token(nxt)

    def _transfer_token(self, j: int):
        prev = self.current_holder
        self.current_holder = j
        self.total_token_transfers += 1
        self._log("TOKEN TRANSFER", j, f"P{prev} -> P{j}")
        self._enter_cs(j)

    def _enter_cs(self, i: int):
        self.in_cs = True
        self.total_cs_entries += 1
        self._log("ENTER CS", i)

    def status_text(self) -> str:
        if self.in_cs:
            return f"P{self.current_holder} is INSIDE the Critical Section"
        return f"Token is idle with P{self.current_holder}"

    def requests_by_process(self) -> Dict[str, int]:
        return {f"P{i}": self.RN[i] for i in range(self.n)}
"""
simulator.py
------------
Suzuki-Kasami Mutual Exclusion Algorithm (textbook-style simulation).

Data kept by the algorithm
- Every process i keeps its OWN array RN_i[j]  -> highest request number of
  process j that i has heard about.  Here:  RN[i][j]  (an N x N matrix).
- The TOKEN carries:
    LN[j]  -> request number of j's most recently GRANTED request
    queue  -> FIFO queue of processes waiting for the token

Rules implemented
1. Requesting the CS
   - If the process already holds the idle token it enters the CS directly
     (no messages needed).
   - Otherwise it does RN[i][i] += 1 and BROADCASTS REQUEST(i, RN[i][i]) to the
     other N-1 processes.  Each receiver updates RN[j][i] = max(RN[j][i], seq).
   - A process that is already waiting (or already inside the CS) does not
     issue another request.
2. The token holder sends the token to i only if it is NOT inside the CS and
   RN[holder][i] == LN[i] + 1   (i.e. i has an outstanding request).
3. Leaving the CS: LN[holder] = RN[holder][holder]; every process k with
   RN[holder][k] == LN[k] + 1 that is not yet queued is appended to the queue;
   if the queue is not empty the token goes to its head.

Message count: a request that needs the token costs (N-1) REQUEST messages
+ 1 TOKEN message = N messages - the key property of Suzuki-Kasami.

(Single-machine teaching simulation: messages are delivered instantly.)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict

NUM_PROCESSES = 4


def _zero_matrix() -> List[List[int]]:
    return [[0] * NUM_PROCESSES for _ in range(NUM_PROCESSES)]


@dataclass
class SuzukiKasami:
    n: int = NUM_PROCESSES
    RN: List[List[int]] = field(default_factory=_zero_matrix)          # RN[i][j]
    token_LN: List[int] = field(default_factory=lambda: [0] * NUM_PROCESSES)
    token_queue: List[int] = field(default_factory=list)
    requesting: List[bool] = field(default_factory=lambda: [False] * NUM_PROCESSES)
    current_holder: int = 0          # P0 starts with the token
    in_cs: bool = False
    logs: List[Dict] = field(default_factory=list)

    total_requests: int = 0
    total_token_transfers: int = 0
    total_cs_entries: int = 0
    total_messages: int = 0

    # ------------------------------------------------------------------
    def _log(self, event: str, process: int, detail: str = ""):
        self.logs.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "event": event,
            "process": f"P{process}",
            "detail": detail,
        })

    # ------------------------------------------------------------------
    # Public actions
    # ------------------------------------------------------------------
    def request_cs(self, i: int):
        """Process Pi wants to enter the critical section."""
        if self.in_cs and self.current_holder == i:
            return                       # already executing the CS
        if self.requesting[i]:
            return                       # already waiting for the token

        self.RN[i][i] += 1
        self.total_requests += 1
        seq = self.RN[i][i]

        # Pi already holds the idle token -> straight into the CS
        if i == self.current_holder and not self.in_cs:
            self._log("REQUEST", i, f"RN[{i}][{i}] = {seq} (holds token, no broadcast)")
            self._enter_cs(i)
            return

        # Otherwise broadcast REQUEST(i, seq) to the other N-1 processes
        self.requesting[i] = True
        for j in range(self.n):
            if j != i:
                self.RN[j][i] = max(self.RN[j][i], seq)
        self.total_messages += self.n - 1
        self._log("REQUEST", i, f"RN[{i}][{i}] = {seq}, broadcast to {self.n - 1} processes")

        # Idle token holder reacts to the request immediately
        self._holder_reacts()

    def next_step(self):
        """NEXT STEP / SEND TOKEN button."""
        if self.in_cs:
            self.exit_cs()
        else:
            self._holder_reacts()

    def exit_cs(self):
        """Token holder leaves the CS and passes the token on if needed."""
        if not self.in_cs:
            return
        h = self.current_holder
        self.token_LN[h] = self.RN[h][h]
        self.in_cs = False
        self.requesting[h] = False
        self._log("EXIT CS", h, f"LN[{h}] = {self.token_LN[h]}")

        for k in range(self.n):
            if k != h and k not in self.token_queue \
                    and self.RN[h][k] == self.token_LN[k] + 1:
                self.token_queue.append(k)

        if self.token_queue:
            self._transfer_token(self.token_queue.pop(0))

    def reset(self):
        self.__init__()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------
    def _holder_reacts(self):
        """Idle holder sends the token to a process with an outstanding request."""
        if self.in_cs:
            return
        h = self.current_holder
        for j in range(self.n):
            if j != h and self.RN[h][j] == self.token_LN[j] + 1:
                if j in self.token_queue:
                    self.token_queue.remove(j)
                self._transfer_token(j)
                return

    def _transfer_token(self, j: int):
        prev = self.current_holder
        self.current_holder = j
        self.total_token_transfers += 1
        self.total_messages += 1
        self._log("TOKEN TRANSFER", j, f"P{prev} -> P{j}")
        self._enter_cs(j)

    def _enter_cs(self, i: int):
        self.in_cs = True
        self.requesting[i] = False
        self.total_cs_entries += 1
        self._log("ENTER CS", i)

    # ------------------------------------------------------------------
    # Convenience for the UI
    # ------------------------------------------------------------------
    def is_waiting(self, i: int) -> bool:
        return self.requesting[i] and i != self.current_holder

    def status_text(self) -> str:
        if self.in_cs:
            return f"P{self.current_holder} is INSIDE the Critical Section"
        return f"Token is idle with P{self.current_holder}"

    def requests_by_process(self) -> Dict[str, int]:
        return {f"P{i}": self.RN[i][i] for i in range(self.n)}

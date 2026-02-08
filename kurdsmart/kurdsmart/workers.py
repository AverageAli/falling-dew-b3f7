from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from PySide6.QtCore import QObject, QThread, Signal


class WorkerSignals(QObject):
    finished = Signal(object)
    failed = Signal(str)


@dataclass
class WorkerTask:
    fn: Callable[..., Any]
    args: tuple[Any, ...]
    kwargs: dict[str, Any]


class Worker(QObject):
    def __init__(self, task: WorkerTask) -> None:
        super().__init__()
        self.task = task
        self.signals = WorkerSignals()

    def run(self) -> None:
        try:
            result = self.task.fn(*self.task.args, **self.task.kwargs)
            self.signals.finished.emit(result)
        except Exception as exc:
            self.signals.failed.emit(str(exc))


def run_in_thread(task: WorkerTask) -> tuple[QThread, Worker]:
    thread = QThread()
    worker = Worker(task)
    worker.moveToThread(thread)
    thread.started.connect(worker.run)
    worker.signals.finished.connect(thread.quit)
    worker.signals.failed.connect(thread.quit)
    thread.finished.connect(thread.deleteLater)
    return thread, worker

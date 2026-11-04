import queue
import threading

class DownloadQueueManager:
    def __init__(self, max_concurrent=2):
        self.max_concurrent = max_concurrent
        self.task_queue = queue.Queue()
        self.running_tasks = []
        self.lock = threading.Lock()

    def add_task(self, task):
        with self.lock:
            self.task_queue.put(task)

    def get_next_task(self):
        with self.lock:
            if len(self.running_tasks) < self.max_concurrent and not self.task_queue.empty():
                task = self.task_queue.get()
                self.running_tasks.append(task)
                return task
        return None

    def task_finished(self, task):
        with self.lock:
            if task in self.running_tasks:
                self.running_tasks.remove(task)

    def get_queue_status(self):
        with self.lock:
            return {
                "waiting": self.task_queue.qsize(),
                "active": len(self.running_tasks),
                "max": self.max_concurrent
            }
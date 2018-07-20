import sitting
import queue
import threading
import request


class Downloader(object):

    def __init__(self):
        self.jobs = queue.PriorityQueue()
        self.results = queue.Queue()

    def fetch(self):
        while True:
            try:
                _, job, handle, args = self.jobs.get()
                response = request.Request(url=job).response.content
                handle(response, args=args)
            finally:
                self.jobs.task_done()

    def create_threads(self):

        for _ in range(sitting.TOTAL_CONCURRENCY):
            thread = threading.Thread(target=self.fetch)
            thread.daemon = True
            thread.start()
        self.jobs.join()

    def add_job(self, job, handle, priority_number=2, args=None):
        """添加任务"""
        self.jobs.put((priority_number, job, handle, args))

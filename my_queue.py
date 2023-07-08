

class Queue:
    """A queue with a maximum number of items. When the queue is full, the oldest item is removed.

    Example:
    >>> q = Queue(4)
    >>> q.enqueue(1)
    >>> q.enqueue(2)
    >>> q.enqueue(2)
    >>> q.enqueue(3)
    >>> q.dequeue()
    1
    >>> print(q)
    Queue([2, 2, 3])
    >>> print(q.most_frequent())
    2
    >>> q.enqueue(None)
    >>> q.enqueue(None)
    >>> q.enqueue(None)
    >>> print(q)
    Queue([3, None, None, None])
    >>> print(q.most_frequent())
    None
    """

    def __init__(self, max_items) -> None:
        self.queue = []
        self.max_items = max_items

    def enqueue(self, item):
        self.queue.append(item)
        if len(self.queue) > self.max_items:
            self.dequeue()

    def dequeue(self):
        return self.queue.pop(0)

    def most_frequent(self):
        """
        Returns the most frequent item in the queue.
        """
        self.counts = {}
        for item in self.queue:
            self.counts[item] = self.counts.get(item, 0) + 1
        if len(self.counts) == 0:
            return None
        return max(self.counts, key=self.counts.get)

    def __repr__(self) -> str:
        return f'Queue({self.queue})'

    def count(self, item):
        return self.queue.count(item)

from rq import Queue
from worker import conn

q = Queue(connection=conn)
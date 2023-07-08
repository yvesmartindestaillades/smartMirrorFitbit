from flask_apscheduler import APScheduler

import apscheduler.schedulers.background



class Scheduler(APScheduler):

    def __init__(self, app=None):
        self.api_enabled = True
        # increase max_instances
        super().__init__(app=app, scheduler=apscheduler.schedulers.background.BackgroundScheduler(max_instances=3))
        self.start()

    def kill(self, listeners=None):
        if listeners != None:
            for l in listeners:
                self.remove_listener(l)
        self.remove_all_jobs()
        self.shutdown(wait=False)


from scheduler import Scheduler
import datetime
from dateutil import tz
import pytz
import time
import os
import sys
import json

class PortolioScheduler:
    def __init__(self, config_file):
        self.scheduler = Scheduler(tzinfo=datetime.timezone.utc)
        with open(os.join(sys.path[0], config_file)) as f:
            self.config_file = json.load(f)
    
    def set_schedule(self, order_schedule, asset, args_data=None):
        sched_type = order_schedule['type']
        time_zone = order_schedule['time_zone']
        try:
            for step_info in order_schedule['steps']:
                do = sched_type
                time_zone_data = pytz.timezone(time_zone)
                step_time = step_info['time']
                asset_fn = getattr(asset, step_info['step'])
                if hasattr(self.scheduler, do) and callable(func := getattr(self.scheduler, do)):
                    if args_data:
                        func(datetime.time(hour=step_time['hour'], minute=step_time['minute'], second=step_time['second'], \
                        tzinfo=time_zone_data), step_info['step'], asset_fn, args=args_data)
                    else:
                        func(datetime.time(hour=step_time['hour'], minute=step_time['minute'], second=step_time['second'], \
                        tzinfo=time_zone_data), step_info['step'], asset_fn, args=args_data)

            self.run_schedule()
        except Exception as e:
            print(f"Got the following issue with scheduler: {e}")

    def update_schedule(self):
        pass

    def delete_schedule(self):
        pass

    def run_schedule(self):
        #Start scheduled jobs
        while True:
            self.scheduler.exec_jobs()
            time.sleep(1)
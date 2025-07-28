from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone
from datetime import datetime, timedelta
import pytz

scheduler = BackgroundScheduler()
scheduler.start()

def add_cron_job(func, hour, min, timezone=timezone('Asia/Singapore')):
    """Add a cron job to the scheduler
    Returns the job id
    """
    job = scheduler.add_job(func, 'cron', hour=hour, minute=min, timezone=timezone)
    return job.id

def add_date_job(func, date, timezone=timezone('Asia/Singapore')):
    """Add a date job to the scheduler
    Returns the job id
    """
    job = scheduler.add_job(func, 'date', run_date=date, timezone=timezone)
    return job.id

def remove_job(job_id):
    """Remove a job from the scheduler"""
    scheduler.remove_job(job_id)
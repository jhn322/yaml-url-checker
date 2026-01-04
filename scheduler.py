import os
import time
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import yaml_url_checker

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("scheduler")

def job():
    logger.info("Starting scheduled URL check...")
    try:
        yaml_url_checker.main()
    except Exception as e:
        logger.error(f"Error during scheduled run: {e}")
    logger.info("Scheduled URL check finished.")

if __name__ == "__main__":
    # Get schedule from environment variable, default to 3 AM every day
    # Format: "minute hour day month day_of_week" (standard cron)
    # But APScheduler uses 5 fields similar to cron, or specific kwargs.
    # To keep it simple and compatible with the user's "0 3 * * *" format,
    # we'll parse a standard cron string or just default to the user's preference.
    
    cron_schedule = os.getenv("CRON_SCHEDULE", "0 3 * * *")
    logger.info(f"Starting scheduler with cron schedule: {cron_schedule}")

    scheduler = BlockingScheduler()
    
    # Parse the standard cron string "m h dom mon dow"
    # Note: This is a basic split; if the user uses complex cron strings, they might need adjustment.
    try:
        parts = cron_schedule.split()
        if len(parts) >= 5:
            minute, hour, day, month, day_of_week = parts[:5]
            trigger = CronTrigger(
                minute=minute,
                hour=hour,
                day=day,
                month=month,
                day_of_week=day_of_week
            )
            scheduler.add_job(job, trigger)
        else:
            logger.error("Invalid CRON_SCHEDULE format. Use 'm h dom mon dow'. Falling back to default 3 AM.")
            scheduler.add_job(job, CronTrigger(hour=3, minute=0))
            
    except Exception as e:
        logger.error(f"Failed to parse cron schedule: {e}. Falling back to default 3 AM.")
        scheduler.add_job(job, CronTrigger(hour=3, minute=0))

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass

import asyncio
import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from config import Config

logger = logging.getLogger(__name__)


class PDFScheduler:
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.scheduler = AsyncIOScheduler()
        self._setup_schedule()

    def _setup_schedule(self):
        """Setup the interval schedule for sending pages"""
        try:
            # Get interval in hours from config
            interval_hours = Config.INTERVAL_HOURS
            
            # Add job to scheduler to run every X hours
            self.scheduler.add_job(
                self._check_and_send_pages_job,
                IntervalTrigger(hours=interval_hours),
                id="interval_pages",
                name=f"Send PDF Pages Every {interval_hours} Hours",
                replace_existing=True,
            )

            logger.info(f"Scheduled pages to send every {interval_hours} hours")

        except Exception as e:
            logger.error(f"Error setting up schedule: {e}")
            # Fallback to default interval (6 hours)
            self.scheduler.add_job(
                self._check_and_send_pages_job,
                IntervalTrigger(hours=6),
                id="interval_pages",
                name="Send PDF Pages Every 6 Hours (Default)",
                replace_existing=True,
            )

    async def _check_and_send_pages_job(self):
        """Job function to check and send pages based on interval"""
        try:
            logger.info("Starting interval pages job")
            await self.bot.check_and_send_pages()
            logger.info("Interval pages job completed")
        except Exception as e:
            logger.error(f"Error in interval pages job: {e}")

    def start(self):
        """Start the scheduler"""
        try:
            self.scheduler.start()
            logger.info("Scheduler started")
        except Exception as e:
            logger.error(f"Error starting scheduler: {e}")

    def stop(self):
        """Stop the scheduler"""
        try:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")

    def get_next_run_time(self):
        """Get the next scheduled run time"""
        try:
            job = self.scheduler.get_job("interval_pages")
            if job:
                return job.next_run_time
            return None
        except Exception as e:
            logger.error(f"Error getting next run time: {e}")
            return None

    def reschedule(self, new_interval_hours: int):
        """Reschedule the interval job to a new interval"""
        try:
            # Remove existing job
            self.scheduler.remove_job("interval_pages")

            # Add new job
            self.scheduler.add_job(
                self._check_and_send_pages_job,
                IntervalTrigger(hours=new_interval_hours),
                id="interval_pages",
                name=f"Send PDF Pages Every {new_interval_hours} Hours",
                replace_existing=True,
            )

            logger.info(f"Rescheduled pages to send every {new_interval_hours} hours")
            return True

        except Exception as e:
            logger.error(f"Error rescheduling: {e}")
            return False

    def is_running(self):
        """Check if scheduler is running"""
        return self.scheduler.running

    def get_jobs(self):
        """Get all scheduled jobs"""
        return self.scheduler.get_jobs()

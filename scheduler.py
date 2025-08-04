import asyncio
import logging
from datetime import datetime, time

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config import Config

logger = logging.getLogger(__name__)


class PDFScheduler:
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.scheduler = AsyncIOScheduler()
        self._setup_schedule()

    def _setup_schedule(self):
        """Setup the daily schedule for sending pages"""
        try:
            # Parse schedule time (format: HH:MM)
            schedule_time = Config.SCHEDULE_TIME
            hour, minute = map(int, schedule_time.split(":"))

            # Add job to scheduler
            self.scheduler.add_job(
                self._send_daily_pages_job,
                CronTrigger(hour=hour, minute=minute),
                id="daily_pages",
                name="Send Daily PDF Pages",
                replace_existing=True,
            )

            logger.info(f"Scheduled daily pages at {schedule_time}")

        except Exception as e:
            logger.error(f"Error setting up schedule: {e}")
            # Fallback to default time (9:00 AM)
            self.scheduler.add_job(
                self._send_daily_pages_job,
                CronTrigger(hour=9, minute=0),
                id="daily_pages",
                name="Send Daily PDF Pages (Default)",
                replace_existing=True,
            )

    async def _send_daily_pages_job(self):
        """Job function to send daily pages"""
        try:
            logger.info("Starting daily pages job")
            await self.bot.send_daily_pages()
            logger.info("Daily pages job completed")
        except Exception as e:
            logger.error(f"Error in daily pages job: {e}")

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
            job = self.scheduler.get_job("daily_pages")
            if job:
                return job.next_run_time
            return None
        except Exception as e:
            logger.error(f"Error getting next run time: {e}")
            return None

    def reschedule(self, new_time: str):
        """Reschedule the daily job to a new time"""
        try:
            hour, minute = map(int, new_time.split(":"))

            # Remove existing job
            self.scheduler.remove_job("daily_pages")

            # Add new job
            self.scheduler.add_job(
                self._send_daily_pages_job,
                CronTrigger(hour=hour, minute=minute),
                id="daily_pages",
                name="Send Daily PDF Pages",
                replace_existing=True,
            )

            logger.info(f"Rescheduled daily pages to {new_time}")
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

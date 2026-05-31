"""Background task manager for async operations."""
import logging
import asyncio
from typing import Callable, Any
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.job import Job

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler: BackgroundScheduler = None

def init_scheduler():
    """Initialize the background task scheduler."""
    global scheduler
    if scheduler is None:
        scheduler = BackgroundScheduler()
        scheduler.start()
        logger.info("Background task scheduler initialized")

def shutdown_scheduler():
    """Shutdown the scheduler."""
    global scheduler
    if scheduler:
        scheduler.shutdown()
        scheduler = None
        logger.info("Background task scheduler shut down")

def schedule_task(func: Callable, *args, **kwargs) -> Job:
    """
    Schedule a function to run once in the background.
    
    Usage:
        async def my_task(data):
            ...
        
        schedule_task(my_task, data)
    """
    if scheduler is None:
        init_scheduler()
    
    logger.info(f"Scheduling task: {func.__name__}")
    
    # If it's an async function, wrap it
    if asyncio.iscoroutinefunction(func):
        def sync_wrapper():
            asyncio.run(func(*args, **kwargs))
        return scheduler.add_job(sync_wrapper, 'date')
    else:
        return scheduler.add_job(func, 'date', args=args, kwargs=kwargs)

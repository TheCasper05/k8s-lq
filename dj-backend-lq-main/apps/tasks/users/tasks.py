import logging

from celery import shared_task

logger = logging.getLogger("lq.tasks")


@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=3,
    name="users.example_task",
)
def example_task(*args, **kwargs):
    """
    Example task template for users module.

    Args:
        *args: Variable positional arguments
        **kwargs: Variable keyword arguments

    Returns:
        dict: Task execution result
    """
    try:
        logger.info(f"Executing users.example_task with args={args}, kwargs={kwargs}")
        # TODO: Implement task logic here
        return {"status": "success", "message": "Task executed successfully"}
    except Exception as e:
        logger.error(f"Error in users.example_task: {str(e)}", exc_info=True)
        raise

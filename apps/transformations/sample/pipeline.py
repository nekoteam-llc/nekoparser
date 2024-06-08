import random
from datetime import timedelta

from prefect import flow, task
from prefect.tasks import task_input_hash

from packages.log import get_logger


@task(
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(days=1),
)
async def square_number(number: int) -> int:
    """
    Calculate the square of a number

    :param number: The number to square
    :return: The square of the number
    """

    logger = get_logger()

    logger.info("Sample task", extra={"number": number})

    return number


@flow
async def sample_pipeline():
    """
    Performs the sum of squares operation
    """

    logger = get_logger()

    input_numbers = [random.randint(1, 100) for _ in range(10)]

    logger.info("Sample pipeline started", extra={"input_numbers": input_numbers})
    results = await square_number.map(input_numbers)  # pyright: ignore[reportCallIssue, reportArgumentType]
    logger.info("Sample pipeline finished", extra={"results": results})

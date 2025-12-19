
from __future__ import annotations

from httpx import (
    URL,
    Proxy,
    Timeout,
    Response,
    BaseTransport,
    AsyncBaseTransport
)
from typing_extensions import (
    Literal,
    override
)


# Sentinel class used until PEP 0661 is accepted
class NotGiven:
    """
    For parameters with a meaningful None value, we need to distinguish between
    the user explicitly passing None, and the user not passing the parameter at
    all.

    User code shouldn't need to use not_given directly.

    For example:

    ```py
    def create(timeout: Timeout | None | NotGiven = not_given): ...


    create(timeout=1)  # 1s timeout
    create(timeout=None)  # No timeout
    create()  # Default timeout behavior
    ```
    """

    def __bool__(self) -> Literal[False]:
        return False

    @override
    def __repr__(self) -> str:
        return "NOT_GIVEN"


not_given = NotGiven()
# for backwards compatibility:
NOT_GIVEN = NotGiven()
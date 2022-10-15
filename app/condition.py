from collections.abc import Callable
from typing import Concatenate, ParamSpec, TypeVar

P = ParamSpec('P')
R = TypeVar('R')


class Condition():

    def __init__(self):
        pass


condition = Condition()


def with_condition(f: Callable[Concatenate[Condition, P], R]) -> Callable[P, R]:
    '''A type-safe decorator which provides a condition.'''

    def inner(*args: P.args, **kwargs: P.kwargs) -> R:
        # Provide the lock as the first argument.
        return f(condition, *args, **kwargs)

    return inner


@with_condition
def sum_threadsafe(c: Condition, numbers: list[float]) -> float:
    print(c)


# We don't need to pass in the lock ourselves thanks to the decorator.
sum_threadsafe([1.1, 2.2, 3.3])


@forcing_condition(label="V_IN")
class DUTInputVoltage():

    def __init__(self):
        pass

    @with_condition
    def set(self, c: Condition):
        pass

    def get(self):
        pass


"""
for example, startup measurement steps:
    - set DUT input voltage
    - configure DUT's registers (depends on: testmode active)
    - activate testmode (depends on: set VIN)
    - raise EN (depends on: configure DUT registers & configure oscilloscope)
    - configure oscilloscope for capture
    - save traces from oscilloscope (depends on: raise EN)
    - save DUT register snapshot (depends on: raise EN)

"""


class Result():
    pass


class BaseTask():

    def __init__(self):
        pass

    def setup(self, initial: Condition) -> Result:
        """
        setup a Task
        :param initial: the Condition to start the sequence with
        :return: Result containing information about success or failure
        """
        pass

    def step(self, c: Condition) -> Result:
        pass

    def finish(self) -> Result:
        pass

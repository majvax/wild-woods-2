# mypy: ignore-errors
# pyright: reportCallIssue=false, reportArgumentType=false, reportReturnType=false, reportUnknownArgumentType=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportGeneralTypeIssues=false
from typing import overload

import esper


@overload
def get_components[C1, C2, C3, C4, C5](
    c1: type[C1],
    c2: type[C2],
    c3: type[C3],
    c4: type[C4],
    c5: type[C5],
    /,
) -> list[tuple[int, tuple[C1, C2, C3, C4, C5]]]: ...
@overload
def get_components[C1, C2, C3, C4, C5, C6](
    c1: type[C1],
    c2: type[C2],
    c3: type[C3],
    c4: type[C4],
    c5: type[C5],
    c6: type[C6],
    /,
) -> list[tuple[int, tuple[C1, C2, C3, C4, C5, C6]]]: ...
@overload
def get_components[C1, C2, C3, C4, C5, C6, C7](
    c1: type[C1],
    c2: type[C2],
    c3: type[C3],
    c4: type[C4],
    c5: type[C5],
    c6: type[C6],
    c7: type[C7],
    /,
) -> list[tuple[int, tuple[C1, C2, C3, C4, C5, C6, C7]]]: ...
@overload
def get_components[C1, C2, C3, C4, C5, C6, C7, C8](
    c1: type[C1],
    c2: type[C2],
    c3: type[C3],
    c4: type[C4],
    c5: type[C5],
    c6: type[C6],
    c7: type[C7],
    c8: type[C8],
    /,
) -> list[tuple[int, tuple[C1, C2, C3, C4, C5, C6, C7, C8]]]: ...


def get_components(*args: type) -> list[tuple[int, tuple[object, ...]]]:
    return esper.get_components(*args)

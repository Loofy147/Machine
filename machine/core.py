from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Mapping, Sequence

OperationFn = Callable[["MachineState", Any], "OperationResult"]


@dataclass(frozen=True)
class MachineState:
    values: Mapping[str, Any] = field(default_factory=dict)

    def with_updates(self, **updates: Any) -> "MachineState":
        next_values = dict(self.values)
        next_values.update(updates)
        return MachineState(next_values)


@dataclass(frozen=True)
class OperationResult:
    value: Any
    updates: Mapping[str, Any] = field(default_factory=dict)
    observation: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Operation:
    name: str
    run: OperationFn


@dataclass(frozen=True)
class TraceEntry:
    state_before: MachineState
    operation: str
    input_value: Any
    result: OperationResult
    state_after: MachineState


@dataclass
class Machine:
    state: MachineState
    operations: dict[str, Operation] = field(default_factory=dict)
    trace: list[TraceEntry] = field(default_factory=list)

    def register(self, operation: Operation) -> None:
        if not operation.name or not operation.name.strip():
            raise ValueError("operation name must be non-empty")
        if operation.name in self.operations:
            raise ValueError(f"operation already registered: {operation.name}")
        self.operations[operation.name] = operation

    def available(self) -> tuple[str, ...]:
        return tuple(self.operations)

    def operate(self, name: str, input_value: Any = None) -> OperationResult:
        try:
            operation = self.operations[name]
        except KeyError as exc:
            raise KeyError(f"unknown operation: {name}") from exc

        state_before = self.state
        result = operation.run(state_before, input_value)
        if not isinstance(result, OperationResult):
            raise TypeError("operation must return OperationResult")

        self.state = state_before.with_updates(**dict(result.updates))
        self.trace.append(
            TraceEntry(
                state_before=state_before,
                operation=name,
                input_value=input_value,
                result=result,
                state_after=self.state,
            )
        )
        return result

    def run_sequence(self, sequence: Sequence[str]) -> list[OperationResult]:
        return [self.operate(name) for name in sequence]


def operation(name: str) -> Callable[[OperationFn], Operation]:
    def decorator(fn: OperationFn) -> Operation:
        return Operation(name=name, run=fn)

    return decorator


def select_first(operations: Iterable[Operation]) -> str:
    candidates = list(operations)
    if not candidates:
        raise ValueError("no operations available")
    return candidates[0].name

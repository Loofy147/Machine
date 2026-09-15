import pytest

from machine.core import Machine, MachineState, Operation, OperationResult, select_first


def increment(state: MachineState, _input: object) -> OperationResult:
    current = int(state.values.get("counter", 0))
    return OperationResult(
        value=current + 1,
        updates={"counter": current + 1},
        observation={"delta": 1},
    )


def reset(state: MachineState, _input: object) -> OperationResult:
    return OperationResult(value=0, updates={"counter": 0}, observation={"reset": True})


def test_operation_changes_state_and_records_trace() -> None:
    machine = Machine(MachineState({"counter": 0}))
    machine.register(Operation("increment", increment))

    result = machine.operate("increment")

    assert result.value == 1
    assert machine.state.values["counter"] == 1
    assert len(machine.trace) == 1
    assert machine.trace[0].state_before.values["counter"] == 0
    assert machine.trace[0].state_after.values["counter"] == 1


def test_machine_can_run_without_a_semantic_goal() -> None:
    machine = Machine(MachineState({"counter": 0}))
    machine.register(Operation("increment", increment))

    machine.run_sequence(["increment", "increment"])

    assert machine.state.values["counter"] == 2


def test_unknown_operation_fails_closed() -> None:
    machine = Machine(MachineState())

    with pytest.raises(KeyError, match="unknown operation"):
        machine.operate("missing")


def test_duplicate_operation_registration_is_rejected() -> None:
    machine = Machine(MachineState())
    machine.register(Operation("reset", reset))

    with pytest.raises(ValueError, match="already registered"):
        machine.register(Operation("reset", reset))


def test_selector_is_not_a_goal_engine() -> None:
    operations = [Operation("increment", increment), Operation("reset", reset)]

    assert select_first(operations) == "increment"

import random
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass

from pydebroglie.core.resolution import Resolution
from pydebroglie.core.topo.topology import ITopology
from pydebroglie.core.trackers.entropy_tracker import EntropyTracker
from pydebroglie.core.trackers.index_picker import IIndexPicker
from pydebroglie.core.trackers.pattern_picker import IPatternPicker
from pydebroglie.core.trackers.tracker import IChoiceObserver, ITracker
from pydebroglie.core.trackers.weighted_random_pattern_picker import (
    WeightedRandomPatternPicker,
)
from pydebroglie.core.wfc.ac4_pattern_model_constraint import Ac4PatternModelConstraint
from pydebroglie.core.wfc.backtrack_policies import IBacktrackPolicy
from pydebroglie.core.wfc.index_pattern_item import IndexPatternItem
from pydebroglie.core.wfc.model_constraint_algorithm import ModelConstraintAlgorithm
from pydebroglie.core.wfc.optimizations import ENABLE_QUICK_SELECT
from pydebroglie.core.wfc.pattern_model import PatternModel
from pydebroglie.core.wfc.pattern_model_constraint import IPatternModelConstraint
from pydebroglie.core.wfc.wave import Wave
from pydebroglie.core.wfc.wave_constraint import IWaveConstraint


@dataclass
class WavePropagatorOptions:
    backtrack_policy: IBacktrackPolicy | None
    max_backtrack_depth: int
    constraints: list[IWaveConstraint] | None
    random_double: Callable[[], float] | None
    index_picker: IIndexPicker | None
    pattern_picker: IPatternPicker | None
    model_constraint_algorithm: ModelConstraintAlgorithm
    clear: bool = True


class WavePropagator:
    # Main data tracking what we've decided so far
    wave: Wave
    pattern_model_constraint: IPatternModelConstraint

    # From model
    pattern_count: int
    frequencies: list[float]

    # Used for backtracking
    backtrack_items: deque[IndexPatternItem]
    backtrack_items_lengths: deque[int]
    prev_choices: deque[IndexPatternItem]
    # Used for max_backtrack_depth
    dropped_backtrack_items_count: int
    # In
    backtrack_count: int  # Purely informational
    backjump_count: int  # Purely informational

    # Basic parameters
    index_count: int
    max_backtrack_depth: int
    constraints: list[IWaveConstraint]
    random_double: Callable[[], float]

    # We evaluate constraints at the last possible minute,
    # instead of eagerly like the model,
    # as they can potentially be expensive.
    deferred_constraints_step: bool

    status: Resolution

    contradiction_reason: str | None
    contradiction_source: object | None

    topology: ITopology
    directions_count: int

    trackers: list[ITracker]
    choice_observers: list[IChoiceObserver]

    index_picker: IIndexPicker
    pattern_picker: IPatternPicker
    backtrack_policy: IBacktrackPolicy | None

    def __init__(
        self, model: PatternModel, topology: ITopology, options: WavePropagatorOptions
    ) -> None:
        # Main data tracking what we've decided so far
        self.wave = Wave(0, 0)
        self.pattern_model_constraint: IPatternModelConstraint

        self.trackers: list[ITracker] = []

        self.pattern_count: int = model.pattern_count
        self.frequencies: list[float] = model.frequencies
        self.index_count: int = topology.index_count
        self.backtrack_policy: IBacktrackPolicy | None = options.backtrack_policy
        self.max_backtrack_depth: int = options.max_backtrack_depth
        self.constraints: list[IWaveConstraint] = options.constraints or []
        self.topology: ITopology = topology
        self.random_double: Callable[[], float] = options.random_double or random.random
        self.directions_count: int = topology.directions_count
        self.index_picker: IIndexPicker = options.index_picker or EntropyTracker()
        self.pattern_picker: IPatternPicker = (
            options.pattern_picker or WeightedRandomPatternPicker()
        )

        match options.model_constraint_algorithm:
            case ModelConstraintAlgorithm.AC4 | ModelConstraintAlgorithm.DEFAULT:
                self.pattern_model_constraint = Ac4PatternModelConstraint(self, model)
            case _:
                raise NotImplementedError("Model constraint algorithm not implemented")

        if options.clear:
            self.clear()

        # @TODO: Finish this constructor

    def internal_ban(self, index: int, pattern: int) -> bool:
        """Requires that index, pattern is possible."""
        # Record information for backtracking
        if self.backtrack_policy is not None:
            self.backtrack_items.append(IndexPatternItem(index, pattern))

        self.pattern_model_constraint.do_ban(index, pattern)

        # Update the wave
        is_contradiction = self.wave.remove_possibility(index, pattern)

        # Update trackers
        for tracker in self.trackers:
            tracker.do_ban(index, pattern)

        return is_contradiction

    def internal_select(self, index: int, chosen_pattern: int) -> bool:
        if ENABLE_QUICK_SELECT:
            for pattern in range(self.pattern_count):
                if pattern == chosen_pattern:
                    continue
                if self.wave.get(index, pattern) and self.internal_ban(index, pattern):
                    return True
            return False

        is_contradiction = False
        self.pattern_model_constraint.do_select(index, chosen_pattern)

        for pattern in range(self.pattern_count):
            if pattern == chosen_pattern:
                continue
            if self.wave.get(index, pattern):
                # This is mostly a repeat of InternalBan, as except for
                # patternModelConstraint, Selects are just seen
                # as a set of bans

                # Record information for backtracking
                if self.backtrack_policy is not None:
                    self.backtrack_items.append(IndexPatternItem(index, pattern))

                # Don't update patternModelConstraint here,
                # it's been done above in DoSelect

                # Update the wave
                is_contradiction |= self.wave.remove_possibility(index, pattern)

                # Update trackers
                for tracker in self.trackers:
                    tracker.do_ban(index, pattern)
        return False

    def get_decided_pattern(self, index: int) -> int:
        decided_pattern = int(Resolution.CONTRADICTION)
        for pattern in range(self.pattern_count):
            if self.wave.get(index, pattern):
                if decided_pattern == int(Resolution.CONTRADICTION):
                    decided_pattern = pattern
                else:
                    return int(Resolution.UNDECIDED)
        return decided_pattern

    def __init_constraints(self) -> None:
        for constraint in self.constraints:
            constraint.init(self)
            if self.status != Resolution.UNDECIDED:
                return
            self.pattern_model_constraint.propagate()
            if self.status != Resolution.UNDECIDED:
                return

    def step_constraints(self) -> None:
        # @TODO: Do we need to worry about evaluating constraints multiple times?
        for constraint in self.constraints:
            constraint.check(self)
            if self.status != Resolution.UNDECIDED:
                return
            self.pattern_model_constraint.propagate()
            if self.status != Resolution.UNDECIDED:
                return
        self.deferred_constraints_step = False

    def clear(self) -> Resolution:
        self.wave = Wave(len(self.frequencies), self.index_count)

        if self.backtrack_policy is not None:
            self.backtrack_items = deque([])
            self.backtrack_items_lengths = deque([])
            self.backtrack_items_lengths.append(0)
            self.prev_choices = deque([])

        self.status = Resolution.UNDECIDED
        self.contradiction_reason = None
        self.contradiction_source = None
        self.trackers = []
        self.choice_observers = []
        self.index_picker.init(self)
        self.pattern_picker.init(self)
        if self.backtrack_policy is not None:
            self.backtrack_policy.init(self)
        self.pattern_model_constraint.clear()

        if self.status == Resolution.CONTRADICTION:
            return self.status

        self.__init_constraints()
        return self.status

    def set_contradiction(
        self, reason: str | None = None, source: object | None = None
    ) -> None:
        """The generation cannot proceed, forcing the algorithm to backtrack or exit."""
        self.status = Resolution.CONTRADICTION
        if reason is not None:
            self.contradiction_reason = reason
        if source is not None:
            self.contradiction_source = source

    def ban(self, x: int, y: int, z: int, pattern: int) -> Resolution:
        """Removes pattern as a possibility from index."""
        index = self.topology.get_index(x, y, z)
        if self.wave.get(index, pattern):
            self.deferred_constraints_step = True
            if self.internal_ban(index, pattern):
                self.status = Resolution.CONTRADICTION
                return self.status
        self.pattern_model_constraint.propagate()
        return self.status

    def step(self) -> Resolution:
        """Make some progress in the WaveFunctionCollapseAlgorithm."""
        if self.deferred_constraints_step:
            self.step_constraints()

        if self.status == Resolution.UNDECIDED:
            index = self.index_picker.get_random_index(self.random_double)
            if index != -1:
                # Pick a tile to select at that index
                pattern = self.pattern_picker.get_random_possible_pattern_at(
                    index, self.random_double
                )
                self.__record_backtrack(index, pattern)
                # Use the pick
                if self.internal_select(index, pattern):
                    self.status = Resolution.CONTRADICTION

            # Reevaluate status
            if self.status == Resolution.UNDECIDED:
                self.pattern_model_constraint.propagate()
            if self.status == Resolution.UNDECIDED:
                self.step_constraints()

            # If we've made all possible choices, and found no contradictions,
            # then we've succeeded.
            if index == -1 and self.status == Resolution.UNDECIDED:
                self.status = Resolution.DECIDED
                return self.status

        self.try_backtrack_until_no_contradiction()

        return self.status

    def add_backtrack_point(self) -> None:
        self.__record_backtrack(-1, -1)

    def __record_backtrack(self, index: int, pattern: int) -> None:
        if self.backtrack_policy is None:
            return

        self.backtrack_items_lengths.append(
            self.dropped_backtrack_items_count + len(self.backtrack_items)
        )
        self.prev_choices.append(IndexPatternItem(index, pattern))
        for co in self.choice_observers:
            co.make_choice(index, pattern)

        # Clean up backtracks if they are too long
        while 0 < self.max_backtrack_depth < len(self.backtrack_items_lengths):
            new_dropped_count = self.backtrack_items_lengths.popleft()
            self.prev_choices.popleft()
            self.backtrack_items = deque(
                list(self.backtrack_items)[
                    new_dropped_count - self.dropped_backtrack_items_count :
                ]
            )
            self.dropped_backtrack_items_count = new_dropped_count

    def try_backtrack_until_no_contradiction(self) -> None:
        if self.backtrack_policy is None:
            return

        while self.status == Resolution.CONTRADICTION:
            backjump_amount = self.backtrack_policy.get_backjump()
            for i in range(backjump_amount):
                if len(self.backtrack_items_lengths) == 1:
                    # We've backtracked as much as we can, but
                    # it's still not possible. That means it is imposible
                    return

                # Actually undo various bits of state
                self.__do_backtrack()
                item = self.prev_choices.pop()
                self.status = Resolution.UNDECIDED
                self.contradiction_reason = None
                self.contradiction_source = None
                for co in self.choice_observers:
                    co.backtrack()
                if backjump_amount == 1:
                    self.backtrack_count += 1

                    # Mark the given choice as impossible
                    if item.index >= 0 and self.internal_select(item.index, item.pattern):
                        self.status = Resolution.CONTRADICTION

            if backjump_amount > 1:
                self.backtrack_count += 1

            # Revalidate status.
            if self.status == Resolution.UNDECIDED:
                self.pattern_model_constraint.propagate()
            if self.status == Resolution.UNDECIDED:
                self.step_constraints()

    def __do_backtrack(self) -> None:
        """Undoes any work that was done since the last backtrack point."""
        target_length = (
            self.backtrack_items_lengths.pop() - self.dropped_backtrack_items_count
        )
        # Undo each item that was added since the backtrack
        while len(self.backtrack_items) > target_length:
            item = self.backtrack_items.pop()

            # Also add the possibility back
            # as it is removed in InternalBan
            self.wave.add_possibility(item.index, item.pattern)

            # Update trackers
            for tracker in self.trackers:
                tracker.undo_ban(item.index, item.pattern)

            # Next, undo the decremenents done in Propagate
            self.pattern_model_constraint.undo_ban(item.index, item.pattern)

    def add_tracker(self, tracker: ITracker) -> None:
        self.trackers.append(tracker)

    def remove_tracker(self, tracker: ITracker) -> None:
        self.trackers.remove(tracker)

    def add_choice_observer(self, co: IChoiceObserver) -> None:
        self.choice_observers.append(co)

    def remove_choice_observer(self, co: IChoiceObserver) -> None:
        self.choice_observers.remove(co)

    def run(self) -> Resolution:
        """Repeatedly step until the status is Decided or Contradiction."""
        while True:
            self.step()
            if self.status != Resolution.UNDECIDED:
                return self.status

    # def to_topo_array(self) -> ITopoArray[int]:
    #     return

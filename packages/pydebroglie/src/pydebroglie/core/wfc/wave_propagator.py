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
    backtrack: bool
    max_backtrack_depth: int
    constraints: list[IWaveConstraint]
    random_double: Callable[[], float] | None

    # We evaluate constraints at the last possible minute,
    # instead of eagerly like the model,
    # as they can potentially be expensive.
    deferred_constraints_step: bool

    status: Resolution

    contradiction_reason: str
    contradiction_source: object

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
        self.backtrack: bool = options.backtrack_policy is not None
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

        # @TODO: Finish this constructor

    def internal_ban(self, index: int, pattern: int) -> bool:
        """Requires that index, pattern is possible."""
        # Record information for backtracking
        if self.backtrack:
            self.backtrack_items.append(IndexPatternItem(index, pattern))

        self.pattern_model_constraint.do_ban(index, pattern)

        # Update the wave
        is_contradiction = self.wave.remove_possibility(index, pattern)

        # Update trackers
        for tracker in self.trackers:
            tracker.do_ban(index, pattern)

        return is_contradiction

    def add_tracker(self, tracker: ITracker) -> None:
        self.trackers.append(tracker)

    def set_contradiction(self) -> None:
        self.status = Resolution.CONTRADICTION

import random
from collections.abc import Callable
from dataclasses import dataclass

from pydebroglie.core.topo.topology import ITopology
from pydebroglie.core.trackers.entropy_tracker import EntropyTracker
from pydebroglie.core.trackers.index_picker import IIndexPicker
from pydebroglie.core.trackers.pattern_picker import IPatternPicker
from pydebroglie.core.trackers.tracker import ITracker
from pydebroglie.core.wfc.backtrack_policies import IBacktrackPolicy
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
    def __init__(
        self, model: PatternModel, topology: ITopology, options: WavePropagatorOptions
    ) -> None:
        # Main data tracking what we've decided so far
        self.wave: Wave | None = None
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
        # self.pattern_picker: IPatternPicker = (
        #     options.pattern_picker or WeightedRandomPatternPicker()
        # )

    def add_tracker(self, tracker: ITracker) -> None:
        self.trackers.append(tracker)

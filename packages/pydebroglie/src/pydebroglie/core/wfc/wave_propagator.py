from collections.abc import Callable
from dataclasses import dataclass

from pydebroglie.core.topo.topology import ITopology
from pydebroglie.core.trackers.index_picker import IIndexPicker
from pydebroglie.core.trackers.pattern_picker import IPatternPicker
from pydebroglie.core.wfc.backtrack_policies import IBacktrackPolicy
from pydebroglie.core.wfc.model_constraint_algorithm import ModelConstraintAlgorithm
from pydebroglie.core.wfc.pattern_model import PatternModel
from pydebroglie.core.wfc.wave_constraint import IWaveConstraint


@dataclass(init=False)
class WavePropagatorOptions:
    backtrack_policy: IBacktrackPolicy
    max_backtrack_depth: int
    constraints: list[IWaveConstraint]
    random_double: Callable[[], float]
    index_picker: IIndexPicker
    pattern_picker: IPatternPicker
    model_constraint_algorithm: ModelConstraintAlgorithm
    clear: bool = True


class WavePropagator:
    def __init__(self, model: PatternModel, topology: ITopology) -> None:
        pass

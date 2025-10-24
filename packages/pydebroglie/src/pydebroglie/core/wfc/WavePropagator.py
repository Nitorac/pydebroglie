from collections.abc import Callable
from dataclasses import dataclass

from pydebroglie.core.trackers.IIndexPicker import IIndexPicker
from pydebroglie.core.trackers.IPatternPicker import IPatternPicker
from pydebroglie.core.wfc.BacktrackPolicies import IBacktrackPolicy
from pydebroglie.core.wfc.IWaveConstraint import IWaveConstraint
from pydebroglie.core.wfc.ModelConstraintAlgorithm import ModelConstraintAlgorithm


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
    pass

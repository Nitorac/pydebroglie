from bitarray import bitarray

from pydebroglie.core.resolution import Resolution
from pydebroglie.core.topo.directions import Direction
from pydebroglie.core.topo.topology import ITopology
from pydebroglie.core.wfc.index_pattern_item import IndexPatternItem
from pydebroglie.core.wfc.pattern_model import PatternModel
from pydebroglie.core.wfc.pattern_model_constraint import IPatternModelConstraint
from pydebroglie.core.wfc.wave_propagator import WavePropagator


class Ac4PatternModelConstraint(IPatternModelConstraint):
    # From model
    propagator_array: list[list[list[int]]]
    pattern_count: int

    # Re-organized propagatorArray
    propagator_array_dense: list[list[bitarray]]

    # Useful values
    propagator: WavePropagator
    directions_count: int
    topology: ITopology
    index_count: int

    # List of locations that still need to be checked against
    # for fulfilling the model's conditions
    to_propagate: list[IndexPatternItem]

    # `compatible` contains the number of patterns present in the wave
    # that can be placed in the cell next to index in direction without being
    # in contradiction with pattern placed in index.
    # If possibilites[index][pattern] is set to false, then
    # compatible[index][pattern][direction] has every direction negative or null
    compatible: list[list[list[int]]]

    def __init__(self, propagator: WavePropagator, model: PatternModel) -> None:
        self.to_propagate = []
        self.propagator = propagator

        self.propagator_array = model.propagator
        self.pattern_count = model.pattern_count

        self.propagator_array_dense = []
        for a1 in model.propagator:
            inner_list = []
            for x in a1:
                dense = bitarray(self.pattern_count)
                dense.setall(False)
                for p in x:
                    dense[p] = True
                inner_list.append(dense)
            self.propagator_array_dense.append(inner_list)

        self.topology = propagator.topology
        self.index_count = self.topology.index_count
        self.directions_count = self.topology.directions_count

    def clear(self) -> None:
        self.to_propagate.clear()
        self.compatible = [
            [[0 for _ in range(self.directions_count)] for _ in range(self.pattern_count)]
            for _ in range(self.index_count)
        ]

        for index in range(self.index_count):
            if not self.topology.contains_index(index):
                continue

            edge_labels = [0 for _ in range(self.directions_count)]
            for d in range(self.pattern_count):
                success, _, _, el = self.topology.try_move(index, Direction(d))
                edge_labels[d] = (int(el) if el is not None else 0) if success else -1

            for pattern in range(self.pattern_count):
                for d in range(self.directions_count):
                    el = edge_labels[d]
                    if el >= 0:
                        compatible_patterns = len(self.propagator_array[pattern][el])
                        self.compatible[index][pattern][d] = compatible_patterns
                        if compatible_patterns == 0 and self.propagator.wave.get(
                            index, pattern
                        ):
                            if self.propagator.internal_ban(index, pattern):
                                self.propagator.set_contradiction()
                            break

    # Precondition that pattern at index is possible.
    def do_ban(self, index: int, pattern: int) -> None:
        # Update compatible (so that we never ban twice)
        for d in range(self.directions_count):
            self.compatible[index][pattern][d] -= self.pattern_count
        # Queue any possible consequences of this changing
        self.to_propagate.append(IndexPatternItem(index, pattern))

    def undo_ban(self, index: int, pattern: int) -> None:
        """Undo what was done in DoBan."""

        # First restore compatible for this cell
        # As it is set a negative value in internal_ban
        for d in range(self.directions_count):
            self.compatible[index][pattern][d] += self.pattern_count

        # As we always Undo in reverse order, if item is in toPropagate, it'll
        # be at the top of the stack.
        # If item is in toPropagate, then we haven't got round to processing yet,
        # so there's nothing to undo.
        if len(self.to_propagate) > 0:
            top = self.to_propagate[-1]
            if top.index == index and top.pattern == pattern:
                self.to_propagate.pop()
                return

        # Not in toPropagate, therefore undo what was done in Propagate
        for d in range(self.directions_count):
            success, i2, idd, el = self.topology.try_move(index, Direction(d))
            if not success:
                continue
            patterns = self.propagator_array[pattern][int(el or 0)]
            for p in patterns:
                self.compatible[i2][p][int(idd) if idd is not None else 0] += 1

    def do_select(self, index: int, pattern: int) -> None:
        """
        Equivalent to calling DoBan on every possible pattern.

        But except the passed in one.
        But it is more efficient.
        Precondition that pattern at index is possible.
        """
        # Update compatible (so that we never ban twice)
        for p in range(self.pattern_count):
            if p == pattern:
                continue
            for d in range(self.directions_count):
                if self.compatible[index][p][d] > 0:
                    self.compatible[index][p][d] -= self.pattern_count

        # Queue any possible consequences of this changing.
        self.to_propagate.append(IndexPatternItem(index, pattern))

    def __propagate_ban_core(self, patterns: list[int], i2: int, d: int) -> None:
        for p in patterns:
            self.compatible[i2][p][d] -= 1
            # Have we just now ruled out this possible pattern?
            if self.compatible[i2][p][d] == 0:
                if self.propagator.internal_ban(i2, p):
                    self.propagator.set_contradiction()

    def __propagate_select_core(
        self, patterns_dense: bitarray, id2: int, idd: int
    ) -> None:
        for p in range(self.pattern_count):
            pattern_contains_p = patterns_dense[p]

            # Sets the value of compatible, triggering internal bans
            prev_compatible = self.compatible[id2][p][idd]
            currently_possible = prev_compatible > 0
            new_compatible = (0 if currently_possible else -self.pattern_count) + (
                1 if pattern_contains_p else 0
            )

            # Have we just now ruled out this possible pattern?
            if new_compatible == 0 and self.propagator.internal_ban(id2, p):
                self.propagator.set_contradiction()

    def propagate(self) -> None:
        while len(self.to_propagate) > 0:
            item = self.to_propagate.pop()
            x, y, z = self.topology.get_coord(item.index)
            if item.pattern >= 0:
                # Process a ban
                for d in range(self.directions_count):
                    success, i2, idd, el = self.topology.try_move(x, y, z, Direction(d))
                    if not success:
                        continue
                    patterns = self.propagator_array[item.pattern][el or 0]
                    self.__propagate_ban_core(
                        patterns, i2, int(idd) if idd is not None else 0
                    )
            else:
                # Process a select
                # Selects work similarly to bans, only instead of decrementing
                # the compatible array we set it to a known value.
                for d in range(self.directions_count):
                    success, i2, idd, el = self.topology.try_move(x, y, z, Direction(d))
                    if not success:
                        continue
                    patterns_dense = self.propagator_array_dense[~item.pattern][el or 0]

                    # @TODO: Special case for when patterns.Length == 1?

                    self.__propagate_select_core(
                        patterns_dense, i2, int(idd) if idd is not None else 0
                    )

            # It's important we fully process the item before returning
            # so that we're in a consistent state for backtracking
            # Hence we don't check this during the loops above

            if self.propagator.status == Resolution.CONTRADICTION:
                return

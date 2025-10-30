from abc import ABC, abstractmethod

from pydebroglie.core.topo.topo_array_1d import TopoArray1D
from pydebroglie.core.topo.topology import ITopology


class ITopoArray[T](ABC):
    """A read-only array coupled with a specific `Topology`."""

    @property
    @abstractmethod
    def topology(self) -> ITopology:
        """Gets the Topology associated with an array."""
        pass

    @abstractmethod
    def get_with_xyz(self, x: int, y: int, z: int = 0) -> T:
        """Gets the value at a particular location."""
        pass

    @abstractmethod
    def get_with_index(self, index: int) -> T:
        """
        Gets the value at a particular location.

        See `Topology` to see how location indices work.
        """
        pass


def create[T](values: list[T], topology: ITopology) -> ITopoArray[T]:
    return TopoArray1D[T](values, topology)

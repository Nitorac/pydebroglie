from pydebroglie.core.topo.topo_array import ITopoArray
from pydebroglie.core.topo.topology import ITopology


class TopoArray1D[T](ITopoArray[T]):
    def __init__(self, values: list[T], topology: ITopology) -> None:
        self.mtopology: ITopology = topology
        self.values: list[T] = values

    @property
    def topology(self) -> ITopology:
        return self.mtopology

    def get_with_xyz(self, x: int, y: int, z: int = 0) -> T:
        return self.values[self.topology.get_index(x, y, z)]

    def get_with_index(self, index: int) -> T:
        return self.values[index]

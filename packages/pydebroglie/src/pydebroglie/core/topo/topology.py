from abc import ABC, abstractmethod
from typing import Self, overload

from bitarray import bitarray

from pydebroglie.core.topo.directions import Direction, EdgeLabel


class ITopology(ABC):
    """
    Specifies a discrete area, volume or graph, and provides generic navigation methods.

    Topologies are used to support generation in a wide variety of shapes.
    Topologies do not actually store data, they just specify the dimensions.
    Actual data is stored in an `ITopoArray`.
    Further information can be found in the documentation.
    """

    @property
    @abstractmethod
    def index_count(self) -> int:
        """Number of unique indices (distinct locations) in the topology."""
        pass

    @property
    @abstractmethod
    def directions_count(self) -> int:
        """Number of unique directions."""
        pass

    @property
    @abstractmethod
    def width(self) -> int:
        """The extent along the x-axis."""
        pass

    @property
    @abstractmethod
    def height(self) -> int:
        """The extent along the y-axis."""
        pass

    @property
    @abstractmethod
    def depth(self) -> int:
        """The extent along the z-axis."""
        pass

    @overload
    @abstractmethod
    def try_move(
        self, index: int, direction: Direction
    ) -> tuple[bool, int, Direction | None, EdgeLabel | None]:
        """
        Given an index and direction, gives the index that is one step in that direction.

        Returns True if it exists and is not masked out. Otherwise, it returns False.
        Additionally, returns information about the edge traversed and inverse_direction.

        :return:
        - succeeded: bool,
        - dest: int,
        - inverse_direction: Direction,
        - edge_label: EdgeLabel,
        """
        pass

    @overload
    @abstractmethod
    def try_move(
        self, x: int, y: int, z: int, direction: Direction
    ) -> tuple[bool, int, Direction | None, EdgeLabel | None]:
        """
        Given co-ordinate and direction, gives index that is one step in that direction.

        Returns True if it exists and is not masked out. Otherwise, it returns False.
        Additionally, returns information about the edge traversed and inverse_direction.

        :return:
        - succeeded: bool,
        - dest: int,
        - inverse_direction: Direction,
        - edge_label: EdgeLabel,
        """
        pass

    @property
    @abstractmethod
    def mask(self) -> bitarray:
        """
        Array with one value per index indicating if the value is missing.

        Not all uses of Topology support masks.
        """
        pass

    @abstractmethod
    def get_index(self, x: int, y: int, z: int) -> int:
        """
        Reduces a three-dimensional co-ordinate to a single integer.

        This is mostly used internally.
        """
        pass

    @abstractmethod
    def get_coord(self, index: int) -> tuple[int, int, int]:
        """
        Inverts ITopology.get_index.

        :return:
        - x: int
        - y: int
        - z: int
        """
        pass

    @abstractmethod
    def with_mask(self, mask: bitarray) -> Self:
        """Returns this topology structure but with a different mask."""
        pass

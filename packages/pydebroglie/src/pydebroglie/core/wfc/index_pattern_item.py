class IndexPatternItem:
    def __init__(self) -> None:
        self.index: int = 0
        self.pattern: int = 0

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, IndexPatternItem)
            and self.index == other.index
            and self.pattern == other.pattern
        )

    def __hash__(self) -> int:
        return self.index.__hash__() * 17 + self.pattern.__hash__()

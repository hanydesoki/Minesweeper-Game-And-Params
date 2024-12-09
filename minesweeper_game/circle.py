
class Circle:

    def __init__(self, center: tuple[int, int], radius: int) -> None:
        self._x, self._y = center
        self._radius: int = radius

    def collidepoint(self, point: tuple[int, int]) -> bool:
        return (point[0] - self.x) ** 2 + (point[1] - self.y) ** 2 <= self.radius ** 2
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(center={self.center}, radius={self.radius})"

    @property
    def x(self) -> int:
        return self._x
    
    @x.setter
    def x(self, new_value: int) -> None:
        self._x = new_value
    
    @property
    def y(self) -> int:
        return self._y
    
    @y.setter
    def y(self, new_value: int) -> None:
        self._y = new_value

    @property
    def radius(self) -> int:
        return self._radius
    
    @radius.setter
    def radius(self, new_value: int) -> None:
        self._radius = new_value

    @property
    def center(self) -> tuple[int, int]:
        return self.x, self.y
    
    @center.setter
    def center(self, new_value: tuple[int, int]) -> None:
        self.x, self.y = new_value
    
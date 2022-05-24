from typing import Tuple


def dot_coords_to_qt_coords(coords: Tuple[float, float], area_height: float):
    """ Converts dot coordinates (origin on the bottom-left corner) to Qt
        coordinates (origin on the top-left corner).
    """
    (x_coord, y_coord) = coords
    return (x_coord, area_height - y_coord)


def quoted(string: str) -> str:
    """ Returns the given string wrapped in escaped double quotes. """
    return f"\"{string}\""

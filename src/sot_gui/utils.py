from typing import Tuple


def dotCoordsToQtCoords(coords: Tuple[float, float], areaHeight: float):
    """ Converts dot coordinates (origin on the bottom-left corner) to Qt
        coordinates (origin on the top-left corner).
    """
    (xCoord, yCoord) = coords
    return (xCoord, areaHeight - yCoord)

import matplotlib.pyplot as plt
from matplotlib import patches, transforms
from typing import List
import numpy as np


class Drawing:
    """ The drawing of any element.

    A Drawing can be a composition of different drawing components (ex.: A lens drawing is two arrows).

    Args:
        *components: The required drawing components (of type `matplotlib.patches.Patch`) that define the Drawing.

            These drawing patches should be instantiated at x = 0 to allow for proper positioning and scaling.

    Examples:
        Create a Drawing from multiple patches

        >>> arrowUp = patches.FancyArrow(x=0, y=0, dx=0, dy=-5, width=0.1)
        >>> arrowDown = patches.FancyArrow(x=0, y=0, dx=0, dy=-5, width=0.1)
        >>> lensDrawing = Drawing(arrowUp, arrowDown)

        Apply the Drawing on a figure at x=10

        >>> fig, axes = plt.subplots()
        >>> lensDrawing.applyTo(axes, x=10)

        Take advantage of the auto-scaling feature by updating the Drawing after the figure's limits have changed
        (on a zoom callback)

        >>> lensDrawing.update()

        Update the Drawing's position

        >>> lensDrawing.update(x=5)

    """

    def __init__(self, *components: patches.Patch):
        self.components: List[patches.Patch] = [*components]  # could be renamed to drawings, parts, patches, artists...

        self.axes = None
        self.x = None
        self.y = None

    def applyTo(self, axes: plt.Axes, x: float = 0, y: float = 0):
        """ Apply the Drawing on a figure at a given position (x, y) with auto-scale.

        Args:
            axes (matplotlib.pyplot.Axes): The figure's Axes on which to apply the drawing.
            x, y (:obj:`float`, optional): The x and y position in data units where to apply the drawing.
                Defaults to (0, 0).

        """

        self.axes = axes
        self.x, self.y = x, y

        self.update()

        for component in self.components:
            self.axes.add_patch(component)

    def update(self, x: float = None, y: float = None):
        """ Update the drawing's position and scaling.

        Args:
            x, y (:obj:`float`, optional): The x and y position where to apply the drawing.
                Defaults to the originally applied position.

        """

        if x is not None:
            self.x = x
        if y is not None:
            self.y = y

        xScaling, yScaling = self.scaling()

        translation = transforms.Affine2D().translate(self.x, self.y)
        scaling = transforms.Affine2D().scale(xScaling, yScaling)

        for component in self.components:
            component.set_transform(scaling + translation + self.axes.transData)

    def scaling(self):
        """ Used internally to compute the required scale transform so that the width of the objects stay the same
        respective to the Axes. """

        xScale, yScale = self.axesToDataScale()

        heightFactor = self.height() / yScale
        xScaling = xScale * (heightFactor / 0.2) ** (3 / 4)

        return xScaling, 1

    def axesToDataScale(self):
        """ Dimensions of the figure in data units. """
        xScale, yScale = self.axes.viewLim.bounds[2:]

        return xScale, yScale

    def height(self):
        """ Initial total height of the drawing (not affected by the transforms).
        Used internally to auto-scale. """

        top, bottom = [], []

        for component in self.components:
            top.append(np.max(component.get_xy(), axis=0)[1])
            bottom.append(np.min(component.get_xy(), axis=0)[1])

        height = np.max(top) - np.min(bottom)

        return height

    def remove(self):
        """ Remove the Drawing from the figure. """
        for component in self.components:
            component.remove()

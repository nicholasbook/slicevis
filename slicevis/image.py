import numpy as np

__all__ = ["Image"]


class Image:
    """Class for four-dimensional images."""

    def __init__(self, data=np.ndarray((1, 1, 1, 1)), metadata=None) -> None:
        """Constructor

        Args:
            data (ndarray, optional): the 4D image. Defaults to np.ndarray((1, 1, 1, 1)).
            metadata (dict, optional): associated metadata dictionary. Defaults to None.

        Raises:
            ValueError: if image data is not 4D
        """
        self.data = data
        if data.ndim != 4:
            raise ValueError("Only 4D images are supported.")
        if metadata == None:
            metadata = {}
        self.metadata = metadata

    def get_timepoint(self, t=0):
        """Returns the 3D image data at timepoint t.

        Args:
            t (int, optional): the timepoint. Defaults to 0.

        Returns:
            ndarray: 3D image data
        """
        return np.asarray(self.data[:, :, :, t])

    def get_class_names(self):
        """Returns the class names for segmentations.

        Returns:
            dict: dictionary of class names and indices
        """
        if "isSegmentation" in self.metadata:
            return self.metadata["Classes"]

    def get_class_colors(self):
        """Returns the class colors for segmentations.

        Returns:
            dict: dictionary of class colors and indices
        """
        if "isSegmentation" in self.metadata:
            return self.metadata["ClassColors"]

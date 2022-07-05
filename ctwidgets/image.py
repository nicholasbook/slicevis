import numpy as np

# Image class represents a CT image data (four-dimensional) and metadata
# It is the output of the load module and the input to the widget module (if time permits, save module)
# image data and metadata should be changeable
# what is the metadata used for?

__all__ = ["Image"]


class Image:
    def __init__(self, data=np.ndarray((1, 1, 1, 1)), metadata=None) -> None:
        self.data = data
        if data.ndim != 4:
            raise ValueError("Only 4D images are supported.")
        if metadata == None:
            metadata = {}
        self.metadata = metadata

    def get_xslice(self, x=0, t=0):
        return np.asarray(self.data[x, :, :, t])

    def get_yslice(self, y=0, t=0):
        return np.asarray(self.data[:, y, :, t])

    def get_zslice(self, z=0, t=0):
        return np.asarray(self.data[:, :, z, t])

    def get_timepoint(self, t=0):
        return np.asarray(self.data[:, :, :, t])

    def get_class_names(self):
        if "isSegmentation" in self.metadata:
            return self.metadata["Classes"]

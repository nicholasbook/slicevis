# stats module provides functions to compute some useful metrics on an Image object
# Min, max, mean, stddev, histograms, ...
# It's essentially a wrapper around numpy but hopefully a nicer interface for the user
import numpy as np


def min(image):
    return np.min(image.get_data())


def max(image):
    return np.max(image.get_data())


def mean(image):
    return np.mean(image.get_data())

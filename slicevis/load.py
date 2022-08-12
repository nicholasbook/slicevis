import nibabel
import pygff
import os
from slicevis.image import Image
import numpy as np
import plotly.colors as pc

__all__ = ["load_image"]


def load_image(filename, is_segmentation=False):
    """Loads a four-dimensional image of variable file type.

    Args:
        filename (str): the filename
        is_segmentation (bool, optional): flag for segmentation files. Defaults to False.

    Returns:
        Image: the 4D image as an instance of the Image class (defined in image.py)
    """
    _, ext = os.path.splitext(filename)
    image = Image()

    # load GFF files using gffio
    if (ext == ".gff") or (ext == ".segff"):
        gff = pygff.load(filename)
        image = Image(gff[:, :, :, :, 0])  # ignore channels
        if ext == ".segff":  # GFF segmentation file
            # get class names and colors from metadata
            classes = gff.info.meta["Project info"]["ClassNames"].split("|")
            class_indices = gff.info.meta["Project info"]["ClassIndices"].split("|")
            class_colors = gff.info.meta["Project info"]["ClassColors"].split("|")
            num_classes = len(classes)
            image.metadata["isSegmentation"] = True
            image.metadata["Classes"] = {}
            image.metadata["ClassColors"] = {}
            for i in range(num_classes):
                image.metadata["Classes"][classes[i]] = int(class_indices[i])
                image.metadata["ClassColors"][classes[i]] = str(class_colors[i])
            tmp = {}
            for i in image.metadata["ClassColors"].keys():  # convert bgra to rgb
                bgra_list = image.metadata["ClassColors"][i].split(" ")
                rgb = ",".join([bgra_list[2], bgra_list[1], bgra_list[0]])
                tmp[i] = "rgb(" + rgb + ")"
            image.metadata["ClassColors"] = tmp
    else:  # use nibabel
        nbl = nibabel.load(filename)
        if nbl.ndim == 3:
            tmp = nbl.get_fdata()
            tmp = tmp[..., np.newaxis]
            image = Image(tmp)
        else:
            image = Image(nbl.get_fdata())

        if is_segmentation:
            image.metadata["isSegmentation"] = True
            image.metadata["Classes"] = {}
            image.metadata["ClassColors"] = {}

            indices = np.unique(image.data)
            for i in indices:
                image.metadata["Classes"][str(int(i))] = int(i)
                image.metadata["ClassColors"][str(int(i))] = "rgb" + str(
                    pc.hex_to_rgb(pc.qualitative.Plotly[int(i)])
                )

    return image

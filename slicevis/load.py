import nibabel
import gffio
import os
from slicevis.image import Image
import numpy as np
import plotly.colors as pc

__all__ = ["load_image"]


def load_image(filename, is_segmentation=False):
    _, ext = os.path.splitext(filename)
    image = Image()

    if (ext == ".gff") or (ext == ".segff"):
        gff = gffio.load(filename)
        image = Image(gff[:, :, :, :, 0])  # ignore channels for now
        if ext == ".segff":  # GFF segmentation file
            classes = gff.info.meta[0][1]["ClassNames"].split("|")  # very unsafe
            class_indices = gff.info.meta[0][1]["ClassIndices"].split("|")
            class_colors = gff.info.meta[0][1]["ClassColors"].split("|")
            num_classes = len(classes)
            image.metadata["isSegmentation"] = True
            image.metadata["Classes"] = {}
            image.metadata["ClassColors"] = {}
            for i in range(num_classes):
                image.metadata["Classes"][classes[i]] = int(class_indices[i])
                image.metadata["ClassColors"][classes[i]] = str(class_colors[i])
            tmp = {}
            for i in image.metadata["ClassColors"].keys():  # convert to rgb(a,b,c)
                tmp[i] = (
                    "rgb("
                    + ",".join(image.metadata["ClassColors"][i].split(" ")[0:3])
                    + ")"
                )
            image.metadata["ClassColors"] = tmp
    else:
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

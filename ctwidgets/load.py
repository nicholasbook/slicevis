import nibabel
import gffio
import os
from ctwidgets.image import Image
import numpy as np

__all__ = ["load_image"]


def load_image(filename):
    _, ext = os.path.splitext(filename)
    image = Image()

    if (ext == ".gff") or (ext == ".segff"):
        gff = gffio.load(filename)
        image = Image(gff[:, :, :, :, 0])  # ignore channels for now
        if ext == ".segff":  # GFF segmentation file
            classes = gff.info.meta[0][1]["ClassNames"].split("|")  # very unsafe
            class_indices = gff.info.meta[0][1]["ClassIndices"].split("|")
            num_classes = len(classes)
            image.metadata["isSegmentation"] = True
            image.metadata["Classes"] = {}
            for i in range(num_classes):
                image.metadata["Classes"][classes[i]] = int(class_indices[i])
    else:
        nbl = nibabel.load(filename)
        if nbl.ndim == 3:
            tmp = nbl.get_fdata()
            tmp = tmp[..., np.newaxis]
            image = Image(tmp)
        else:
            image = Image(nbl.get_fdata())

        # TODO: get metadata as dict (nbl.header.keys())

    return image

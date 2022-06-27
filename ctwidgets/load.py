import nibabel
import gffio
import os
from ctwidgets.image import Image

__all__ = ["load_image"]


def load_image(filename):
    _, ext = os.path.splitext(filename)
    image = Image()

    if (ext == ".gff") or (ext == ".segf"):
        gff = gffio.load(filename)
        image = Image(gff[:, :, :, :, 0])  # ignore channels for now
    else:
        nbl = nibabel.load(filename)
        image = nbl.get_fdata()

    return image

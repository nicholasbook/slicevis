import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from ipywidgets import widgets
import numpy as np

# TODO: convert this to class ImageWidget with methods show_axial, show_coronal, ... save_image, add_overlay, ..?
# function to show static image of a slice (2D) of 4D image
def show_image(
    image2D, title="Slice of 4D image", xlabel="Y", ylabel="X", color="bone"
):
    if image2D.ndim != 2:
        raise ValueError("input image must be 2D")

    fig = plt.figure(figsize=(10.0, 10.0))
    plt.imshow(image2D, cmap=color)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(
        title + " (" + str(xlabel) + "," + str(ylabel) + "-plane)", fontsize=20, pad=20
    )
    plt.colorbar()


class SliceWidget:
    """Class for widgets that offers interactive visualization of slices in 3D image"""

    def __init__(self, image3D):
        if image3D.ndim != 3:
            raise ValueError("input image must be 3D")

        self.image3D = image3D
        self.curr_axis = 2  # z = const plane
        default_slice = int(image3D.shape[self.curr_axis] / 2)  # axial slice
        self.image2D = image3D[:, :, default_slice]  # current slice, always transpose!

        self.b_axial = widgets.Button(description="Show axial")
        self.b_coronal = widgets.Button(description="Show coronal")
        self.b_sagittal = widgets.Button(description="Show sagittal")
        self.b_layout = widgets.HBox([self.b_axial, self.b_coronal, self.b_sagittal])
        # TODO change to toggle buttons and make views (dis-)appear dynamically

        self.title = "Slice of 4D image"
        xlabel = "Y"
        ylabel = "X"
        self.color = "gray"

        self.fig = px.imshow(
            self.image2D,
            title=self.title + " (" + str(xlabel) + "," + str(ylabel) + "-plane)",
            color_continuous_scale=self.color,
            labels={"x": xlabel, "y": ylabel},
            width=600,
            height=600,
        )
        self.fig.update_layout(title_x=0.5, title_font_size=20)

        self.widget = go.FigureWidget(data=self.fig)
        self.app = widgets.VBox([self.b_layout, self.widget])

        self.b_axial.on_click(self.__show_axial)
        self.b_coronal.on_click(self.__show_coronal)
        self.b_sagittal.on_click(self.__show_sagittal)

        display(self.app)

    def __show_axial(self, b):  # don't ask why b is required
        """Shows X,Y-plane in widget"""
        self.curr_axis = 2  # z = const
        default_slice = int(self.image3D.shape[self.curr_axis] / 2)  # default z index
        self.image2D = self.image3D[:, :, default_slice]
        xlabel = "Y"
        ylabel = "X"

        self.widget.data[0]["z"] = self.image2D
        self.widget.layout.title.text = (
            self.title + " (" + str(xlabel) + "," + str(ylabel) + "-plane)"
        )
        self.widget.layout.xaxis.title.text = xlabel
        self.widget.layout.yaxis.title.text = ylabel

    def __show_coronal(self, b):
        """Shows X,Z-plane in widget"""
        self.curr_axis = 1  # y = const
        default_slice = int(self.image3D.shape[self.curr_axis] / 2)  # default y index
        self.image2D = self.image3D[:, default_slice, :]
        self.image2D = np.flipud(self.image2D)
        xlabel = "Z"
        ylabel = "X"

        self.widget.data[0]["z"] = self.image2D
        self.widget.layout.title.text = (
            self.title + " (" + str(xlabel) + "," + str(ylabel) + "-plane)"
        )
        self.widget.layout.xaxis.title.text = xlabel
        self.widget.layout.yaxis.title.text = ylabel

    def __show_sagittal(self, b):
        self.curr_axis = 0  # x = const
        """Shows Y,Z-plane in widget"""
        default_slice = int(self.image3D.shape[self.curr_axis] / 2)  # default x index
        self.image2D = self.image3D[default_slice, :, :]  # not transposed!
        xlabel = "Z"
        ylabel = "Y"

        self.widget.data[0]["z"] = self.image2D
        self.widget.layout.title.text = (
            self.title + " (" + str(xlabel) + "," + str(ylabel) + "-plane)"
        )
        self.widget.layout.xaxis.title.text = xlabel
        self.widget.layout.yaxis.title.text = ylabel

    def set_figure_size(self, width, height):
        self.widget.layout.width = width
        self.widget.layout.height = height

    # def __rotate_view(b):
    #     self.image2D = np.rot90(self.image2D)


# interactive image should have:
# optional histogram, some statistics, toggle between axes (axial, coronal, saggital),
# slider for slice, button for animation, loadable segmentation overlay
# https://plotly.com/python/figurewidget-app/
# flip image?

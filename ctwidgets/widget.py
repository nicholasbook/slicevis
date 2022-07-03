import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from ipywidgets import widgets
import numpy as np
from ctwidgets.throttle import throttle

is_debug = False  # global debug flag

# TODO: convert this to class ImageWidget with methods show_axial, show_coronal, ... save_image, add_overlay, ..?
def show_image(
    image2D, title="Slice of 3D image", xlabel="Y", ylabel="X", color="bone"
):
    """Function to show static image of a slice (2D) of 4D image"""
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

    # TODO: clean up class members, docstring (raises, methods), ...
    # definitely needs some debug output

    def __init__(self, image3D, debug=False):
        if image3D.ndim != 3:
            raise ValueError("input image must be 3D")
        global is_debug
        is_debug = debug

        self.image3D = image3D
        self.curr_axis = 2  # z = const plane
        default_slice = int(image3D.shape[self.curr_axis] / 2)  # axial slice
        self.image2D = image3D[:, :, default_slice]  # current slice

        # buttons in horizontal layout
        self.b_axial = widgets.Button(description="Show axial")
        self.b_coronal = widgets.Button(description="Show coronal")
        self.b_sagittal = widgets.Button(description="Show sagittal")
        self.b_layout = widgets.HBox(
            [self.b_axial, self.b_coronal, self.b_sagittal],
        )

        # utility buttons in second row
        self.b_rot = widgets.Button(description="Rotate counterclockwise")
        self.b_flip_ud = widgets.Button(description="Flip upside down")
        self.b_flip_lr = widgets.Button(description="Flip left to right")
        self.util_layout = widgets.HBox([self.b_rot, self.b_flip_ud, self.b_flip_lr])

        # stack buttons
        self.b_layout_combined = widgets.VBox([self.b_layout, self.util_layout])

        # vertical slider
        max = self.image3D.shape[self.curr_axis] - 1
        self.slider = widgets.IntSlider(
            description="Z",
            value=default_slice,
            min=0,
            max=max,
            step=1,
            orientation="vertical",
        )
        self.min_label = widgets.Label(value="Min = 0")
        self.max_label = widgets.Label(value="Max = " + str(max))
        self.slider_layout = widgets.VBox([self.max_label, self.slider, self.min_label])

        # figure setup
        self.title = "Slice of 4D image"
        self.color = "gray"
        xlabel = "Y"
        ylabel = "X"

        self.fig = px.imshow(
            self.image2D,
            title=self.title + " (" + str(xlabel) + "," + str(ylabel) + "-plane)",
            color_continuous_scale=self.color,
            labels={"x": xlabel, "y": ylabel},
            width=800,
            height=600,
        )
        self.fig.update_layout(title_x=0.5, title_font_size=20)
        self.widget = go.FigureWidget(data=self.fig)  # dynamic figure widget

        # optional debug output
        self.out = widgets.Output()
        self.b_clear = widgets.Button(description="Clear")

        # app layout

        self.slice_layout = widgets.HBox([self.slider_layout, self.widget])
        self.slice_layout.layout.align_items = "center"
        if is_debug:
            self.app = widgets.VBox(
                [
                    self.b_layout_combined,
                    self.slice_layout,
                    widgets.HBox([self.out, self.b_clear]),
                ]
            )
        else:
            self.app = widgets.VBox([self.b_layout_combined, self.slice_layout])
        self.app.layout.justify_content = "flex-start"  # main axis = vertical
        self.app.layout.align_items = "center"  # cross axis = horizontal

        # connect buttons to callbacks
        self.b_axial.on_click(self.__show_axial)
        self.b_axial.on_click(self.__axis_changed)
        self.b_coronal.on_click(self.__show_coronal)
        self.b_coronal.on_click(self.__axis_changed)
        self.b_sagittal.on_click(self.__show_sagittal)
        self.b_sagittal.on_click(self.__axis_changed)
        self.b_rot.on_click(self.__rotate_view)
        self.b_flip_ud.on_click(self.__flip_up)
        self.b_flip_lr.on_click(self.__flip_lr)

        self.slider.observe(self.__slice_changed, names="value")
        if is_debug:
            self.b_clear.on_click(self.__clear_output)

        display(self.app)  # show app

    def __show_axial(self, b):  # don't ask why b is required
        """Shows X,Y-plane in widget"""

        self.curr_axis = 2  # z = const
        default_slice = int(self.image3D.shape[self.curr_axis] / 2)  # default z index
        self.image2D = self.image3D[:, :, default_slice]
        self.widget.data[0]["z"] = self.image2D
        self.slider.value = default_slice

        xlabel = "Y"
        ylabel = "X"

        self.widget.layout.title.text = (
            self.title + " (" + str(xlabel) + "," + str(ylabel) + "-plane)"
        )
        self.widget.layout.xaxis.title.text = xlabel
        self.widget.layout.yaxis.title.text = ylabel

        global is_debug
        if is_debug:
            with self.out:
                print("Show axial.")

    def __show_coronal(self, b):
        """Shows X,Z-plane in widget"""

        self.curr_axis = 1  # y = const
        default_slice = int(self.image3D.shape[self.curr_axis] / 2)  # default y index
        self.image2D = self.image3D[:, default_slice, :]
        self.widget.data[0]["z"] = self.image2D
        self.slider.value = default_slice

        xlabel = "Z"
        ylabel = "X"

        self.widget.layout.title.text = (
            self.title + " (" + str(xlabel) + "," + str(ylabel) + "-plane)"
        )
        self.widget.layout.xaxis.title.text = xlabel
        self.widget.layout.yaxis.title.text = ylabel

        global is_debug
        if is_debug:
            with self.out:
                print("Show coronal.")

    def __show_sagittal(self, b):
        self.curr_axis = 0  # x = const
        """Shows Y,Z-plane in widget"""
        default_slice = int(self.image3D.shape[self.curr_axis] / 2)  # default x index
        self.image2D = self.image3D[default_slice, :, :]  # not transposed!
        self.widget.data[0]["z"] = self.image2D
        self.slider.value = default_slice

        xlabel = "Z"
        ylabel = "Y"

        self.widget.layout.title.text = (
            self.title + " (" + str(xlabel) + "," + str(ylabel) + "-plane)"
        )
        self.widget.layout.xaxis.title.text = xlabel
        self.widget.layout.yaxis.title.text = ylabel

        global is_debug
        if is_debug:
            with self.out:
                self.out.append_stdout("Show sagittal.")

    def __axis_changed(self, change):
        """Update slider range based on current axis"""
        max = self.image3D.shape[self.curr_axis] - 1
        self.slider.max = max
        self.max_label.value = "Max = " + str(max)

        global is_debug
        if is_debug:
            with self.out:
                print("Axis changed.")

    def __rotate_view(self, b):
        self.image2D = np.rot90(self.image2D)
        self.widget.data[0]["z"] = self.image2D
        # TODO: store transformation matrix. currently, all 2D manipulations are lost on axis/slice change

    def __flip_up(self, b):
        self.image2D = np.flipud(self.image2D)
        self.widget.data[0]["z"] = self.image2D

    def __flip_lr(self, b):
        self.image2D = np.fliplr(self.image2D)
        self.widget.data[0]["z"] = self.image2D

    @throttle(0.1, is_debug)
    def __slice_changed(self, change):
        """Update self.image2D if slider changed (throttled)"""
        # careful, this callback is also triggered by slider.value = ... !
        # therefore, make sure that change.new does not exceed dimension limits

        if self.curr_axis == 0:
            # index = max(change.new, self.image3D.shape[0] - 1)
            index = change.new
            self.image2D = self.image3D[index, :, :]
            self.widget.data[0]["z"] = self.image2D
        elif self.curr_axis == 1:
            index = change.new  # max(change.new, self.image3D.shape[1] - 1)
            self.image2D = self.image3D[:, index, :]
            self.widget.data[0]["z"] = self.image2D
        else:
            index = change.new  # max(change.new, self.image3D.shape[2] - 1)
            self.image2D = self.image3D[:, :, index]
            self.widget.data[0]["z"] = self.image2D

        global is_debug
        if is_debug:
            with self.out:
                print("Slice changed (change.new = " + str(change.new) + ").")

    def __clear_output(self, b):
        self.out.clear_output()

    # --- public methods ---

    def set_figure_size(self, width, height):
        """Set width and height of image widget (includes colorbar)"""
        self.widget.layout.width = width
        self.widget.layout.height = height


# interactive image should have:
# optional histogram, some statistics, toggle between axes (axial, coronal, saggital),
# slider for slice, button for animation, loadable segmentation overlay
# https://plotly.com/python/figurewidget-app/
# flip image?

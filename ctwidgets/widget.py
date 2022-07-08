import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from ipywidgets import widgets
import numpy as np
from ctwidgets.utilities import throttle

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

    def __init__(self, image3D, colored=False, debug=False):
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
        self.b_rot = widgets.Button(description="Rotate 90°")
        self.b_flip_ud = widgets.Button(description="Flip upside down")
        self.b_flip_lr = widgets.Button(description="Flip left to right")
        self.util_layout = widgets.HBox([self.b_rot, self.b_flip_ud, self.b_flip_lr])

        # stack buttons
        self.b_layout_combined = widgets.VBox([self.b_layout, self.util_layout])

        # vertical slider (+ buttons and labels)
        max = self.image3D.shape[self.curr_axis] - 1
        self.slider = widgets.IntSlider(
            description="Z",
            value=default_slice,
            min=0,
            max=max,
            step=1,
            orientation="vertical",
        )
        self.b_up = widgets.Button(
            description="↑", layout=widgets.Layout(width="50px", font_weight="bold")
        )
        self.b_down = widgets.Button(
            description="↓", layout=widgets.Layout(width="50px", font_weight="bold")
        )
        self.min_label = widgets.Label(value="Min = 0")
        self.max_label = widgets.Label(value="Max = " + str(max))
        self.slider_layout = widgets.VBox(
            [self.max_label, self.b_up, self.slider, self.b_down, self.min_label],
            layout=widgets.Layout(align_items="center"),
        )

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
        self.b_up.on_click(self.__up_pressed)
        self.b_down.on_click(self.__down_pressed)

        if is_debug:
            self.b_clear.on_click(self.__clear_output)

        if colored:
            self.set_colormap()

        display(self.app)  # show app

    def __show_axial(self, b):  # don't ask why b is required
        """Shows X,Y-plane in widget"""

        self.curr_axis = 2  # z = const
        default_slice = int(self.image3D.shape[self.curr_axis] / 2)  # default z index
        self.__update2D(default_slice)
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
        self.__update2D(default_slice)
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
        self.__update2D(default_slice)
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
        """Update slider range and labels based on current axis"""
        max = self.image3D.shape[self.curr_axis] - 1
        self.slider.max = max
        self.max_label.value = "Max = " + str(max)

        if self.curr_axis == 0:
            self.slider.description = "X"
        elif self.curr_axis == 1:
            self.slider.description = "Y"
        else:
            self.slider.description = "Z"

        global is_debug
        if is_debug:
            with self.out:
                print("Axis changed.")

    def __rotate_view(self, b):
        rot_axes = []
        if self.curr_axis == 0:
            rot_axes = [1, 2]
        elif self.curr_axis == 1:
            rot_axes = [0, 2]
        else:
            rot_axes = [0, 1]
        self.image3D = np.rot90(self.image3D, axes=rot_axes)  # rotated "view"

        self.__update2D(self.slider.value)  # index unchanged

    def __flip_up(self, b):
        self.image3D = np.flipud(self.image3D)
        self.__update2D(self.slider.value)

    def __flip_lr(self, b):
        self.image3D = np.fliplr(self.image3D)
        self.__update2D(self.slider.value)

    @throttle(0.1, is_debug)
    def __slice_changed(self, change):
        """Update self.image2D if slider changed (throttled)"""
        # careful, this callback is also triggered by slider.value = ... !
        # therefore, make sure that change.new does not exceed dimension limits
        self.__update2D(change.new)

        global is_debug
        if is_debug:
            with self.out:
                print("Slice changed (change.new = " + str(change.new) + ").")

    def __clear_output(self, b):
        self.out.clear_output()

    def __update2D(self, index):
        if self.curr_axis == 0:
            # index = max(change.new, self.image3D.shape[0] - 1)
            self.image2D = self.image3D[index, :, :]
            self.widget.data[0]["z"] = self.image2D
        elif self.curr_axis == 1:
            # max(change.new, self.image3D.shape[1] - 1)
            self.image2D = self.image3D[:, index, :]
            self.widget.data[0]["z"] = self.image2D
        else:
            # max(change.new, self.image3D.shape[2] - 1)
            self.image2D = self.image3D[:, :, index]
            self.widget.data[0]["z"] = self.image2D

    def __up_pressed(self, b):
        new_value = self.slider.value + 1
        self.slider.value = new_value
        self.__update2D(new_value)

    def __down_pressed(self, b):
        new_value = self.slider.value - 1
        self.slider.value = new_value
        self.__update2D(new_value)

    # --- public methods ---

    def set_figure_size(self, width, height):
        """Set width and height of image widget (includes colorbar)"""
        self.widget.layout.width = width
        self.widget.layout.height = height

    def set_colormap(self, cmap="Inferno"):
        """Changes the figure's colormap"""
        self.widget.update_coloraxes(
            cmin=np.min(self.image3D), cmax=np.max(self.image3D), colorscale=cmap
        )

    def add_class_names(self, names, indices):
        """Sets indices as the colorbar ticks and names as the tick labels."""
        self.widget.update_coloraxes(
            colorbar_tickmode="array",
            colorbar_tickvals=indices,
            colorbar_ticktext=names,
        )


# interactive image should have:
# optional histogram, some statistics, toggle between axes (axial, coronal, saggital),
# slider for slice, button for animation, loadable segmentation overlay
# https://plotly.com/python/figurewidget-app/
# flip image?


# class SegmentationWidget(SliceWidget):
#     def __init__(self, image3D, segmentation, colored=False, debug=False):
#         super().__init__(image3D, colored, debug)

#         self.segmentation = segmentation
#         self.widget.

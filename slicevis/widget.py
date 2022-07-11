import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from ipywidgets import widgets
import numpy as np
from slicevis.image import Image
from slicevis.utilities import throttle
from slicevis.load import load_image

is_debug = False  # global debug flag


class SliceWidget:
    """Class for widgets that offers interactive visualization of slices in 3D image"""

    # TODO: clean up class members, docstring (raises, methods), ...

    def __init__(self, image3D, colored=False, debug=False):
        if image3D.ndim != 3:
            raise ValueError("input image must be 3D")
        global is_debug
        is_debug = debug

        self.image3D = image3D

        self.seg3D = None
        self.seg2D = None
        self.seg3D_validation = None
        self.seg2D_validation = None
        self.class_names = {}
        self.class_names_validation = {}
        self.class_colors = {}

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
        self.b_layout_vertical = widgets.VBox(
            [self.b_layout, self.util_layout],
            layout=widgets.Layout(width="80%", align_items="center"),
        )

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
        self.color = "gray"
        xlabel = "Y"
        ylabel = "X"

        self.fig = px.imshow(
            self.image2D,
            color_continuous_scale=self.color,
            labels={"x": xlabel, "y": ylabel, "color": "Value"},
            width=800,
            height=600,
        )  # TODO: change hoverlabel dynamically
        self.widget = go.FigureWidget(data=self.fig)  # dynamic figure widget
        self.widget_box = widgets.Box([self.widget])

        # load segmentation
        self.b_load_seg = widgets.Button(description="Load")
        self.b_clear_seg = widgets.Button(description="Clear")
        self.segmentation_path = widgets.Text(
            placeholder="Segmentation file",
            layout=widgets.Layout(width="90%"),
        )
        self.load_seg_box = widgets.VBox(
            [
                self.segmentation_path,
                widgets.HBox(
                    [self.b_load_seg, self.b_clear_seg],
                    layout=widgets.Layout(width="95%"),
                ),
            ],
            layout=widgets.Layout(width="20%", align_items="center"),
        )

        # load validation segmentation
        self.b_load_valid = widgets.Button(description="Load")
        self.b_clear_valid = widgets.Button(description="Clear")
        self.validation_path = widgets.Text(
            placeholder="Validation file",
            layout=widgets.Layout(width="90%"),
        )
        self.load_valid_box = widgets.VBox(
            [
                self.validation_path,
                widgets.HBox(
                    [self.b_load_valid, self.b_clear_valid],
                    layout=widgets.Layout(width="95%"),
                ),
            ],
            layout=widgets.Layout(width="20%", align_items="center"),
        )

        self.b_layout_horizontal = widgets.HBox(
            [
                self.load_seg_box,
                self.load_valid_box,
                self.b_layout_vertical,
            ],
            layout=widgets.Layout(
                justify_content="space-around", align_items="center", width="85%"
            ),
        )

        # optional debug output
        self.out = widgets.Output()
        self.b_clear = widgets.Button(description="Clear")

        # app layout
        self.slice_layout = widgets.HBox(
            [self.slider_layout, self.widget_box],
            layout=widgets.Layout(align_items="center"),
        )

        if is_debug:
            self.app = widgets.VBox(
                [
                    self.b_layout_horizontal,
                    self.slice_layout,
                    widgets.VBox([self.b_clear, self.out]),
                ]
            )
        else:
            self.app = widgets.VBox([self.b_layout_horizontal, self.slice_layout])
        self.app.layout.justify_content = (
            "flex-start"  # main axis = vertical (no effect)
        )
        self.app.layout.align_items = "center"  # cross axis = horizontal
        self.app.layout.border = "2px solid gray"

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

        self.b_load_seg.on_click(self.__load_segmentation)
        self.b_clear_seg.on_click(self.__clear_segmentation)
        self.b_load_valid.on_click(self.__load_validation_segmentation)
        self.b_clear_valid.on_click(self.__clear_validation)

        self.slider.observe(self.__slice_changed, names="value")
        self.b_up.on_click(self.__up_pressed)
        self.b_down.on_click(self.__down_pressed)

        if is_debug:
            self.b_clear.on_click(self.__clear_output)
            self.b_layout_vertical.layout.border = "1px solid black"
            self.b_layout_horizontal.layout.border = "1px solid black"
            self.slice_layout.layout.border = "1px solid black"
            self.slider_layout.layout.border = "1px solid black"
            self.widget_box.layout.border = "1px solid black"
            self.load_seg_box.layout.border = "1px solid black"

        if colored:
            self.set_colormap()

        display(self.app)  # show app

    def __show_axial(self, b):  # don't ask why b is required
        """Shows X,Y-plane in widget"""

        self.curr_axis = 2  # z = const
        default_slice = int(self.image3D.shape[self.curr_axis] / 2)  # default z index

        self.slider.value = default_slice

        xlabel = "Y"
        ylabel = "X"

        self.widget.update_layout(
            xaxis=dict(title_text=xlabel, range=[0, self.image3D.shape[1]]),
            yaxis=dict(title_text=ylabel, range=[self.image3D.shape[0], 0]),
        )

        self.__debug("Show axial.")

    def __show_coronal(self, b):
        """Shows X,Z-plane in widget"""

        self.curr_axis = 1  # y = const
        default_slice = int(self.image3D.shape[self.curr_axis] / 2)  # default y index

        self.slider.value = default_slice  # calls __update2D (but only after __show_coronal has returned!)

        xlabel = "Z"
        ylabel = "X"

        self.widget.update_layout(
            xaxis=dict(title_text=xlabel, range=[0, self.image3D.shape[2]]),
            yaxis=dict(title_text=ylabel, range=[self.image3D.shape[0], 0]),
        )

        self.__debug("Show coronal.")

    def __show_sagittal(self, b):
        self.curr_axis = 0  # x = const
        """Shows Y,Z-plane in widget"""
        default_slice = int(self.image3D.shape[self.curr_axis] / 2)  # default x index
        self.slider.value = default_slice

        xlabel = "Z"
        ylabel = "Y"

        self.widget.update_layout(
            xaxis=dict(title_text=xlabel, range=[0, self.image3D.shape[2]]),
            yaxis=dict(title_text=ylabel, range=[self.image3D.shape[1], 0]),
        )

        self.__debug("Show sagittal.")

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

        self.__debug("Axis changed.")

    def __rotate_view(self, b):
        rot_axes = self.__get_rot_axes()
        self.image3D = np.rot90(self.image3D, axes=rot_axes)  # rotated "view"
        if self.seg3D is not None:
            self.seg3D = np.rot90(self.seg3D, axes=rot_axes)
        self.__update2D(None)  # index unchanged

    def __flip_up(self, b):
        flip_axis = self.__get_rot_axes()[0]
        self.image3D = np.flip(self.image3D, axis=flip_axis)
        if self.seg3D is not None:
            self.seg3D = np.flip(self.seg3D, axis=flip_axis)
        self.__update2D(None)

    def __flip_lr(self, b):
        flip_axis = self.__get_rot_axes()[1]
        self.image3D = np.flip(self.image3D, axis=flip_axis)
        if self.seg3D is not None:
            self.seg3D = np.flip(self.seg3D, axis=flip_axis)
        self.__update2D(None)

    @throttle(0.05)
    def __slice_changed(self, change):
        """Update self.image2D if slider changed (throttled)"""
        # careful, this callback is also triggered by slider.value = ... !
        # therefore, make sure that change.new does not exceed dimension limits

        self.__update2D(change.new)

    def __clear_output(self, b):
        self.out.clear_output()

    def __update2D(self, index):
        if index is None:
            index = self.slider.value

        if self.curr_axis == 0:
            # index = max(change.new, self.image3D.shape[0] - 1)
            self.image2D = self.image3D[index, :, :]
            if self.seg3D is not None:
                self.seg2D = self.seg3D[index, :, :]
            if self.seg3D_validation is not None:
                self.seg2D_validation = self.seg3D_validation[index, :, :]
        elif self.curr_axis == 1:
            # max(change.new, self.image3D.shape[1] - 1)
            self.image2D = self.image3D[:, index, :]
            if self.seg3D is not None:
                self.seg2D = self.seg3D[:, index, :]
            if self.seg3D_validation is not None:
                self.seg2D_validation = self.seg3D_validation[:, index, :]
        else:
            # max(change.new, self.image3D.shape[2] - 1)
            self.image2D = self.image3D[:, :, index]
            if self.seg3D is not None:
                self.seg2D = self.seg3D[:, :, index]
            if self.seg3D_validation is not None:
                self.seg2D_validation = self.seg3D_validation[:, :, index]

        # generate segmentations (optional)
        trace_list = []

        # validation segmentation "underlay"
        if self.seg3D_validation is not None:
            for c in self.class_names_validation.values():
                if c == 0:  # unclassified
                    continue
                c_indices = np.nonzero(self.seg2D_validation == c)  # tuple of arrays
                class_name = list(self.class_names.keys())[
                    list(self.class_names.values()).index(c)
                ]
                color = self.class_colors[class_name]
                if len(self.class_names_validation) == 2:  # white if only one class
                    color = "rgb(255,255,255)"
                    class_name = list(self.class_names_validation.keys())[
                        list(self.class_names_validation.values()).index(c)
                    ]
                trace_list.append(
                    go.Scatter(
                        y=c_indices[0],
                        x=c_indices[1],
                        opacity=0.3,
                        mode="markers",
                        marker_color=color,
                        marker_symbol="square",
                        showlegend=True,
                        name=class_name,
                    )
                )

        # segmentation "overlay"
        if self.seg3D is not None:
            for c in self.class_names.values():
                if c == 0:  # unclassified
                    continue
                c_indices = np.nonzero(self.seg2D == c)  # tuple of arrays
                class_name = list(self.class_names.keys())[
                    list(self.class_names.values()).index(c)
                ]
                trace_list.append(
                    go.Scatter(
                        y=c_indices[0],
                        x=c_indices[1],
                        opacity=0.5,
                        mode="markers",
                        marker_symbol="square",
                        marker_color=self.class_colors[class_name],
                        showlegend=True,
                        name=class_name,
                    )
                )

        # batch update
        with self.widget.batch_update():
            self.widget.data[0]["z"] = self.image2D
            self.widget.data = [self.widget.data[0]]  # clear segmentations
            self.widget.add_traces(trace_list)
            self.widget.update_layout(
                legend=dict(x=0, y=1, orientation="h", yanchor="bottom", xanchor="left")
            )
        self.__debug("update.")

    def __up_pressed(self, b):
        new_value = self.slider.value + 1
        self.slider.value = new_value

    def __down_pressed(self, b):
        new_value = self.slider.value - 1
        self.slider.value = new_value

    def __load_segmentation(self, b, is_validation=False):

        file = None
        if is_validation:
            file = self.validation_path.value
        else:
            file = self.segmentation_path.value

        if str(file):  # not empty
            # try:
            seg_image = load_image(file, is_segmentation=True)

            if is_validation:
                self.seg3D_validation = seg_image.get_timepoint(0)
            else:
                self.seg3D = seg_image.get_timepoint(0)  # 3D

            if is_validation:
                if (
                    self.seg3D_validation.shape != self.image3D.shape
                    and self.seg3D.shape != self.image3D.shape
                ):
                    raise ValueError()  # segmentation must exist
            else:
                if self.seg3D.shape != self.image3D.shape:  # shapes must agree
                    raise ValueError()

            if is_validation:  # rename class names
                self.class_names_validation = seg_image.get_class_names()
                tmp = {}
                for i in self.class_names_validation.keys():
                    tmp[i + "_v"] = self.class_names_validation[i]
                self.class_names_validation = tmp
                self.class_colors = seg_image.get_class_colors()

            else:
                self.class_names = seg_image.get_class_names()

            self.class_colors = seg_image.get_class_colors()  # "rgb(a,b,c)"

            self.__update2D(index=None)  # sets seg2D and paints it
            # except FileNotFoundError:
            #     print("Segmentation file name invalid.")
            # except ValueError:
            #     print("Segmentation invalid")

    def __load_validation_segmentation(self, b):
        self.__load_segmentation(b, True)

    def __debug(self, string):
        global is_debug
        if is_debug:
            self.out.append_stdout(string + "\n")

    def __get_rot_axes(self):
        if self.curr_axis == 0:
            return [1, 2]
        elif self.curr_axis == 1:
            return [0, 2]
        else:
            return [0, 1]

    def __clear_segmentation(self, b):
        if self.seg3D is not None:
            self.seg3D = None
            self.seg2D = None
            self.__update2D(None)

    def __clear_validation(self, b):
        if self.seg3D_validation is not None:
            self.seg3D_validation = None
            self.seg2D_validation = None
            self.__update2D(None)

    # --- public methods ---

    def set_figure_size(self, width, height):
        """Set width and height of image widget (includes colorbar)"""
        self.widget.layout.width = width
        self.widget.layout.height = height

    def set_colormap(self, cmap="Inferno"):
        """Changes the figure's colormap"""
        self.widget.update_coloraxes(
            cmin=np.min(self.image3D),
            cmax=np.max(self.image3D),
            colorscale=cmap,
            title="Class",
        )

        self.__debug(
            "cmin=" + str(np.min(self.image3D)) + ", cmax=" + str(np.max(self.image3D))
        )

    def add_class_names(self, names, indices):
        """Sets indices as the colorbar ticks and names as the tick labels."""
        self.widget.update_coloraxes(
            colorbar_tickmode="array",
            colorbar_tickvals=indices,
            colorbar_ticktext=names,
        )

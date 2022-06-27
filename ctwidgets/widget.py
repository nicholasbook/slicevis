import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go


# function to show static image of a slice (2D) of 4D image
def show_image(image2D, title="Slice of 4D image", color="gray"):
    if image2D.ndim != 2:
        raise ValueError("input image must be 2D")

    fig = plt.figure(figsize=(10.0, 10.0))
    plt.imshow(image2D, cmap=color)


def show_image_interactive(image2D, title="Slice of 4D image", color="gray"):
    if image2D.ndim != 2:
        raise ValueError("input image must be 2D")

    fig = px.imshow(image2D, title=title, color_continuous_scale=color)
    # fig.update_layout()
    fig.show()


# all images should have:
# xlabel, xlabel, title, colorbar

# interactive image should have:
# optional histogram, some statistics, toggle between axes (axial, coronal, saggital),
# slider for slice, button for animation, loadable segmentation overlay
# https://plotly.com/python/figurewidget-app/
# flip image?

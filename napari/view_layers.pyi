# flake8: noqa
from typing import List, Sequence, Union

import napari

def view_image(
    data=None,
    *,
    channel_axis=None,
    rgb=None,
    colormap=None,
    contrast_limits=None,
    gamma=1,
    interpolation="nearest",
    rendering="mip",
    iso_threshold=0.5,
    attenuation=0.05,
    name=None,
    metadata=None,
    scale=None,
    translate=None,
    rotate=None,
    shear=None,
    affine=None,
    opacity=1,
    blending=None,
    visible=True,
    multiscale=None,
    title="napari",
    ndisplay=2,
    order=(),
    axis_labels=(),
    show=True
) -> napari.viewer.Viewer: ...
def view_tracks(
    data,
    *,
    properties=None,
    graph=None,
    tail_width=2,
    tail_length=30,
    name=None,
    metadata=None,
    scale=None,
    translate=None,
    rotate=None,
    shear=None,
    affine=None,
    opacity=1,
    blending="additive",
    visible=True,
    colormap="turbo",
    color_by="track_id",
    colormaps_dict=None,
    title="napari",
    ndisplay=2,
    order=(),
    axis_labels=(),
    show=True
) -> napari.viewer.Viewer: ...
def view_shapes(
    data=None,
    *,
    ndim=None,
    properties=None,
    text=None,
    shape_type="rectangle",
    edge_width=1,
    edge_color="black",
    edge_color_cycle=None,
    edge_colormap="viridis",
    edge_contrast_limits=None,
    face_color="white",
    face_color_cycle=None,
    face_colormap="viridis",
    face_contrast_limits=None,
    z_index=0,
    name=None,
    metadata=None,
    scale=None,
    translate=None,
    rotate=None,
    shear=None,
    affine=None,
    opacity=0.7,
    blending="translucent",
    visible=True,
    title="napari",
    ndisplay=2,
    order=(),
    axis_labels=(),
    show=True
) -> napari.viewer.Viewer: ...
def view_points(
    data=None,
    *,
    ndim=None,
    properties=None,
    text=None,
    symbol="o",
    size=10,
    edge_width=1,
    edge_color="black",
    edge_color_cycle=None,
    edge_colormap="viridis",
    edge_contrast_limits=None,
    face_color="white",
    face_color_cycle=None,
    face_colormap="viridis",
    face_contrast_limits=None,
    n_dimensional=False,
    name=None,
    metadata=None,
    scale=None,
    translate=None,
    rotate=None,
    shear=None,
    affine=None,
    opacity=1,
    blending="translucent",
    visible=True,
    title="napari",
    ndisplay=2,
    order=(),
    axis_labels=(),
    show=True
) -> napari.viewer.Viewer: ...
def view_vectors(
    data,
    *,
    properties=None,
    edge_width=1,
    edge_color="red",
    edge_color_cycle=None,
    edge_colormap="viridis",
    edge_contrast_limits=None,
    length=1,
    name=None,
    metadata=None,
    scale=None,
    translate=None,
    rotate=None,
    shear=None,
    affine=None,
    opacity=0.7,
    blending="translucent",
    visible=True,
    title="napari",
    ndisplay=2,
    order=(),
    axis_labels=(),
    show=True
) -> napari.viewer.Viewer: ...
def view_labels(
    data,
    *,
    num_colors=50,
    properties=None,
    color=None,
    seed=0.5,
    name=None,
    metadata=None,
    scale=None,
    translate=None,
    rotate=None,
    shear=None,
    affine=None,
    opacity=0.7,
    blending="translucent",
    visible=True,
    multiscale=None,
    title="napari",
    ndisplay=2,
    order=(),
    axis_labels=(),
    show=True
) -> napari.viewer.Viewer: ...
def view_surface(
    data,
    *,
    colormap="gray",
    contrast_limits=None,
    gamma=1,
    name=None,
    metadata=None,
    scale=None,
    translate=None,
    rotate=None,
    shear=None,
    affine=None,
    opacity=1,
    blending="translucent",
    visible=True,
    title="napari",
    ndisplay=2,
    order=(),
    axis_labels=(),
    show=True
) -> napari.viewer.Viewer: ...
def view_path(
    path: Union[str, Sequence[str]],
    *,
    stack: bool = False,
    plugin: Union[str, None] = None,
    layer_type: Union[str, None] = None,
    title="napari",
    ndisplay=2,
    order=(),
    axis_labels=(),
    show=True,
    **kwargs
) -> napari.viewer.Viewer: ...

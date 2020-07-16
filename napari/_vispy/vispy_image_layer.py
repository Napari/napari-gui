import warnings
from vispy.scene.visuals import Image as ImageNode
from .volume import Volume as VolumeNode
from vispy.color import Colormap
import numpy as np
from .vispy_base_layer import VispyBaseLayer
from ..layers.image._image_constants import Rendering


texture_dtypes = [
    np.dtype(np.int8),
    np.dtype(np.uint8),
    np.dtype(np.int16),
    np.dtype(np.uint16),
    np.dtype(np.float32),
]


class VispyImageLayer(VispyBaseLayer):
    def __init__(self, layer):
        self._image_node = ImageNode(None, method='auto')
        self._volume_node = VolumeNode(np.zeros((1, 1, 1)), clim=[0, 1])
        super().__init__(layer, self._image_node)

        self.layer.events.rendering.connect(self._on_rendering_change)
        self.layer.events.interpolation.connect(self._on_interpolation_change)
        self.layer.events.colormap.connect(self._on_colormap_change)
        self.layer.events.contrast_limits.connect(
            self._on_contrast_limits_change
        )
        self.layer.events.gamma.connect(self._on_gamma_change)
        self.layer.events.iso_threshold.connect(self._on_threshold_change)
        self.layer.events.attenuation.connect(self._on_threshold_change)

        self._on_display_change()
        self._on_data_change()

    def _on_display_change(self, data=None):
        parent = self.node.parent
        self.node.parent = None

        if self.layer.dims.ndisplay == 2:
            self._image_node.set_data(data)
            self.node = self._image_node
        else:
            if data is None:
                data = np.zeros((1, 1, 1))
            self._volume_node.set_data(data, clim=self.layer.contrast_limits)
            self.node = self._volume_node

        self.node.parent = parent
        self.reset()

    def _data_astype(self, data, dtype):
        """Broken out as a separate function for perfmon reasons."""
        return data.astype(dtype)

    def _on_data_change(self, event=None):
        data = self.layer._data_view
        dtype = np.dtype(data.dtype)
        if dtype not in texture_dtypes:
            try:
                dtype = dict(
                    i=np.int16, f=np.float32, u=np.uint16, b=np.uint8
                )[dtype.kind]
            except KeyError:  # not an int or float
                raise TypeError(
                    f'type {dtype} not allowed for texture; must be one of {set(texture_dtypes)}'  # noqa: E501
                )
            data = self._data_astype(data, dtype)

        if self.layer.dims.ndisplay == 3 and self.layer.dims.ndim == 2:
            data = np.expand_dims(data, axis=0)

        # Check if data exceeds MAX_TEXTURE_SIZE and downsample
        if (
            self.MAX_TEXTURE_SIZE_2D is not None
            and self.layer.dims.ndisplay == 2
        ):
            data = self.downsample_texture(data, self.MAX_TEXTURE_SIZE_2D)
        elif (
            self.MAX_TEXTURE_SIZE_3D is not None
            and self.layer.dims.ndisplay == 3
        ):
            data = self.downsample_texture(data, self.MAX_TEXTURE_SIZE_3D)

        # Check if ndisplay has changed current node type needs updating
        if (
            self.layer.dims.ndisplay == 3
            and not isinstance(self.node, VolumeNode)
        ) or (
            self.layer.dims.ndisplay == 2
            and not isinstance(self.node, ImageNode)
        ):
            self._on_display_change(data)
        else:
            if self.layer.dims.ndisplay == 2:
                self.node._need_colortransform_update = True
                self.node.set_data(data)
            else:
                self.node.set_data(data, clim=self.layer.contrast_limits)

        # Call to update order of translation values with new dims:
        self._on_scale_change()
        self._on_translate_change()
        self.node.update()

    def _on_interpolation_change(self, event=None):
        self.node.interpolation = self.layer.interpolation

    def _on_rendering_change(self, event=None):
        if self.layer.dims.ndisplay == 3:
            self.node.method = self.layer.rendering
            self._on_threshold_change()

    def _on_colormap_change(self, event=None):
        cmap = self.layer.colormap[1]
        if self.layer.gamma != 1:
            # when gamma!=1, we instantiate a new colormap
            # with 256 control points from 0-1
            cmap = Colormap(cmap[np.linspace(0, 1, 256) ** self.layer.gamma])

        # Below is fixed in #1712
        if not self.layer.dims.ndisplay == 2:
            self.node.view_program['texture2D_LUT'] = (
                cmap.texture_lut() if (hasattr(cmap, 'texture_lut')) else None
            )
        self.node.cmap = cmap

    def _on_contrast_limits_change(self, event=None):
        if self.layer.dims.ndisplay == 2:
            self.node.clim = self.layer.contrast_limits
        else:
            self._on_data_change()

    def _on_gamma_change(self, event=None):
        self._on_colormap_change()

    def _on_threshold_change(self, event=None):
        if self.layer.dims.ndisplay == 2:
            return
        rendering = Rendering(self.layer.rendering)
        if rendering == Rendering.ISO:
            self.node.threshold = float(self.layer.iso_threshold)
        elif rendering == Rendering.ATTENUATED_MIP:
            self.node.threshold = float(self.layer.attenuation)

        # Fix for #1399, should be fixed in the VisPy threshold setter
        if 'u_threshold' not in self.node.shared_program:
            self.node.shared_program['u_threshold'] = self.node._threshold
            self.node.update()

    def reset(self, event=None):
        self._reset_base()
        self._on_interpolation_change()
        self._on_colormap_change()
        self._on_rendering_change()
        if self.layer.dims.ndisplay == 2:
            self._on_contrast_limits_change()

    def downsample_texture(self, data, MAX_TEXTURE_SIZE):
        """Downsample data based on maximum allowed texture size.

        Parameters
        ----------
        data : array
            Data to be downsampled if needed.
        MAX_TEXTURE_SIZE : int
            Maximum allowed texture size.

        Returns
        -------
        data : array
            Data that now fits inside texture.
        """
        if np.any(np.greater(data.shape, MAX_TEXTURE_SIZE)):
            if self.layer.multiscale:
                raise ValueError(
                    f"Shape of individual tiles in multiscale {data.shape} "
                    f"cannot exceed GL_MAX_TEXTURE_SIZE "
                    f"{MAX_TEXTURE_SIZE}. Rendering is currently in "
                    f"{self.layer.dims.ndisplay}D mode."
                )
            warnings.warn(
                f"data shape {data.shape} exceeds GL_MAX_TEXTURE_SIZE "
                f"{MAX_TEXTURE_SIZE} in at least one axis and "
                f"will be downsampled. Rendering is currently in "
                f"{self.layer.dims.ndisplay}D mode."
            )
            downsample = np.ceil(
                np.divide(data.shape, MAX_TEXTURE_SIZE)
            ).astype(int)
            scale = np.ones(self.layer.ndim)
            for i, d in enumerate(self.layer.dims.displayed):
                scale[d] = downsample[i]
            self.layer._transforms['tile2data'].scale = scale
            self._on_scale_change()
            slices = tuple(slice(None, None, ds) for ds in downsample)
            data = data[slices]
        return data

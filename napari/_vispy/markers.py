from vispy.scene.visuals import Markers as BaseMarkers


# Custom markers class is needed for entering 3D rendering mode when a points
# layer is invisible and the self._data property is None
class Markers(BaseMarkers):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _compute_bounds(self, axis, view):
        # This if statement needs to be added to vispy master
        if self._data is None:
            return None
        pos = self._data['a_position']
        if pos is None:
            return None
        if pos.shape[1] > axis:
            return (pos[:, axis].min(), pos[:, axis].max())
        else:
            return (0, 0)

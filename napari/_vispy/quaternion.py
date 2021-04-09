import numpy as np


def quaternion2euler(quaternion, degrees=False):
    """Converts VisPy quaternion into euler angle representation.

    Parameters
    ----------
    quaternion : vispy.util.Quaternion
        Quaternion for conversion.
    degrees : bool
        If output is returned in degrees or radians.

    Returns
    -------
    angles : 3-tuple
        Euler angles in (rx, ry, rz) order.
    """
    
    def capper(value):
        # Cap the value to +1 or -1
        value_capped = value if abs(value) < 1 else np.sign(value)
        return value_capped
    
    
    q = quaternion
    angles = (
        np.arctan2(
            2 * (q.w * q.z + q.y * q.x),
            1 - 2 * (q.y * q.y + q.z * q.z),
        ),
        np.arcsin(capper(2 * (q.w * q.y - q.z * q.x))),
        np.arctan2(
            2 * (q.w * q.x + q.y * q.z),
            1 - 2 * (q.x * q.x + q.y * q.y),
        ),
    )
    if degrees:
        return tuple(np.degrees(angles))
    else:
        return angles

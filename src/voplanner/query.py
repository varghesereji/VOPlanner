from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord
import astropy.units as u
import numpy as np


def query_target_radec(target_name):
    """
    Query SIMBAD for RA/Dec of a target by name.

    Parameters
    ----------
    target_name : str

    Returns
    -------
    coord : astropy.coordinates.SkyCoord or None
        SkyCoord if found, None if not resolvable.
    """

    try:
        result = Simbad.query_object(target_name)
    except Exception:
        return None

    if result is None or len(result) == 0:
        return None
    ra = result['ra'][0]
    dec = result['dec'][0]

    # Safety: catch masked values
    if np.ma.is_masked(ra) or np.ma.is_masked(dec):
        return None

    coord = SkyCoord(
        ra, dec,
        unit=(u.hourangle, u.deg),
        frame='icrs'
    )

    return coord

# end

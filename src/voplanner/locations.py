import astropy.units as u
from astropy.coordinates import EarthLocation
from pytz import timezone
from astroplan import Observer


locations_dict = {
    "subaru": {
        'name': "Subaru Telescope", # Telescope name
        'long': '-155d28m48.900s',
        'lat': '+19d49m42.600s',
        'elev': 4163,
        'pres': 0.615,
        'hum': 0.11,
        'temp': 0,
        'tz': 'US/Hawaii',
        'description': "Subaru Telescope on Maunakea, Hawaii"
        }
}


def make_observer(telescope):
    telescope = locations_dict[telescope]
    longitude = telescope['long']
    latitude = telescope['lat']
    elevation = telescope['elev'] * u.m
    location = EarthLocation.from_geodetic(longitude, latitude, elevation)

    observer = Observer(name=telescope['name'],
                        location=location,
                        pressure=telescope['pres'] * u.bar,
                        relative_humidity=telescope['hum'],
                        temperature=telescope['temp'] * u.deg_C,
                        timezone=timezone(telescope['tz']),
                        description=telescope['description'])
    return observer



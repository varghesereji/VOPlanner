from astropy.time import TimeDelta
from astropy.time import Time
from astropy.table import Table
from astroplan import FixedTarget
from astroplan.plots import plot_altitude
from astroplan.plots import plot_sky
import  astropy.units as u
import pytz
from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from astropy.coordinates import SkyCoord
import numpy as np

from .locations import make_observer
from .setups import read_args
from .setups import read_config


# Plotting
def plotting_one(time, observer, target, ax=None):
    if ax is None:
        plot_altitude(target, observer, time, airmass_yaxis=True)
    else:
        plot_altitude(target, observer, time, ax=ax, airmass_yaxis=True)


def plotting_sky(time, observer, target, ax=None):
    if ax is None:
        plot_sky(target, observer, time)
    else:
        plot_sky(target, observer, time, ax=ax)

def time_from_local(timestr, observer):
    tz = observer.timezone
    time = Time(tz.localize(
        datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S")
        )
                )
    return time


def main():
    # print("The function will be added soon")
    # print(make_observer('subaru'))
    args = read_args().parse_args()
    configfilename = args.config
    config = read_config(configfilename)
    location = config['setups']['LOCATION']
    # print(location)
    # print(make_observer(location))
    observer = make_observer(location.lower())
    timezone = observer.timezone
    t_start = time_from_local(config['setups']['START'], observer)
    t_end = time_from_local(config['setups']['END'], observer)
    interval = config['setups']['INTERVAL_HRS']
    times = t_start + np.arange(
        0, (t_end - t_start).to(u.hour).value + 0.001, float(interval)
    ) * u.hour

    # Get targets
    targets_list_fname = config['inputs']['TARGETS']
    tbl = Table.read(targets_list_fname, format="csv")
    # print(tbl)
    targets_name = tbl['name']
    # print(targets_name)
    fig, ax = plt.subplots()
    fig2, ax2 = plt.subplots(subplot_kw={"projection": "polar"})

    for i, name in enumerate(targets_name):
        ra = tbl['ra'][i]
        dec = tbl['dec'][i]
        coords = ra + " " + dec
        target = FixedTarget(coord=SkyCoord(coords),
                             name=name)
        plotting_one(times, observer, target, ax=ax)
        plotting_sky(times, observer, target, ax=ax2)
    xticks = ax.get_xticks()
    times_utc = Time(mdates.num2date(xticks))
    times_local = times_utc.to_datetime(timezone=timezone)
    ax.set_xticklabels([t.strftime("%H:%M") for t in times_local])
    ax.set_xlabel("Time (IST)")
    start_local = t_start.to_datetime(timezone=timezone)
    obs_date = start_local.strftime("%d %b %Y")
    ax.legend(loc="center left", shadow=True,
              bbox_to_anchor=(1.02, 0.5))
    ax.grid()
    ax.set_title(f"Date: {obs_date}")

    # ax2.set_theta_zero_location('N')
    plt.show()

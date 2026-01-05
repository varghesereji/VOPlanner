from astropy.time import TimeDelta
from astropy.time import Time
from astropy.table import Table
from astroplan import FixedTarget
from astroplan.plots import plot_altitude
from astroplan.plots import plot_sky
import astropy.units as u

from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import mplcursors

from astropy.coordinates import SkyCoord
import numpy as np

from .locations import make_observer
from .setups import read_args
from .setups import read_config
from .query import query_target_radec


# Plotting
def plotting_one(time, observer, target, ax=None):
    if ax is None:
        ax = plt.gca()
        plot_altitude(target, observer, time, airmass_yaxis=True)
    else:
        plot_altitude(target, observer, time, ax=ax, airmass_yaxis=True)
    line = ax.lines[-1]
    line.set_label(target.name)
    return line


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
    lines = []
    for i, name in enumerate(targets_name):
        ra = tbl['ra'][i]
        dec = tbl['dec'][i]
        if ra is np.ma.masked or dec is np.ma.masked:
            # print(ra, dec)
            target = targets_name[i]
            print("Coordinates of {} not given. Querying in Simbad".format(
                target))
            coord = query_target_radec(target)
            # continue
        else:
            coords = ra + " " + dec
            coord = SkyCoord(coords)
        target = FixedTarget(coord=coord,
                             name=name)
        line = plotting_one(times, observer, target, ax=ax)
        lines.append(line)
        plotting_sky(times, observer, target, ax=ax2)
    cursor = mplcursors.cursor(lines, hover=True)

    @cursor.connect("add")
    def on_add(sel):
        line = sel.artist

        # Highlight hovered curve
        for l in lines:
            l.set_linewidth(1)
            l.set_alpha(0.3)

        line.set_linewidth(3)
        line.set_alpha(1.0)

        x, y = sel.target

        t_utc = Time(mdates.num2date(x))
        t_local = t_utc.to_datetime(timezone=timezone)
        label = (
            rf"$\bf{{{line.get_label()}}}$" "\n"
            rf"Time : {t_local.strftime('%H:%M')}" "\n"
            rf"Alt : ${y:.1f}^o$"
            )
        # sel.annotation.set_text(line.get_label())
        sel.annotation.set_text(label)
        sel.annotation.get_bbox_patch().set(fc="white", alpha=0.9)

        fig.canvas.draw_idle()

    @cursor.connect("remove")
    def on_remove(sel):
        for li in lines:
            li.set_linewidth(1)
            li.set_alpha(0.6)
        fig.canvas.draw_idle()
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

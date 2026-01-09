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


# coordinate

import re
import astropy.units as u
from astropy.coordinates import SkyCoord, Angle

def extract_numbers(val):
    return list(map(float, re.findall(r"[-+]?\d*\.?\d+", val)))

def normalize_sexagesimal(sign, a, b, c):
    b += int(c // 60)
    c = c % 60

    a += int(b // 60)
    b = b % 60

    return sign * a, b, c


def smart_skycoord(ra, dec, frame="icrs"):
    # --- 1. Try Astropy directly ---
    try:
        return SkyCoord(ra, dec, frame=frame)
    except Exception:
        pass

    # --- 2. Parse RA ---
    ra_nums = extract_numbers(ra)
    if len(ra_nums) == 1:
        ra_angle = Angle(ra_nums[0], unit=u.deg)
    elif len(ra_nums) >= 3:
        h, m, s = ra_nums[:3]
        h, m, s = normalize_sexagesimal(1, h, m, s)
        ra_angle = Angle((h + m/60 + s/3600) * 15, unit=u.deg)
    else:
        raise ValueError(f"Unrecognized RA format: {ra}")

    # --- 3. Parse Dec ---
    dec_nums = extract_numbers(dec)
    sign = -1 if "-" in dec.strip() else 1
    if len(dec_nums) == 1:
        dec_angle = Angle(sign * dec_nums[0], unit=u.deg)
    elif len(dec_nums) >= 3:
        d, m, s = dec_nums[:3]
        d, m, s = normalize_sexagesimal(sign, d, m, s)
        dec_angle = Angle(d + m/60 + s/3600, unit=u.deg)
    else:
        raise ValueError(f"Unrecognized Dec format: {dec}")

    return SkyCoord(ra=ra_angle, dec=dec_angle, frame=frame)


# Plotting
def plotting_one(time, observer, target, ax=None, limits=(0, 90)):
    if ax is None:
        ax = plt.gca()
        plot_altitude(target, observer, time, airmass_yaxis=True,
                      min_altitude=limits[0],
                      max_altitude=limits[-1])
    else:
        plot_altitude(target, observer, time, ax=ax, airmass_yaxis=True,
                      min_altitude=limits[0],
                      max_altitude=limits[-1])
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
        print("Doing for ", name)
        if ra is np.ma.masked or dec is np.ma.masked:
            # print(ra, dec)
            target = targets_name[i]
            print("Coordinates of {} not given. Querying in Simbad".format(
                target))
            coord = query_target_radec(target)
            if coord is None:
                print("Couldn't complete query. Check target name")
                continue
        else:
            # coords = ra + " " + dec
            coord = smart_skycoord(ra, dec)
            # coord = SkyCoord(ra=ra, dec=dec)  #, coords)
        target = FixedTarget(coord=coord,
                             name=name)
        min_alt = float(config['setups']['MIN_ALT'])
        max_alt = float(config['setups']['MAX_ALT'])
        line = plotting_one(times, observer, target, ax=ax,
                            limits=(min_alt, max_alt))
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

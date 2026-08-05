#!/usr/bin/env python3
import math, datetime, sys

LAT, LON = 49.28, -123.12

def sun_times(lat, lon, date):
    n = date.timetuple().tm_yday
    lng_hour = lon / 15

    def calc(setting):
        t = n + ((18 if setting else 6) - lng_hour) / 24
        m = 0.9856 * t - 3.289
        mr = math.radians(m)
        l = m + 1.916 * math.sin(mr) + 0.020 * math.sin(2 * mr) + 282.634
        l %= 360
        lr = math.radians(l)
        ra = math.degrees(math.atan2(0.91764 * math.sin(lr), math.cos(lr)))
        ra %= 360
        ra_hr = ra / 15
        sin_dec = 0.39782 * math.sin(lr)
        cos_dec = math.cos(math.asin(sin_dec))
        zenith = 90.833
        cos_h = (math.cos(math.radians(zenith)) - sin_dec * math.sin(math.radians(lat))) / (cos_dec * math.cos(math.radians(lat)))
        if cos_h > 1 or cos_h < -1:
            return None
        h = math.degrees(math.acos(cos_h))
        if not setting:
            h = 360 - h
        h /= 15
        ut = (h + ra_hr - 0.06571 * t - 6.622 - lng_hour) % 24
        return ut

    rise = calc(False)
    sett = calc(True)
    return rise, sett

def fmt_delta(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    if h > 0:
        return f"{h}h {m}m"
    return f"{m}m"

now = datetime.datetime.now()
today = now.date()
rise_h, set_h = sun_times(LAT, LON, today)

tz_offset = now.astimezone().utcoffset().total_seconds() / 3600
rise_local = (rise_h + tz_offset) % 24
set_local = (set_h + tz_offset) % 24

now_h = now.hour + now.minute / 60 + now.second / 3600

rise_time = f"{int(rise_local)}:{int((rise_local % 1) * 60):02d}"
set_time = f"{int(set_local)}:{int((set_local % 1) * 60):02d}"

rise_sec = (rise_local - now_h) * 3600
set_sec = (set_local - now_h) * 3600

if rise_sec < 0:
    rise_sec += 86400
if set_sec < 0:
    set_sec += 86400

if now_h < rise_local:
    print(f"sunrise in {fmt_delta(rise_sec)}")
elif now_h < set_local:
    print(f"sunset in {fmt_delta(set_sec)}")
else:
    print(f"sunrise in {fmt_delta(rise_sec)}")

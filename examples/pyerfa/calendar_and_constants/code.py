"""
A first look at PyERFA: the Python wrapper for the ERFA C library
of fundamental astronomy routines (the open-source counterpart of
the IAU's SOFA library).

Every ERFA function is exposed as a NumPy universal function, so
they accept scalars or arrays interchangeably. See the docs at
https://pyerfa.readthedocs.io/ for the full catalogue.
"""
from IPython.core.display import display, HTML

# ERFA exposes a number of useful astronomical constants from erfam.h.
heading("Some ERFA constants")
note(
    "These come straight from the ERFA C library and are handy "
    "when working with time and angles."
)
constants = {
    "DAYSEC (seconds in a day)": erfa.DAYSEC,
    "DJY (days in a Julian year)": erfa.DJY,
    "DAU (astronomical unit, metres)": erfa.DAU,
    "CMPS (speed of light, m/s)": erfa.CMPS,
    "DR2D (radians to degrees)": erfa.DR2D,
}
rows = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in constants.items())
display(HTML(f"<table>{rows}</table>"), append=True)


# Julian Date 2460000.5 corresponds to 2023-02-25 00:00 UTC. Let's
# convert four consecutive JDs to calendar dates with erfa.jd2cal.
heading("Julian dates to calendar dates")
note(
    "erfa.jd2cal is a NumPy ufunc, so it broadcasts over array "
    "inputs and returns aligned arrays of year, month, day, and "
    "fractional day."
)

jd_base = 2460000.0
jd_offsets = np.array([0, 1, 2, 3])
year, month, day, frac = erfa.jd2cal(jd_base, jd_offsets)

note(f"Year:  {year.tolist()}")
note(f"Month: {month.tolist()}")
note(f"Day:   {day.tolist()}")
note(f"Frac:  {frac.tolist()}")


# Going the other direction: calendar -> two-part Julian Date.
heading("Calendar dates to Julian dates")
note(
    "erfa.cal2jd returns a (DJM0, DJM) pair where DJM0 is the MJD "
    "zero-point (2400000.5) and DJM is the Modified Julian Date."
)
djm0, djm = erfa.cal2jd(2024, 7, 20)
note(f"For 2024-07-20: DJM0 = {djm0}, MJD = {djm}, JD = {djm0 + djm}")

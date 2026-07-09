"""
A first look at bilby.cython: gravitational-wave geometry helpers.

bilby.cython provides fast, Cython-accelerated implementations of the
geometry routines used by the Bilby gravitational-wave inference
library. The package is installed as `bilby.cython` but imported as
`bilby_cython`.

We'll compute polarization tensors for an astrophysical source on the
sky and then project them against a simple detector response tensor
to get the antenna pattern factors F+ and Fx.

Docs and source: https://git.ligo.org/colm.talbot/bilby-cython
"""
import numpy as np
from bilby_cython import geometry
from IPython.core.display import display, HTML

heading("A source on the sky")
note(
    "We pick a sky location (right ascension, declination), a "
    "polarization angle psi, and a GPS time. These four numbers "
    "fully specify how a passing gravitational wave is oriented "
    "relative to Earth."
)

right_ascension = 1.375   # radians
declination = -1.2108     # radians
polarization_angle = 2.659
gps_time = 1126259642.413  # GW150914-ish

# Plus and cross polarization tensors are 3x3 symmetric matrices.
e_plus = geometry.get_polarization_tensor(
    ra=right_ascension,
    dec=declination,
    time=gps_time,
    psi=polarization_angle,
    mode="plus",
)
e_cross = geometry.get_polarization_tensor(
    ra=right_ascension,
    dec=declination,
    time=gps_time,
    psi=polarization_angle,
    mode="cross",
)

note("Plus polarization tensor e+:")
display(np.round(e_plus, 4), append=True)
note("Cross polarization tensor e×:")
display(np.round(e_cross, 4), append=True)

heading("A toy detector response tensor")
note(
    "A real interferometer response tensor is built from its two arm "
    "vectors as (x⊗x − y⊗y) / 2. Here we use the LIGO Hanford arms "
    "(approximate unit vectors in Earth-centered coordinates)."
)

x_arm = np.array([-0.2239, 0.7998, 0.5569])
y_arm = np.array([-0.9140, 0.0261, -0.4049])
detector_tensor = 0.5 * (np.outer(x_arm, x_arm) - np.outer(y_arm, y_arm))

# three_by_three_matrix_contraction computes sum_ij A_ij B_ij,
# which is exactly the antenna pattern factor for a given mode.
f_plus = geometry.three_by_three_matrix_contraction(
    detector_tensor, e_plus,
)
f_cross = geometry.three_by_three_matrix_contraction(
    detector_tensor, e_cross,
)

note(
    f"Antenna pattern factors at this sky location: "
    f"<strong>F+ = {f_plus:+.4f}</strong>, "
    f"<strong>F× = {f_cross:+.4f}</strong>."
)
note(
    "These tell us how strongly the detector responds to each "
    "polarization for a wave coming from this direction."
)

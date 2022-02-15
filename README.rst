wind-3dp-loader
===============

Python data loader for Wind/3DP instrument. At the moment provides released data obtained by SunPy through CDF files from CDAWeb for the following datasets:

- WI_SFSP_3DP: Electron omnidirectional fluxes 27 keV - 520 keV, often at 24 sec
- WI_SFPD_3DP: Electron energy-angle distributions 27 keV to 520 keV, often at 24 sec
- WI_SOSP_3DP: Proton omnidirectional fluxes 70 keV - 6.8 MeV, often at 24 sec
- WI_SOPD_3DP: Proton energy-angle distributions 70 keV - 6.8 MeV, often at 24 sec

Installation
------------

wind_3dp_loader requires python >= 3.6 and SunPy >= 3.1.3

It can be installed from this repository using pip:

.. code:: bash

    pip install git+https://github.com/jgieseler/wind-3dp-loader

Usage
-----

The standard usecase is to utilize the ``wind3dp_load`` function, which
returns Pandas dataframe(s) of the Wind/3DP measurements.

.. code:: python

   from wind_3dp_loader import wind3dp_load
   import datetime as dt

   df = wind3dp_load(
    dataset="WI_SFPD_3DP",
    starttime=dt.datetime(2021, 4, 16),
    endtime="2021/04/20",
    resample="1min",
    multi_index=True
)

Input
~~~~~

-  ``dataset``: ``'WI_SFSP_3DP'``, ``'WI_SFPD_3DP'``, ``'WI_SOSP_3DP'``, or ``'WI_SOPD_3DP'``. See above for explanation.
-  ``starttime``, ``endtime``: datetime object or "standard" datetime string
-  ``resample``: Pandas frequency (e.g., ``'1min'``), or ``None``, optional. Frequency to which the original data (~24 seconds) is resamepled. By default ``'1min'``.
-  ``multi_index``: ``True``, or ``'False'`` (boolean), optional. Provide output for pitch-angle resolved data as Pandas Dataframe with multiindex. By default ``True``.

Return
~~~~~~

-  Pandas data frame, optional multiindex for pitch-angle resolved fluxes. Energies are given in ``eV``, differential intensities in ``cm-2 s-1 sr-1 eV-1``


Data folder structure
---------------------

All data files are automatically saved in a SunPy subfolder of the current user home directory.


License
-------

This project is Copyright (c) Jan Gieseler and licensed under
the terms of the BSD 3-clause license. This package is based upon
the `Openastronomy packaging guide <https://github.com/OpenAstronomy/packaging-guide>`_
which is licensed under the BSD 3-clause licence. See the licenses folder for
more information.

Acknowledgements
----------------

The development of this software has received funding from the European Union's Horizon 2020 research and innovation programme under grant agreement No 101004159 (SERPENTINE).

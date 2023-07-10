This package is not maintained any more! Please use https://github.com/serpentine-h2020/SEPpy instead!
======================================================================================================

wind-3dp-loader
===============

|pytest|

.. |pytest| image:: https://github.com/jgieseler/wind-3dp-loader/workflows/pytest/badge.svg

Python data loader for Wind/3DP instrument. At the moment provides released data obtained by SunPy through CDF files from CDAWeb for the following datasets:

- WI_SFSP_3DP: Electron omnidirectional fluxes 27 keV - 520 keV, often at 24 sec (`Info <https://cdaweb.gsfc.nasa.gov/misc/NotesW.html#WI_SFSP_3DP>`_, `Metadata <https://cdaweb.gsfc.nasa.gov/pub/software/cdawlib/0SKELTABLES/wi_sfsp_3dp_00000000_v01.skt>`_)
- WI_SFPD_3DP: Electron energy-angle distributions 27 keV to 520 keV, often at 24 sec (`Info <https://cdaweb.gsfc.nasa.gov/misc/NotesW.html#WI_SFPD_3DP>`_, `Metadata <https://cdaweb.gsfc.nasa.gov/pub/software/cdawlib/0SKELTABLES/wi_sfpd_3dp_00000000_v01.skt>`_)
- WI_SOSP_3DP: Proton omnidirectional fluxes 70 keV - 6.8 MeV, often at 24 sec (`Info <https://cdaweb.gsfc.nasa.gov/misc/NotesW.html#WI_SOSP_3DP>`_, `Metadata <https://cdaweb.gsfc.nasa.gov/pub/software/cdawlib/0SKELTABLES/wi_sosp_3dp_00000000_v01.skt>`_)
- WI_SOPD_3DP: Proton energy-angle distributions 70 keV - 6.8 MeV, often at 24 sec (`Info <https://cdaweb.gsfc.nasa.gov/misc/NotesW.html#WI_SOPD_3DP>`_, `Metadata <https://cdaweb.gsfc.nasa.gov/pub/software/cdawlib/0SKELTABLES/wi_sopd_3dp_00000000_v01.skt>`_)

Disclaimer
----------
This software is provided "as is", with no guarantee. It is no official data source, and not officially endorsed by the corresponding instrument teams. Please always refer to the instrument descriptions before using the data!


Usage
-----

The standard usecase is to utilize the ``wind3dp_load`` function, which
returns Pandas dataframe(s) of the Wind/3DP measurements.

.. code:: python

   from wind_3dp_loader import wind3dp_load
   import datetime as dt

   df, meta = wind3dp_load(dataset="WI_SFPD_3DP",
                           startdate=dt.datetime(2021, 4, 16),
                           enddate="2021/04/20",
                           resample="1min",
                           multi_index=True,
                           path=None,
                           threshold=None)

Input
~~~~~

-  ``dataset``: ``'WI_SFSP_3DP'``, ``'WI_SFPD_3DP'``, ``'WI_SOSP_3DP'``, or ``'WI_SOPD_3DP'``. See above for explanation.
-  ``startdate``, ``enddate``: datetime object or "standard" datetime string
-  ``resample``: Pandas frequency (e.g., ``'1min'`` or ``'1h'``), or ``None``, optional. Frequency to which the original data (~24 seconds) is resamepled. By default ``'1min'``.
-  ``multi_index``: ``True``, or ``False`` (boolean), optional. Provide output for pitch-angle resolved data as Pandas Dataframe with multiindex. By default ``True``.
-  ``path``: String, optional. Local path for storing downloaded data, e.g. ``path='data/wind/3dp/'``. By default `None`. Default setting saves data according to `sunpy's Fido standards <https://docs.sunpy.org/en/stable/guide/acquiring_data/fido.html#downloading-data>`_. The default setting can be changed according to the corresponding `sunpy documentation <https://docs.sunpy.org/en/stable/guide/customization.html>`_, where the setting that needs to be changed is named ``download_dir`` (e.g., one could set it to a shared directory on a multi-user system).
-  ``threshold``: Integer or float, optional. Replace all FLUX values in ``df`` above ``threshold`` with ``np.nan``, by default ``None``.
      

Return
~~~~~~

-  Pandas data frame, optional multiindex for pitch-angle resolved fluxes. Energies are given in ``eV``, differential intensities in ``cm-2 s-1 sr-1 eV-1``. See info links above for the different datasets for a description of the dataframe columns.
-  Dictionary of metadata (e.g., energy channels; empty add the moment). 


Data folder structure
---------------------

If no ``path`` argument is provided, all data files are automatically saved in a SunPy subfolder of the current user home directory.


Flux value threshold
--------------------

If a flux ``threshold`` is defined (as integer or float), all fluxes above this value will be replaced with ``np.nan``. This might me useful if there are some 'outlier' data points. For example, see the following two figures for ``threshold=None`` and ``threshold=0.1``, respectively:

|wind3dp_org|
|wind3dp_threshold|

.. |wind3dp_org| image:: https://github.com/jgieseler/wind-3dp-loader/raw/main/docs/wind3dp_org.png
.. |wind3dp_threshold| image:: https://github.com/jgieseler/wind-3dp-loader/raw/main/docs/wind3dp_threshold.png

License
-------

This project is Copyright (c) Jan Gieseler and licensed under
the terms of the BSD 3-clause license. This package is based upon
the `Openastronomy packaging guide <https://github.com/OpenAstronomy/packaging-guide>`_
which is licensed under the BSD 3-clause license. See the licenses folder for
more information.

Acknowledgements
----------------

The development of this software has received funding from the European Union's Horizon 2020 research and innovation programme under grant agreement No 101004159 (SERPENTINE).

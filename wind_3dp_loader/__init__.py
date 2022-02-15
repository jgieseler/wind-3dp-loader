# Licensed under a 3-clause BSD style license - see LICENSE.rst

from pkg_resources import get_distribution, DistributionNotFound
try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    pass  # package is not installed

import cdflib
import numpy as np
import pandas as pd

from sunpy.net import Fido
from sunpy.net import attrs as a


def _date2str(date):
    year = str(date)[0:4]
    month = str(date)[4:6]
    day = str(date)[6:8]
    return year+'/'+month+'/'+day


def _cdf2df_3d(cdf, index_key, dtimeindex=True, badvalues=None,
            ignore=None, include=None):
    """
    Converts a cdf file to a pandas dataframe.
    Note that this only works for 1 dimensional data, other data such as
    distribution functions or pitch angles will not work properly.
    Parameters
    ----------
    cdf : cdf
        Opened CDF file.
    index_key : str
        The CDF key to use as the index in the output DataFrame.
    dtimeindex : bool
        If ``True``, the DataFrame index is parsed as a datetime.
        Default is ``True``.
    badvalues : dict, list
        Deprecated.
    ignore : list
        In case a CDF file has columns that are unused / not required, then
        the column names can be passed as a list into the function.
    include : str, list
        If only specific columns of a CDF file are desired, then the column
        names can be passed as a list into the function. Should not be used
        with ``ignore``.
    Returns
    -------
    df : :class:`pandas.DataFrame`
        Data frame with read in data.
    """
    if badvalues is not None:
        warnings.warn('The badvalues argument is decprecated, as bad values '
                      'are now automatically recognised using the FILLVAL CDF '
                      'attribute.', DeprecationWarning)
    if include is not None:
        if ignore is not None:
            raise ValueError('ignore and include are incompatible keywords')
        if isinstance(include, str):
            include = [include]
        if index_key not in include:
            include.append(index_key)

    # Extract index values
    index_info = cdf.varinq(index_key)
    if index_info['Last_Rec'] == -1:
        raise CDFEmptyError('No records present in CDF file')

    index = cdf.varget(index_key)
    try:
        # If there are multiple indexes, take the first one
        # TODO: this is just plain wrong, there should be a way to get all
        # the indexes out
        index = index[...][:, 0]
    except IndexError:
        pass

    if dtimeindex:
        index = cdflib.epochs.CDFepoch.breakdown(index, to_np=True)
        index_df = pd.DataFrame({'year': index[:, 0],
                                 'month': index[:, 1],
                                 'day': index[:, 2],
                                 'hour': index[:, 3],
                                 'minute': index[:, 4],
                                 'second': index[:, 5],
                                 'ms': index[:, 6],
                                 })
        # Not all CDFs store pass milliseconds
        try:
            index_df['us'] = index[:, 7]
            index_df['ns'] = index[:, 8]
        except IndexError:
            pass
        index = pd.DatetimeIndex(pd.to_datetime(index_df), name='Time')
    data_dict = {}
    npoints = len(index)

    var_list = _get_cdf_vars(cdf)
    keys = {}
    # Get mapping from each attr to sub-variables
    for cdf_key in var_list:
        if ignore:
            if cdf_key in ignore:
                continue
        elif include:
            if cdf_key not in include:
                continue
        if cdf_key == 'Epoch':
            keys[cdf_key] = 'Time'
        else:
            keys[cdf_key] = cdf_key
    # Remove index key, as we have already used it to create the index
    keys.pop(index_key)
    # Remove keys for data that doesn't have the right shape to load in CDF
    # Mapping of keys to variable data
    vars = {cdf_key: cdf.varget(cdf_key) for cdf_key in keys.copy()}
    for cdf_key in keys:
        var = vars[cdf_key]
        if type(var) is np.ndarray:
            key_shape = var.shape
            if len(key_shape) == 0 or key_shape[0] != npoints:
                vars.pop(cdf_key)
        else:
            vars.pop(cdf_key)

    # Loop through each key and put data into the dataframe
    for cdf_key in vars:
        df_key = keys[cdf_key]
        # Get fill value for this key
        try:
            fillval = float(cdf.varattsget(cdf_key)['FILLVAL'])
        except KeyError:
            fillval = np.nan

        if isinstance(df_key, list):
            for i, subkey in enumerate(df_key):
                data = vars[cdf_key][...][:, i]
                data = _fillval_nan(data, fillval)
                data_dict[subkey] = data
        else:
            # If ndims is 1, we just have a single column of data
            # If ndims is 2, have multiple columns of data under same key
            # If ndims is 3, have multiple columns of data under same key, with 2 sub_keys (e.g., energy and pitch-angle)
            key_shape = vars[cdf_key].shape
            ndims = len(key_shape)
            if ndims == 1:
                data = vars[cdf_key][...]
                data = _fillval_nan(data, fillval)
                data_dict[df_key] = data
            elif ndims == 2:
                for i in range(key_shape[1]):
                    data = vars[cdf_key][...][:, i]
                    data = _fillval_nan(data, fillval)
                    data_dict[f'{df_key}_{i}'] = data
            elif ndims == 3:
                for i in range(key_shape[2]):
                    for j in range(key_shape[1]): 
                       data = vars[cdf_key][...][:, j, i]
                       data = _fillval_nan(data, fillval)
                       data_dict[f'{df_key}_E{i}_P{j}'] = data

    return pd.DataFrame(index=index, data=data_dict)

def _get_cdf_vars(cdf):
    # Get list of all the variables in an open CDF file
    var_list = []
    cdf_info = cdf.cdf_info()
    for attr in list(cdf_info.keys()):
        if 'variable' in attr.lower() and len(cdf_info[attr]) > 0:
            for var in cdf_info[attr]:
                var_list += [var]

    return var_list


def _fillval_nan(data, fillval):
    try:
        data[data == fillval] = np.nan
    except ValueError:
        # This happens if we try and assign a NaN to an int type
        pass
    return data


def wind3dp_download(dataset, starttime, endtime, path=None):
    trange = a.Time(starttime, endtime)
    cda_dataset = a.cdaweb.Dataset(dataset)
    result = Fido.search(trange, cda_dataset)
    downloaded_files = Fido.fetch(result) # use Fido.fetch(result, path='/ThisIs/MyPath/to/Data/{file}') to use a specific local folder for saving data files
    downloaded_files.sort()
    return downloaded_files


def _wind3dp_load(files, resample="1min"):
    if isinstance(resample, str):
        try:
            _ = pd.Timedelta(resample)
        except ValueError:
            raise Warning(f"Your 'resample' option of [{resample}] doesn't seem to be a proper Pandas frequency!") 
    try:
        # read 0th cdf file
        cdf = cdflib.CDF(files[0])
        df = _cdf2df_3d(cdf, "Epoch")

        # read additional cdf files
        if len(files) > 1:
            for f in files[1:]:
                cdf = cdflib.CDF(f)
                t_df = _cdf2df_3d(cdf, "Epoch")
                df = pd.concat([df, t_df])
        if isinstance(resample, str):
            df = df.resample(resample).mean()
            df.index = df.index + pd.tseries.frequencies.to_offset(pd.Timedelta(resample)/2)
        return df
    except:
        raise Exception(f"Problem while loading CDF file! Delete downloaded file(s) {files} and try again. Sometimes this is enogh to solve the problem.") 


def wind3dp_load(dataset, starttime, endtime, resample="1min", multi_index=True):
    files = wind3dp_download(dataset, starttime, endtime)
    df = _wind3dp_load(files, resample)

    # create multi-index data frame of flux
    if multi_index:
        if dataset == 'WI_SFPD_3DP' or dataset == 'WI_SOPD_3DP':
            no_channels = len(df[df.columns[df.columns.str.startswith("ENERGY")]].columns)
            t_df = [''] * no_channels
            multi_keys = np.append( 
                                   [f"FLUX_E{i}" for i in range(no_channels)],
                                   df.drop(df.columns[df.columns.str.startswith(f"FLUX_")], axis=1).columns,
                                   )
            for i in range(no_channels):
                t_df[i] = df[df.columns[df.columns.str.startswith(f"FLUX_E{i}")]]
            t_df.extend([df[col] for col in df.drop(df.columns[df.columns.str.startswith(f"FLUX_")], axis=1).columns.values])
            df = pd.concat(t_df, axis=1, keys=multi_keys)
        else:
            print('')
            print('Multi-index function only available (and necessary) for pitch-angle resolved fluxes. Skipping.')
    return df
        

"""
def wind3dp_load_single(file):
    cdf = cdflib.CDF(file)
    df = _cdf2df_3d(cdf, "Epoch")
    df = df.resample("60s").mean()
    df.index = df.index + pd.tseries.frequencies.to_offset("30s")
    return df


def wind3dp_load(dataset, starttime, endtime, resample="1min"):
    files = wind3dp_download(dataset, starttime, endtime)
    df = _wind3dp_load(files, resample)
    return df
"""


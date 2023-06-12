# Module for loading the data and extracting features
# © Johann Benerradi

import mne
import numpy as np
import os
import pandas as pd
import pickle
import scipy.io.wavfile as wf

from scipy import signal


CUTOFF = [1, None]  # Hz


def get_dfs():
    """
    Load all the JSON data files as DataFrames.

    Returns
    -------
    dfs : list of DataFrames
        Data loaded as DataFrames.
    """
    dfs = []
    for file in os.listdir("../dataset/"):
        if file.endswith(".json"):
            dfs.append(pd.read_json(f"../dataset/{file}"))
    return dfs


def get_eda(df):
    """
    Get the EDA data from a DataFrame of JSON data.

    Parameters
    ----------
    df : DataFrame
        DataFrame of JSON data.

    Returns
    -------
    array : array of shape (1 channel, n_times)
        EDA data of the DataFrame.
    """
    array = np.empty(0)
    for _, r in df.iterrows():
        array = np.append(array, r['hardware']['bitalino'])
    return array[np.newaxis, :]


def get_eeg(df):
    """
    Get the EEG data from a DataFrame of JSON data.

    Parameters
    ----------
    df : DataFrame
        DataFrame of JSON data.

    Returns
    -------
    array : array of shape (4 channels (T3, T4, O1, O2), n_times)
        EEG data of the DataFrame.
    """
    array = np.empty((4, 0))
    keys = ['eeg-T3', 'eeg-T4', 'eeg-O1', 'eeg-O2']
    for _, r in df.iterrows():
        values = [[r['hardware']['brainbit'][ch]] for ch in keys]
        array = np.append(array, values, axis=1)
    ch_names = [ch.split('-')[1] for ch in keys]
    ch_types = [ch.split('-')[0] for ch in keys]
    info = mne.create_info(ch_names=ch_names, sfreq=10.0, ch_types=ch_types)
    raw = mne.io.RawArray(array, info)
    iir_params = dict(order=4, ftype='butter', output='sos')
    raw.filter(*CUTOFF, method='iir', iir_params=iir_params, verbose=False)
    # TODO: adapt filtering to match online (epochs instead of raw)
    return raw.get_data()


def get_core(df):
    """
    Get the core position data from a DataFrame of JSON data.

    Parameters
    ----------
    df : DataFrame
        DataFrame of JSON data.

    Returns
    -------
    array : array of shape (2 channels (x, y), n_times)
        Core positon data of the DataFrame.
    """
    array = np.empty((2, 0))
    keys = ['r_shoudler', 'l_shoudler']
    for _, r in df.iterrows():
        core_x = np.mean([r['hardware']['skeleton'][k]['x'] for k in keys])
        core_y = np.mean([r['hardware']['skeleton'][k]['x'] for k in keys])
        values = [[core_x], [core_y]]
        array = np.append(array, values, axis=1)
    return array


def get_flow(df):
    """
    Get the flow data from a DataFrame of JSON data.

    Parameters
    ----------
    df : DataFrame
        DataFrame of JSON data.

    Returns
    -------
    array : array of shape (1 channels, n_times)
        Flow data of the DataFrame.
    """
    array = df['flow'].values
    # Replace nan by mean on the session
    array[np.isnan(array)] = np.nanmean(array)
    return array[np.newaxis, :]


def get_audio(df):
    audio_name = '_'.join(df['session'][0]['name'].split('_')[:-1])
    audio_path = f'../dataset/{audio_name}.wav'
    print(audio_path)
    rate, data = wf.read(audio_path)

    # Convert stereo to mono
    data = data.mean(axis=1)

    # Get envelope of audio signal
    hb_data = signal.hilbert(data)
    envolope = np.abs(hb_data)
    num = int(len(envolope)/rate*10.0)
    envolope = signal.resample(envolope, num)
    return envolope[np.newaxis, :]


def get_all(feature_name, tslide):
    """
    Get the feature data from a DataFrame of JSON data and save it in a folder.

    Parameters
    ----------
    feature_name : string
        Name of the feature to use. Can be `'eda'`, `'eeg'`, `'core'`, `'flow'`
        or `'audio'`.

    tslide : float
        Length of the sliding window (in seconds).

    Returns
    -------
    all_feature : array of shape (n_windows, n_channels, n_times)
        All the feature data of the dataset, segmented in time windows of
        duration `tslide` seconds.
    """
    sfreq = 10.0  # Hz
    sliding_size = int(tslide * sfreq)
    checkpoint_folder = '../checkpoints/'
    checkpoint_file = f'{checkpoint_folder}all_{feature_name}.pickle'

    if os.path.isfile(checkpoint_file):
        print('Checkpoint found, loading...')
        with open(checkpoint_file, 'rb') as f:
            all_feature = pickle.load(f)
        print('Done!')

    else:
        dfs = get_dfs()
        all_feature = None

        # Loop over all files
        for df in dfs:
            feature = None
            if feature_name == 'eda':
                feature = get_eda(df)
            elif feature_name == 'eeg':
                feature = get_eeg(df)
            elif feature_name == 'core':
                feature = get_core(df)
            elif feature_name == 'flow':
                feature = get_flow(df)
            elif feature_name == 'audio':
                feature = get_audio(df)

            # Create sliding window
            r = feature.shape[-1] % sliding_size
            if r > 0:
                feature = feature[:, :-r]  # crop to fit window size
            feature = feature.reshape(feature.shape[0], -1, sliding_size)
            feature = feature.swapaxes(0, 1)
            if all_feature is None:
                all_feature = feature
            else:
                all_feature = np.append(all_feature, feature, axis=0)
        print(all_feature.shape)

        if not os.path.isdir(checkpoint_folder):
            os.mkdir(checkpoint_folder)
        with open(checkpoint_file, 'wb') as f:
            pickle.dump(all_feature, f)
        print('Checkpoint saved!')

    return all_feature


if __name__ == '__main__':
    all_eda = get_all('eda', 5.0)
    all_eeg = get_all('eeg', 5.0)
    all_core = get_all('core', 5.0)
    all_flow = get_all('flow', 5.0)
    all_env = get_all('audio', 5.0)

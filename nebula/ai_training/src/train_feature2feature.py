# Main script for training the AI Factory
# © Johann Benerradi

import matplotlib.pyplot as plt
import numpy as np
import os
import pickle
import torch
import torch.nn as nn
import torch.optim as optim

from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader

from dl import DatasetFromNumPy, Hourglass
from load import get_all


TSLIDE = 5  # sec


def scaler(name, f_train, f_test):
    maxs = f_train.max(axis=(0, 2))
    mins = f_train.min(axis=(0, 2))

    if name is not None:
        checkpoint_folder = '../../models/'
        if not os.path.isdir(checkpoint_folder):
            os.mkdir(checkpoint_folder)
        checkpoint_file = f'{checkpoint_folder}{name}_minmax.pickle'
        with open(checkpoint_file, 'wb') as f:
            pickle.dump([mins, maxs], f)

    maxs = maxs[np.newaxis, :, np.newaxis]
    mins = mins[np.newaxis, :, np.newaxis]
    f_train = (f_train - mins) / (maxs - mins)
    f_test = (f_test - mins) / (maxs - mins)
    return f_train, f_test


def train_feature2feature(feature_in_name, feature_out_name, lr,
                          n_epochs=50, batch_size=4):
    """
    Train deep learning model to predict a feature from another and save it
    along with the validation MSE loss graph.

    Parameters
    ----------
    feature_in : string
        Feature to use as predictor. Can be `'eda'`, `'eeg'`, `'core'`,
        `'flow'` or `'audio'`.

    feature_out : string
        Feature to predict. Can be `'eda'`, `'eeg'`, `'core'`, `'flow'` or
        `'audio'`.

    lr : float
        Learning rate of the Adam optimiser.

    n_epochs : integer
        Number of epochs for the deep learning training.

    batch_size : integer
        Batch size to use for the deep learning training.
    """

    # Load feature
    model_name = f'{feature_in_name}2{feature_out_name}'
    print(model_name)
    feature_in = get_all(feature_in_name, TSLIDE)
    feature_out = get_all(feature_out_name, TSLIDE)

    # Split based on indices of the smallest data sample between feature in and
    # feature out. This is because all features have the same starting point
    # but some have an earlier end point (eg. audio).
    min_sample_size = min(feature_in.shape[0], feature_out.shape[0])
    split = train_test_split(range(min_sample_size), test_size=0.25)

    # Split dataset
    f_in_train, f_in_test = feature_in[split[0]], feature_in[split[1]]
    f_out_train, f_out_test = feature_out[split[0]], feature_out[split[1]]
    print(f_in_train.shape, f_in_test.shape)
    print(f_out_train.shape, f_out_test.shape)

    # Min-max scaling
    f_in_train, f_in_test = scaler(model_name, f_in_train, f_in_test)
    f_out_train, f_out_test = scaler(None, f_out_train, f_out_test)

    # Load training set
    dataset_train = DatasetFromNumPy(f_in_train, f_out_train)
    train_loader = DataLoader(dataset=dataset_train, batch_size=batch_size,
                              shuffle=True)
    # Load validation set
    datanirs_val = DatasetFromNumPy(f_in_test, f_out_test)
    val_loader = DataLoader(dataset=datanirs_val, batch_size=batch_size,
                            shuffle=False)

    # Instantiate models and hyperparameters
    hourglass = Hourglass(feature_in.shape[1], feature_out.shape[1]).double()
    criterion = nn.MSELoss()
    params = list(hourglass.parameters())
    optimizer = optim.Adam(params, lr=lr)

    perfs = []
    for epoch in range(n_epochs):
        print(f"Epoch number: {epoch}")
        # TRAINING
        hourglass.train()
        for data in train_loader:
            # Get the inputs
            x, y = data

            # Zero the parameter gradients
            optimizer.zero_grad()

            # Forward + backward + optimize
            pred = hourglass(x)
            loss = criterion(pred, y)
            loss.backward()
            optimizer.step()

        # VALIDATION
        hourglass.eval()
        with torch.no_grad():
            validation_loss = 0.0
            for i, data in enumerate(val_loader, 0):
                x, y = data
                pred = hourglass(x)
                loss = criterion(pred, y)
                validation_loss += loss.item()
            perf = validation_loss / (i+1)
            perfs.append(perf)

    # Make checkpoint folder
    checkpoint_folder = '../../models/'
    if not os.path.isdir(checkpoint_folder):
        os.mkdir(checkpoint_folder)
    file_path = f'{checkpoint_folder}{model_name}'

    # Plot loss
    fig, ax = plt.subplots(figsize=(6, 5))
    fig.suptitle(f"lr={lr}, n_epochs={n_epochs}, batch_size={batch_size}")
    ax.set(xlabel="Epoch", ylabel="Loss")
    ax.plot(perfs)
    plt.savefig(f'./{model_name}.png')

    # Save model
    torch.save(hourglass.state_dict(), f'{file_path}.pt')


if __name__ == '__main__':
    # 1. For live EEG -> flow
    train_feature2feature('eeg', 'flow', 0.00001, n_epochs=500, batch_size=32)

    # 2. For predicted flow -> core (current_nnet_x_y_z)
    train_feature2feature('flow', 'core', 0.00001, n_epochs=200, batch_size=4)

    # 3. For robot position (current_robot_x_y_z) -> flow
    train_feature2feature('core', 'flow', 0.00001, n_epochs=80, batch_size=4)

    # 4. For live sound (amplitude) -> robot position (current_robot_x_y_z)
    train_feature2feature('audio', 'core', 0.00005, n_epochs=100, batch_size=16)

    # 5. For live sound (amplitude) -> flow
    train_feature2feature('audio', 'flow', 0.0001, n_epochs=30, batch_size=4)

    # 6. For predicted flow -> sound (amplitude)
    train_feature2feature('flow', 'audio', 0.0001, n_epochs=30, batch_size=4)

    # 7. For live EDA -> flow
    train_feature2feature('eda', 'flow', 0.00001, n_epochs=80, batch_size=16)

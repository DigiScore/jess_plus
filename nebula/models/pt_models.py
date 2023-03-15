import torch.nn as nn
import torch.nn.functional as F


class Hourglass(nn.Module):

    def __init__(self, n_ch_in, n_ch_out):
        super(Hourglass, self).__init__()
        # Encoder
        self.conv1 = nn.Conv1d(n_ch_in, 8, kernel_size=5, stride=3)
        self.bn1 = nn.BatchNorm1d(8)
        self.fc1 = nn.Linear(128, 32)
        # Decoder
        self.fc2 = nn.Linear(32, 128)
        self.tconv1 = nn.ConvTranspose1d(8, n_ch_out, kernel_size=5, stride=3)

    def forward(self, x):
        batch_size = x.size(0)
        # Encode
        x = F.relu(self.bn1(self.conv1(x)))
        x = x.view(batch_size, -1)  # flatten
        x = F.relu(self.fc1(x))
        # Decode
        x = F.relu(self.fc2(x))
        x = x.view(batch_size, 8, -1)  # un-flatten
        x = self.tconv1(x)
        return x

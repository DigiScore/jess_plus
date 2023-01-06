import argparse
import time

from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels
from brainflow.data_filter import DataFilter
from brainflow.ml_model import MLModel, BrainFlowMetrics, BrainFlowClassifiers, BrainFlowModelParams


def main():
    BoardShim.enable_board_logger()
    DataFilter.enable_data_logger()
    MLModel.enable_ml_logger()

    params = BrainFlowInputParams()

    board = BoardShim(7, params)
    master_board_id = board.get_board_id()
    sampling_rate = BoardShim.get_sampling_rate(master_board_id)
    board.prepare_session()
    board.start_stream(45000)
    BoardShim.log_message(LogLevels.LEVEL_INFO.value, 'start sleeping in the main thread')
    time.sleep(5)  # recommended window size for eeg metric calculation is at least 4 seconds, bigger is better
    # data = board.get_board_data()
    # board.stop_stream()
    # board.release_session()

    while True:
        data = board.get_board_data()

        eeg_channels = BoardShim.get_eeg_channels(int(master_board_id))
        bands = DataFilter.get_avg_band_powers(data, eeg_channels, sampling_rate, True)
        feature_vector = bands[0]
        print(feature_vector)

        mindfulness_params = BrainFlowModelParams(BrainFlowMetrics.MINDFULNESS.value,
                                                  BrainFlowClassifiers.DEFAULT_CLASSIFIER.value)
        mindfulness = MLModel(mindfulness_params)
        mindfulness.prepare()
        print('Mindfulness: %s' % str(mindfulness.predict(feature_vector)))
        mindfulness.release()

        restfulness_params = BrainFlowModelParams(BrainFlowMetrics.RESTFULNESS.value,
                                                  BrainFlowClassifiers.DEFAULT_CLASSIFIER.value)
        restfulness = MLModel(restfulness_params)
        restfulness.prepare()
        print('Restfulness: %s' % str(restfulness.predict(feature_vector)))
        restfulness.release()
        time.sleep(2)

if __name__ == "__main__":
    main()

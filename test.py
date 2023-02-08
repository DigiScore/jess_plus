from nebula.nebula_dataclass import DataBorg


b1 = DataBorg()

b2 = DataBorg()

b3 = DataBorg()

print(b1.move_rnn)

b2.move_rnn = 2

print(b1.move_rnn)

b3.move_rnn = 12345

print(b1.move_rnn, b2.move_rnn, b3.move_rnn)

b4 = DataBorg()

b4.move_rnn = 5678

print(b1.move_rnn, b2.move_rnn, b3.move_rnn)

b4.randomiser()

print(b1.move_rnn, b2.move_rnn, b3.move_rnn)









#
# import argparse
# import time
#
# from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels
# from brainflow.data_filter import DataFilter
# from brainflow.ml_model import MLModel, BrainFlowMetrics, BrainFlowClassifiers, BrainFlowModelParams
# import logging
#
# import pyqtgraph as pg
# from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
# from brainflow.data_filter import DataFilter, FilterTypes, DetrendOperations
# from pyqtgraph.Qt import QtGui, QtCore
#
#
# class Graph:
#     def __init__(self, board_shim):
#         self.board_id = board_shim.get_board_id()
#         self.board_shim = board_shim
#         self.exg_channels = BoardShim.get_exg_channels(self.board_id)
#         self.sampling_rate = BoardShim.get_sampling_rate(self.board_id)
#         self.update_speed_ms = 50
#         self.window_size = 4
#         self.num_points = self.window_size * self.sampling_rate
#
#         self.app = QtGui.QApplication([])
#         self.win = pg.GraphicsWindow(title='BrainFlow Plot', size=(800, 600))
#
#         self._init_timeseries()
#
#         timer = QtCore.QTimer()
#         timer.timeout.connect(self.update)
#         timer.start(self.update_speed_ms)
#         QtGui.QApplication.instance().exec_()
#
#     def _init_timeseries(self):
#         self.plots = list()
#         self.curves = list()
#         for i in range(len(self.exg_channels)):
#             p = self.win.addPlot(row=i, col=0)
#             p.showAxis('left', False)
#             p.setMenuEnabled('left', False)
#             p.showAxis('bottom', False)
#             p.setMenuEnabled('bottom', False)
#             if i == 0:
#                 p.setTitle('TimeSeries Plot')
#             self.plots.append(p)
#             curve = p.plot()
#             self.curves.append(curve)
#
#     def update(self):
#         data = self.board_shim.get_current_board_data(self.num_points)
#         # print(len(data))
#         for count, channel in enumerate(self.exg_channels):
#             # plot timeseries
#             DataFilter.detrend(data[channel], DetrendOperations.CONSTANT.value)
#             DataFilter.perform_bandpass(data[channel], self.sampling_rate, 3.0, 45.0, 2,
#                                         FilterTypes.BUTTERWORTH.value, 0)
#             DataFilter.perform_bandstop(data[channel], self.sampling_rate, 48.0, 52.0, 2,
#                                         FilterTypes.BUTTERWORTH.value, 0)
#             DataFilter.perform_bandstop(data[channel], self.sampling_rate, 58.0, 62.0, 2,
#                                         FilterTypes.BUTTERWORTH.value, 0)
#             self.curves[count].setData(data[channel].tolist())
#
#         self.app.processEvents()
#
#
# def main():
#     BoardShim.enable_dev_board_logger()
#
#     params = BrainFlowInputParams()
#
#     # try:
#     board_shim = BoardShim(7, params)
#     board_shim.prepare_session()
#     board_shim.start_stream(450000)
#     Graph(board_shim)
#     # except BaseException:
#     #     logging.warning('Exception', exc_info=True)
#     # finally:
#     #     print("EEENNNNNEENENNNNDDDDDDD")
#     #     logging.info('End')
#     #     if board_shim.is_prepared():
#     #         logging.info('Releasing session')
#     #         board_shim.release_session()
#
#
# if __name__ == '__main__':
#     main()
# # #
# # # def main():
# # #     BoardShim.enable_board_logger()
# # #     DataFilter.enable_data_logger()
# # #     MLModel.enable_ml_logger()
# # #
# # #     params = BrainFlowInputParams()
# # #
# # #     board = BoardShim(7, params)
# # #     master_board_id = board.get_board_id()
# # #     sampling_rate = BoardShim.get_sampling_rate(master_board_id)
# # #     board.prepare_session()
# # #     board.start_stream(45000)
# # #     BoardShim.log_message(LogLevels.LEVEL_INFO.value, 'start sleeping in the main thread')
# # #     time.sleep(5)  # recommended window size for eeg_board metric calculation is at least 4 seconds, bigger is better
# # #     # data = board.get_board_data()
# # #     # board.stop_stream()
# # #     # board.release_session()
# # #
# # #     while True:
# # #         data = board.get_board_data()
# # #
# # #         eeg_channels = BoardShim.get_eeg_channels(int(master_board_id))
# # #         bands = DataFilter.get_avg_band_powers(data, eeg_channels, sampling_rate, True)
# # #         feature_vector = bands[0]
# # #         print(feature_vector)
# # #
# # #         mindfulness_params = BrainFlowModelParams(BrainFlowMetrics.MINDFULNESS.value,
# # #                                                   BrainFlowClassifiers.DEFAULT_CLASSIFIER.value)
# # #         mindfulness = MLModel(mindfulness_params)
# # #         mindfulness.prepare()
# # #         print('Mindfulness: %s' % str(mindfulness.predict(feature_vector)))
# # #         mindfulness.release()
# # #
# # #         restfulness_params = BrainFlowModelParams(BrainFlowMetrics.RESTFULNESS.value,
# # #                                                   BrainFlowClassifiers.DEFAULT_CLASSIFIER.value)
# # #         restfulness = MLModel(restfulness_params)
# # #         restfulness.prepare()
# # #         print('Restfulness: %s' % str(restfulness.predict(feature_vector)))
# # #         restfulness.release()
# # #         time.sleep(2)
# # #
# # # if __name__ == "__main__":
# # #     main()

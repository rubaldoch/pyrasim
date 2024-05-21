#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: SFCW Signal Generator
# Author: Roosevelt Ubaldo based on previous implementations
# Description: Generates a CW signal, TX and RX thorugh USRP, and send by ZMQ server to posprocessing.
# GNU Radio version: 3.10.1.1

from packaging.version import Version as StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

from PyQt5 import Qt
from PyQt5.QtCore import QObject, pyqtSlot
from gnuradio import analog
from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import zeromq
from gnuradio.qtgui import Range, RangeWidget
from PyQt5 import QtCore
from xmlrpc.server import SimpleXMLRPCServer
import threading
import math



from gnuradio import qtgui

class sfcw_signal_generator_simul(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "SFCW Signal Generator", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("SFCW Signal Generator")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "sfcw_signal_generator_simul")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Variables
        ##################################################
        self.light_speed = light_speed = 2.998e3
        self.baseband_freq = baseband_freq = 1e3
        self.zmq_server_port = zmq_server_port = 8082
        self.xmlrpc_server_port = xmlrpc_server_port = 8080
        self.wave_type = wave_type = 1
        self.wave_length = wave_length = (light_speed/baseband_freq)
        self.usrpDevice = usrpDevice = "serial=310C4C0"
        self.tx_gain = tx_gain = 10
        self.timestamp = timestamp = 0
        self.target_speed = target_speed = 0
        self.target_range = target_range = 1
        self.samp_rate = samp_rate = 0.2e6
        self.rx_gain = rx_gain = 10
        self.rcs = rcs = math.pi
        self.noise_amp = noise_amp = 0
        self.n_points = n_points = 1024
        self.n_channels = n_channels = 2
        self.loss = loss = 0.01
        self.center_freq = center_freq = 3.0e9

        ##################################################
        # Blocks
        ##################################################
        # Create the options list
        self._wave_type_options = [0, 1]
        # Create the labels list
        self._wave_type_labels = ['Constant Wave', 'Sine Wave']
        # Create the combo box
        self._wave_type_tool_bar = Qt.QToolBar(self)
        self._wave_type_tool_bar.addWidget(Qt.QLabel("Waveform Type" + ": "))
        self._wave_type_combo_box = Qt.QComboBox()
        self._wave_type_tool_bar.addWidget(self._wave_type_combo_box)
        for _label in self._wave_type_labels: self._wave_type_combo_box.addItem(_label)
        self._wave_type_callback = lambda i: Qt.QMetaObject.invokeMethod(self._wave_type_combo_box, "setCurrentIndex", Qt.Q_ARG("int", self._wave_type_options.index(i)))
        self._wave_type_callback(self.wave_type)
        self._wave_type_combo_box.currentIndexChanged.connect(
            lambda i: self.set_wave_type(self._wave_type_options[i]))
        # Create the radio buttons
        self.top_layout.addWidget(self._wave_type_tool_bar)
        self._tx_gain_range = Range(0, 76, 1, 10, 200)
        self._tx_gain_win = RangeWidget(self._tx_gain_range, self.set_tx_gain, "Transmission Gain", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._tx_gain_win)
        self._timestamp_range = Range(0, 200, 1, 0, 200)
        self._timestamp_win = RangeWidget(self._timestamp_range, self.set_timestamp, "Timestamp", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._timestamp_win)
        self._target_speed_range = Range(-100, 100, 1, 0, 200)
        self._target_speed_win = RangeWidget(self._target_speed_range, self.set_target_speed, "Target Speed", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._target_speed_win)
        self._target_range_range = Range(1, 100, 1, 1, 200)
        self._target_range_win = RangeWidget(self._target_range_range, self.set_target_range, "Target Range", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._target_range_win)
        self._samp_rate_range = Range(0.2e6, 50e6, 1e6, 0.2e6, 200)
        self._samp_rate_win = RangeWidget(self._samp_rate_range, self.set_samp_rate, "Sample Rate", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._samp_rate_win)
        self._rx_gain_range = Range(0, 76, 1, 10, 200)
        self._rx_gain_win = RangeWidget(self._rx_gain_range, self.set_rx_gain, "Reception Gain", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._rx_gain_win)
        self._noise_amp_range = Range(0, 1, 0.01, 0, 200)
        self._noise_amp_win = RangeWidget(self._noise_amp_range, self.set_noise_amp, "Noise Level", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._noise_amp_win)
        self._loss_range = Range(0, 1, 0.01, 0.01, 200)
        self._loss_win = RangeWidget(self._loss_range, self.set_loss, "Loss (media and system)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._loss_win)
        self._baseband_freq_range = Range(1e3, 1e5, 1e3, 1e3, 200)
        self._baseband_freq_win = RangeWidget(self._baseband_freq_range, self.set_baseband_freq, "Baseband Frequency", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._baseband_freq_win)
        self.zeromq_pub_sink_0_0 = zeromq.pub_sink(gr.sizeof_gr_complex, n_channels*n_points, f"tcp://127.0.0.1:{zmq_server_port}", 100, False, -1, '')
        self.xmlrpc_server_0_0 = SimpleXMLRPCServer(('127.0.0.1', xmlrpc_server_port), allow_none=True)
        self.xmlrpc_server_0_0.register_instance(self)
        self.xmlrpc_server_0_0_thread = threading.Thread(target=self.xmlrpc_server_0_0.serve_forever)
        self.xmlrpc_server_0_0_thread.daemon = True
        self.xmlrpc_server_0_0_thread.start()
        self.blocks_throttle_0_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)
        self.blocks_stream_to_vector_0_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, n_channels*n_points)
        self.blocks_selector_0_0 = blocks.selector(gr.sizeof_gr_complex*1,wave_type,0)
        self.blocks_selector_0_0.set_enabled(True)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.blocks_interleave_0 = blocks.interleave(gr.sizeof_gr_complex*1, 1)
        self.blocks_delay_0 = blocks.delay(gr.sizeof_gr_complex*1, int(samp_rate*2*(target_range -target_speed*timestamp)/light_speed))
        self.blocks_add_xx_0 = blocks.add_vcc(1)
        self.analog_sig_source_x_0_0_0 = analog.sig_source_c(samp_rate, analog.GR_SIN_WAVE, baseband_freq, 1, 0, 0)
        self.analog_sig_source_x_0_0 = analog.sig_source_c(samp_rate, analog.GR_CONST_WAVE, baseband_freq, 1, 0, 0)
        self.analog_noise_source_x_0 = analog.noise_source_c(analog.GR_GAUSSIAN, noise_amp, 0)
        self.analog_const_source_x_0 = analog.sig_source_c(0, analog.GR_CONST_WAVE, 0, 0, rcs*(tx_gain*rx_gain*pow(wave_length,2)*loss)/(pow(4*math.pi,3)*pow(target_range,4)))


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_const_source_x_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.analog_noise_source_x_0, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.analog_sig_source_x_0_0, 0), (self.blocks_throttle_0, 0))
        self.connect((self.analog_sig_source_x_0_0_0, 0), (self.blocks_throttle_0_0, 0))
        self.connect((self.blocks_add_xx_0, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.blocks_delay_0, 0), (self.blocks_interleave_0, 1))
        self.connect((self.blocks_interleave_0, 0), (self.blocks_stream_to_vector_0_0, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self.blocks_delay_0, 0))
        self.connect((self.blocks_selector_0_0, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.blocks_selector_0_0, 0), (self.blocks_interleave_0, 0))
        self.connect((self.blocks_stream_to_vector_0_0, 0), (self.zeromq_pub_sink_0_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.blocks_selector_0_0, 0))
        self.connect((self.blocks_throttle_0_0, 0), (self.blocks_selector_0_0, 1))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "sfcw_signal_generator_simul")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_light_speed(self):
        return self.light_speed

    def set_light_speed(self, light_speed):
        self.light_speed = light_speed
        self.set_wave_length((self.light_speed/self.baseband_freq))
        self.blocks_delay_0.set_dly(int(self.samp_rate*2*(self.target_range -self.target_speed*self.timestamp)/self.light_speed))

    def get_baseband_freq(self):
        return self.baseband_freq

    def set_baseband_freq(self, baseband_freq):
        self.baseband_freq = baseband_freq
        self.set_wave_length((self.light_speed/self.baseband_freq))
        self.analog_sig_source_x_0_0.set_frequency(self.baseband_freq)
        self.analog_sig_source_x_0_0_0.set_frequency(self.baseband_freq)

    def get_zmq_server_port(self):
        return self.zmq_server_port

    def set_zmq_server_port(self, zmq_server_port):
        self.zmq_server_port = zmq_server_port

    def get_xmlrpc_server_port(self):
        return self.xmlrpc_server_port

    def set_xmlrpc_server_port(self, xmlrpc_server_port):
        self.xmlrpc_server_port = xmlrpc_server_port

    def get_wave_type(self):
        return self.wave_type

    def set_wave_type(self, wave_type):
        self.wave_type = wave_type
        self._wave_type_callback(self.wave_type)
        self.blocks_selector_0_0.set_input_index(self.wave_type)

    def get_wave_length(self):
        return self.wave_length

    def set_wave_length(self, wave_length):
        self.wave_length = wave_length
        self.analog_const_source_x_0.set_offset(self.rcs*(self.tx_gain*self.rx_gain*pow(self.wave_length,2)*self.loss)/(pow(4*math.pi,3)*pow(self.target_range,4)))

    def get_usrpDevice(self):
        return self.usrpDevice

    def set_usrpDevice(self, usrpDevice):
        self.usrpDevice = usrpDevice

    def get_tx_gain(self):
        return self.tx_gain

    def set_tx_gain(self, tx_gain):
        self.tx_gain = tx_gain
        self.analog_const_source_x_0.set_offset(self.rcs*(self.tx_gain*self.rx_gain*pow(self.wave_length,2)*self.loss)/(pow(4*math.pi,3)*pow(self.target_range,4)))

    def get_timestamp(self):
        return self.timestamp

    def set_timestamp(self, timestamp):
        self.timestamp = timestamp
        self.blocks_delay_0.set_dly(int(self.samp_rate*2*(self.target_range -self.target_speed*self.timestamp)/self.light_speed))

    def get_target_speed(self):
        return self.target_speed

    def set_target_speed(self, target_speed):
        self.target_speed = target_speed
        self.blocks_delay_0.set_dly(int(self.samp_rate*2*(self.target_range -self.target_speed*self.timestamp)/self.light_speed))

    def get_target_range(self):
        return self.target_range

    def set_target_range(self, target_range):
        self.target_range = target_range
        self.analog_const_source_x_0.set_offset(self.rcs*(self.tx_gain*self.rx_gain*pow(self.wave_length,2)*self.loss)/(pow(4*math.pi,3)*pow(self.target_range,4)))
        self.blocks_delay_0.set_dly(int(self.samp_rate*2*(self.target_range -self.target_speed*self.timestamp)/self.light_speed))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.analog_sig_source_x_0_0.set_sampling_freq(self.samp_rate)
        self.analog_sig_source_x_0_0_0.set_sampling_freq(self.samp_rate)
        self.blocks_delay_0.set_dly(int(self.samp_rate*2*(self.target_range -self.target_speed*self.timestamp)/self.light_speed))
        self.blocks_throttle_0.set_sample_rate(self.samp_rate)
        self.blocks_throttle_0_0.set_sample_rate(self.samp_rate)

    def get_rx_gain(self):
        return self.rx_gain

    def set_rx_gain(self, rx_gain):
        self.rx_gain = rx_gain
        self.analog_const_source_x_0.set_offset(self.rcs*(self.tx_gain*self.rx_gain*pow(self.wave_length,2)*self.loss)/(pow(4*math.pi,3)*pow(self.target_range,4)))

    def get_rcs(self):
        return self.rcs

    def set_rcs(self, rcs):
        self.rcs = rcs
        self.analog_const_source_x_0.set_offset(self.rcs*(self.tx_gain*self.rx_gain*pow(self.wave_length,2)*self.loss)/(pow(4*math.pi,3)*pow(self.target_range,4)))

    def get_noise_amp(self):
        return self.noise_amp

    def set_noise_amp(self, noise_amp):
        self.noise_amp = noise_amp
        self.analog_noise_source_x_0.set_amplitude(self.noise_amp)

    def get_n_points(self):
        return self.n_points

    def set_n_points(self, n_points):
        self.n_points = n_points

    def get_n_channels(self):
        return self.n_channels

    def set_n_channels(self, n_channels):
        self.n_channels = n_channels

    def get_loss(self):
        return self.loss

    def set_loss(self, loss):
        self.loss = loss
        self.analog_const_source_x_0.set_offset(self.rcs*(self.tx_gain*self.rx_gain*pow(self.wave_length,2)*self.loss)/(pow(4*math.pi,3)*pow(self.target_range,4)))

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq




def main(top_block_cls=sfcw_signal_generator_simul, options=None):

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()

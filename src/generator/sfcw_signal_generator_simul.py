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
from xmlrpc.server import SimpleXMLRPCServer
import threading
import math




class sfcw_signal_generator_simul(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "SFCW Signal Generator", catch_exceptions=True)

        ##################################################
        # Variables
        ##################################################
        self.light_speed = light_speed = 2.998e3
        self.baseband_freq = baseband_freq = 1e3
        self.zmq_server_port = zmq_server_port = 8082
        self.xmlrpc_server_port = xmlrpc_server_port = 8080
        self.wave_type = wave_type = 1
        self.wave_length = wave_length = (light_speed/baseband_freq)
        self.tx_gain = tx_gain = 10
        self.timestamp = timestamp = 0
        self.target_speed = target_speed = 0
        self.target_range = target_range = 1
        self.samp_rate = samp_rate = 200e3
        self.rx_gain = rx_gain = 10
        self.rcs = rcs = math.pi
        self.noise_amp = noise_amp = 0
        self.n_points = n_points = 1024
        self.n_channels = n_channels = 2
        self.loss = loss = 0

        ##################################################
        # Blocks
        ##################################################
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
        self.blocks_selector_0_0.set_input_index(self.wave_type)

    def get_wave_length(self):
        return self.wave_length

    def set_wave_length(self, wave_length):
        self.wave_length = wave_length
        self.analog_const_source_x_0.set_offset(self.rcs*(self.tx_gain*self.rx_gain*pow(self.wave_length,2)*self.loss)/(pow(4*math.pi,3)*pow(self.target_range,4)))

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




def main(top_block_cls=sfcw_signal_generator_simul, options=None):
    tb = top_block_cls()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()

    tb.wait()


if __name__ == '__main__':
    main()

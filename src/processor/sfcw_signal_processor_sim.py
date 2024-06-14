#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import os
import json
from src.processor.constants import LIGHTSPEED
import zmq
import time
import matplotlib.pyplot as plt
from dataclasses import dataclass, field
from src.processor.utils import getSocket, getXmlrpc, psd
import numpy as np
import string
import random

samp_rate = 0.2e6
lo_setting_time = 0.01
n_points_per_channel_zmq = 1024

@dataclass
class SfcwSimulationConfig:
    start_frequency: float = 100e6
    end_frequency: float = None
    step_frequency: float = None
    N: int = None
    name: str = ''
    target_range_start: float = 1.0
    target_range_end: float =  50.0 # field(init=False, repr=False)
    target_range_step: float =  1.0 # field(init=False, repr=False)
    sample_rate: float = field(init=False, repr=False)
    M: int = field(init=False, repr=False)
    

    def __post_init__(self):
        # Adjust frequency to simulator
        self.start_frequency /= 1e5
        if self.end_frequency: self.end_frequency /= 1e5
        if self.step_frequency: self.step_frequency /= 1e5

        if self.N is None:
            bandwith = self.end_frequency - self.start_frequency
            self.N = int(bandwith / self.step_frequency)
        
        if self.end_frequency is None:
            self.end_frequency = self.start_frequency + self.N * self.step_frequency
        
        if self.step_frequency is None:
            self.step_frequency = round((self.end_frequency - self.start_frequency) / self.N, 2)

        self.sample_rate = self.end_frequency * 10
        if self.name == '':
            self.name = ''.join(random.choices(string.ascii_letters, k=6))
            self.name = f"test-{self.name}"
       
        self.M = int(2**np.ceil(np.log2(self.end_frequency/self.step_frequency)))
        # self.target_range_end = self.max_unambiguos_range/2
        # self.target_range_step = self.range_resolution

    @property
    def max_unambiguos_range(self):
        return round(LIGHTSPEED/(2* self.step_frequency),2)
    
    @property
    def range_resolution(self):
        return round(LIGHTSPEED/(2* self.N * self.step_frequency), 2)

    def print_info(self):
        print(f"===========================================")
        print(f"Max unambiguos range: {self.max_unambiguos_range} m")
        print(f"Range resolution: {self.range_resolution} m")

def change_variable(xmlrpc_function, value, retry_seconds=1):
    try:
        xmlrpc_function(round(value, 2))
        time.sleep(lo_setting_time)
    except:
        print(f"XMLRPC server is down. Trying again in {retry_seconds} s")
        time.sleep(retry_seconds)
        change_variable(xmlrpc_function, value, retry_seconds + 1)

def preprocess_data(buffer,  filename=None):
    """Pre-process raw data.

    This function gets a filename, loads the data 
    and reshape it to obtain the reference and
    measurement data.

    Args:
        filename (str) : path to the file.
        n_pts_per_chan (int) : Number of points per channel.

    Returns:
        ndarray for ``reference`` and ``measurement`` channel.
    """
    data = np.frombuffer(buffer, dtype=np.complex64, count=n_points_per_channel_zmq*2)

    if filename:
        data.tofile(filename)

    """
        Data is received interleaved [a,b,a,b,a,b,...]
        this is why we need to reshape according to channel number into
        [[a, b], 
        [a, b],
        [a, b], ...
        ]
    """

    data = data.reshape(n_points_per_channel_zmq, 2)
    data = data.T

    # split into reference (ref) and measurement channel (meas)
    ref_data = data[0]
    meas_data = data[1]
    return ref_data, meas_data



def get_frequency(data, sample_rate):
    y_psd = psd(data.size, data)
    x_freq = np.fft.fftfreq(data.size, 1 / sample_rate)
    idx_max = np.argmax(y_psd)
    return round(x_freq[idx_max], 2)


def sfcw_signal_processor(config: SfcwSimulationConfig, verbose:bool=True):

    results = []
    # Init functions
    xmlrpc = getXmlrpc()

    change_variable(xmlrpc.set_n_points, n_points_per_channel_zmq)
    change_variable(xmlrpc.set_samp_rate, config.sample_rate)

    if verbose: config.print_info()

    target_range = config.target_range_start
    while target_range <= config.target_range_end:
        if verbose:
                print("+++++++++++++++++++++++++++++++++++++++++++")
                print(f"Current range: {target_range}\n")

        change_variable(xmlrpc.set_target_range, target_range)
        V_pos = np.zeros(config.M, dtype=np.complex64) # *2 to consider positive and negatives values

        current_frequency = config.start_frequency
        idx = int(current_frequency / config.step_frequency)

        while current_frequency < config.end_frequency:
            if verbose: print(f"Current frequency {idx}: {current_frequency}")

            change_variable(xmlrpc.set_baseband_freq, current_frequency)

            # Retrieve data
            time.sleep(1) 
            socket = getSocket()
                       # Time sleep to start collecting data

            while socket.poll(10) == 0: pass

            msg = socket.recv(flags=zmq.NOBLOCK)
            reference_data, measurement_data = preprocess_data(msg)            
            if verbose: print(f"Received frequency: {get_frequency(reference_data, config.sample_rate)}\n")
        
            sample_value_index = reference_data.size // 2
            # sample_value = np.angle(measurement_data[sample_value_index]/reference_data[sample_value_index])
            sample_value = measurement_data[sample_value_index]/reference_data[sample_value_index]
            
            V_pos[idx] = sample_value
                
            socket.close()
            current_frequency += config.step_frequency
            idx += 1
        
        V_neg = np.flip(V_pos[1:])
        V = np.concatenate((V_pos, V_neg))
        y_m2 = np.abs(np.fft.ifft(V_pos))
        x_m2 = np.linspace(0, y_m2.size - 1, y_m2.size)
        x_m2 = x_m2*LIGHTSPEED/(2*y_m2.size*config.step_frequency)
        results.append({
            'expected': target_range, 
            'predicted': x_m2[np.argmax(y_m2)],
            })
    
        target_range += config.target_range_step  

    return results
import numpy as np
import numpy.typing as npt
import matplotlib.pyplot as plt
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Union, List

DEBUG = 1

@dataclass
class Sinusoid:
    """
    Base class to represent a Sinusoid

    x(n) = A cos(2πfn + θ); n = -inf, ... , inf
    
    Sinusoid = np.real(ComplexSinusoid)
    """

    amplitude: float = 1
    frequency: float = 10
    phase: float = 0
    
    # Properties
    @property
    def angular_frequency(self) -> float:
        return 2 * np.pi * self.frequency
    

    @property
    def average_power(self):
        """
        Retrieve the average power of the sinusoid

        P = (1.0/N) sum_{n=0}^{N-1}|x(n)|^2

        Reference: Signals and Systems, p. 20.
        """
        period = 1.0/self.frequency
        time_axis = np.arange(0, period-1, 1)
        return (1.0/period)*np.sum(np.power(np.abs(self._sample_amplitudes(time_axis)), 2))
    
    # Methods
    def _sample_amplitudes(self, time_axis: np.array):
        return self.amplitude * np.cos(self.angular_frequency*time_axis + self.phase)


    
    # Operators
    def __add__(self, other):
        if self.frequency == other.frequency:
            A1 = self.amplitude
            A2 = other.amplitude
            theta1 = self.phase
            theta2 = other.phase
            A = np.power(np.power(A1, 2) + np.power(A2, 2)  + 2*A1*A2*np.cos(theta1-theta2), 0.5)
            theta = np.arctan((A1*np.sin(theta1) + A2*np.sin(theta2))/(A1*np.cos(theta1) + A2*np.cos(theta2)))
            return Sinusoid(amplitude=A, frequency=self.frequency, phase=theta)


    # Plotting
    
    def plot(self, sample_rate:int = None):
        """
        Plot one cycle of the sinusoid in time domain using matplolib
        
        Args:
            sample_rate (int): sampling rate for the sinusoid. Default 100 times the frequency
        """

        if sample_rate == None:
            sample_rate = 2 * np.abs(self.frequency) + 1

        time_axis = np.arange(0, np.abs(1.0/self.frequency), 1.0/sample_rate)
        amplitude_axis = self._sample_amplitudes(time_axis)
        
        plt.plot(time_axis, amplitude_axis)
        plt.ylabel("Amplitude")
        plt.xlabel("Time (s)")
        plt.show()

@dataclass
class Waveform(ABC):
    duration: float = 1.0
    time_start: float = 0.0
    sample_rate: int = None

    time_axis: npt.NDArray[np.float_] = field(init=False, repr=False)
    amplitude_axis: npt.NDArray[Union[np.float_, np.complex_]] = field(init=False, repr=False)
    
    # Properties
    @property
    def time_end(self) -> float:
        return self.time_start + self.duration

    def __len__(self):
        return len(self.time_axis)
    
    def __add__(self, other):
        if self.sample_rate == other.sample_rate:
            duration = max(self.time_end, other.time_end) - min(self.time_start, other.time_start)
            add_result = Waveform(
                duration=duration, 
                time_start= min(self.time_start, other.time_start),
                sample_rate= self.sample_rate
                )
            add_result.time_axis = np.arange(0, duration, 1.0/add_result.sample_rate, dtype=np.float_) + add_result.time_start
            add_result.amplitude_axis = np.zeros(len(add_result))

            s_i = np.isclose(add_result.time_axis, self.time_axis[0]).nonzero()[0][0]
            s_j = np.isclose(add_result.time_axis, self.time_axis[-1]).nonzero()[0][0]
            o_i = np.isclose(add_result.time_axis, other.time_axis[0]).nonzero()[0][0]
            o_j = np.isclose(add_result.time_axis, other.time_axis[-1]).nonzero()[0][0]

            if DEBUG:
                print(f"si: {s_i}, sj: {s_j}, oi: {o_i}, oj: {o_j}")
            if (o_i <= s_j and s_i <= o_i):
                """
                ----------------------------
                |           |***n***|       |
                ----------------------------
                s_i        o_i    s_j     o_j
                """
                if DEBUG:
                    print("case 1")
                
                n = s_j - o_i + 1
                o_k = 0                 # starting index in other array
                s_k = len(self) - n     # starting index in self array
                r_k = o_i               # starting index in result array
                # Sum intersection
                while r_k <= min(s_j, o_j):
                    add_result.amplitude_axis[r_k] = self.amplitude_axis[s_k] + other.amplitude_axis[o_k]
                    r_k += 1
                    s_k += 1
                    o_k += 1
                # Left side
                r_k = 0
                s_k = 0
                while r_k < o_i:
                    add_result.amplitude_axis[r_k] = self.amplitude_axis[s_k]
                    r_k += 1
                    s_k += 1
                # Right side
                r_k = min(s_j, o_j) + 1
                o_k = n
                while r_k <= o_j:
                    add_result.amplitude_axis[r_k] = other.amplitude_axis[o_k]
                    r_k += 1
                    o_k += 1
                # If other is included in self
                s_k = o_j - s_i + 1
                while r_k <= max(o_j, s_j):
                    add_result.amplitude_axis[r_k] = self.amplitude_axis[s_k]
                    r_k += 1
                    s_k += 1
            elif (o_i > s_j and o_j > s_i):
                """
                -------------       ---------
                |           |       |       |
                -------------       ---------
                s_i        s_j     o_i     o_j
                """
                if DEBUG:
                    print("case 2")
                # Left side
                r_k = s_i
                s_k = 0
                while r_k <= s_j:
                    add_result.amplitude_axis[r_k] = self.amplitude_axis[s_k]
                    r_k += 1
                    s_k += 1
                # Right side
                r_k = o_i
                o_k = 0
                while r_k <= o_j:
                    add_result.amplitude_axis[r_k] = other.amplitude_axis[o_k]
                    r_k += 1
                    o_k += 1
            elif (s_i <= o_j and o_i <= s_i):
                """
                ----------------------------
                |           |***n***|       |
                ----------------------------
                o_i        s_i    o_j     s_j
                """
                if DEBUG:
                    print("case 3")
                n = o_j - s_i + 1
                o_k = len(other) - n    # starting index in other array
                s_k = 0                 # starting index in self array
                r_k = s_i               # starting index in result array
                # Sum intersection
                while r_k <= min(o_j, s_j):
                    add_result.amplitude_axis[r_k] = self.amplitude_axis[s_k] + other.amplitude_axis[o_k]
                    r_k += 1
                    s_k += 1
                    o_k += 1
                # Left side
                r_k = 0
                o_k = 0
                while r_k < s_i:
                    add_result.amplitude_axis[r_k] = other.amplitude_axis[o_k]
                    r_k += 1
                    o_k += 1
                # Right side
                r_k = min(o_j, s_j) + 1
                s_k = n
                while r_k <= s_j:
                    add_result.amplitude_axis[r_k] = self.amplitude_axis[s_k]
                    r_k += 1
                    s_k += 1
                # If self is included in other
                o_k = s_j - o_i + 1
                while r_k <= max(o_j, s_j):
                    add_result.amplitude_axis[r_k] = other.amplitude_axis[o_k]
                    r_k += 1
                    o_k += 1

            elif (s_i > o_j and s_j > o_i):
                """
                -------------       ---------
                |           |       |       |
                -------------       ---------
                o_i        o_j     s_i     s_j
                """
                if DEBUG:
                    print("case 4")
                # Left side
                r_k = o_i
                o_k = 0
                while r_k <= o_j:
                    add_result.amplitude_axis[r_k] = other.amplitude_axis[o_k]
                    r_k += 1
                    o_k += 1
                # Right side
                r_k = s_i
                s_k = 0
                while r_k <= s_j:
                    add_result.amplitude_axis[r_k] = self.amplitude_axis[s_k]
                    r_k += 1
                    s_k += 1
        
            return add_result
        else:
            raise TypeError("Waveforms are not of the same sample rate!")

    def __mul__(self, other):
        if self.sample_rate == other.sample_rate:
            duration = max(self.time_end, other.time_end) - min(self.time_start, other.time_start)
            add_result = Waveform(
                duration=duration, 
                time_start= min(self.time_start, other.time_start),
                sample_rate= self.sample_rate
                )
            add_result.time_axis = np.arange(0, duration, 1.0/add_result.sample_rate, dtype=np.float_) + add_result.time_start
            add_result.amplitude_axis = np.zeros(len(add_result))

            s_i = np.isclose(add_result.time_axis, self.time_axis[0]).nonzero()[0][0]
            s_j = np.isclose(add_result.time_axis, self.time_axis[-1]).nonzero()[0][0]
            o_i = np.isclose(add_result.time_axis, other.time_axis[0]).nonzero()[0][0]
            o_j = np.isclose(add_result.time_axis, other.time_axis[-1]).nonzero()[0][0]

            if DEBUG:
                print(f"si: {s_i}, sj: {s_j}, oi: {o_i}, oj: {o_j}")
            if (o_i <= s_j and s_i <= o_i):
                """
                ----------------------------
                |           |***n***|       |
                ----------------------------
                s_i        o_i    s_j     o_j
                """
                if DEBUG:
                    print("case 1")
                
                n = s_j - o_i + 1
                o_k = 0                 # starting index in other array
                s_k = len(self) - n     # starting index in self array
                r_k = o_i               # starting index in result array
                # Sum intersection
                while r_k <= min(s_j, o_j):
                    add_result.amplitude_axis[r_k] = self.amplitude_axis[s_k] * other.amplitude_axis[o_k]
                    r_k += 1
                    s_k += 1
                    o_k += 1
                # Left side
                r_k = 0
                s_k = 0
                while r_k < o_i:
                    add_result.amplitude_axis[r_k] = self.amplitude_axis[s_k]
                    r_k += 1
                    s_k += 1
                # Right side
                r_k = min(s_j, o_j) + 1
                o_k = n
                while r_k <= o_j:
                    add_result.amplitude_axis[r_k] = other.amplitude_axis[o_k]
                    r_k += 1
                    o_k += 1
                # If other is included in self
                s_k = o_j - s_i + 1
                while r_k <= max(o_j, s_j):
                    add_result.amplitude_axis[r_k] = self.amplitude_axis[s_k]
                    r_k += 1
                    s_k += 1
            elif (o_i > s_j and o_j > s_i):
                """
                -------------       ---------
                |           |       |       |
                -------------       ---------
                s_i        s_j     o_i     o_j
                """
                if DEBUG:
                    print("case 2")
                # Left side
                r_k = s_i
                s_k = 0
                while r_k <= s_j:
                    add_result.amplitude_axis[r_k] = self.amplitude_axis[s_k]
                    r_k += 1
                    s_k += 1
                # Right side
                r_k = o_i
                o_k = 0
                while r_k <= o_j:
                    add_result.amplitude_axis[r_k] = other.amplitude_axis[o_k]
                    r_k += 1
                    o_k += 1
            elif (s_i <= o_j and o_i <= s_i):
                """
                ----------------------------
                |           |***n***|       |
                ----------------------------
                o_i        s_i    o_j     s_j
                """
                if DEBUG:
                    print("case 3")
                n = o_j - s_i + 1
                o_k = len(other) - n    # starting index in other array
                s_k = 0                 # starting index in self array
                r_k = s_i               # starting index in result array
                # Sum intersection
                while r_k <= min(o_j, s_j):
                    add_result.amplitude_axis[r_k] = self.amplitude_axis[s_k] * other.amplitude_axis[o_k]
                    r_k += 1
                    s_k += 1
                    o_k += 1
                # Left side
                r_k = 0
                o_k = 0
                while r_k < s_i:
                    add_result.amplitude_axis[r_k] = other.amplitude_axis[o_k]
                    r_k += 1
                    o_k += 1
                # Right side
                r_k = min(o_j, s_j) + 1
                s_k = n
                while r_k <= s_j:
                    add_result.amplitude_axis[r_k] = self.amplitude_axis[s_k]
                    r_k += 1
                    s_k += 1
                # If self is included in other
                o_k = s_j - o_i + 1
                while r_k <= max(o_j, s_j):
                    add_result.amplitude_axis[r_k] = other.amplitude_axis[o_k]
                    r_k += 1
                    o_k += 1

            elif (s_i > o_j and s_j > o_i):
                """
                -------------       ---------
                |           |       |       |
                -------------       ---------
                o_i        o_j     s_i     s_j
                """
                if DEBUG:
                    print("case 4")
                # Left side
                r_k = o_i
                o_k = 0
                while r_k <= o_j:
                    add_result.amplitude_axis[r_k] = other.amplitude_axis[o_k]
                    r_k += 1
                    o_k += 1
                # Right side
                r_k = s_i
                s_k = 0
                while r_k <= s_j:
                    add_result.amplitude_axis[r_k] = self.amplitude_axis[s_k]
                    r_k += 1
                    s_k += 1
        
            return add_result
        else:
            raise TypeError("Waveforms are not of the same sample rate!")

    # Plotting
    def plot(self):
        plt.plot(self.time_axis, self.amplitude_axis)
        plt.ylabel("Amplitude")
        plt.xlabel("Time (s)")
        plt.show()
    
@dataclass
class CosineWaveform(Waveform, Sinusoid):
    
    def __post_init__(self):
        """
        Use Nyquist teorem as default sample rate if has no value.
        """
        
        if self.sample_rate != None:
            # Ensure Nyquist theorem
            if 2 * np.abs(self.frequency) >= self.sample_rate:
                raise TypeError("Sample rate must be greater than twice the frequency")
        else:
            # set default sample rate
            self.sample_rate = 2 * np.abs(self.frequency) + 1 
        
        if DEBUG:
            print(f"sample_rate: {self.sample_rate}, frequency: {self.frequency}")
        
        self.time_axis = np.arange(0, self.duration, 1.0/self.sample_rate, dtype=float) + self.time_start
        self.amplitude_axis = self._sample_amplitudes(self.time_axis)

    def update_sample_rate(self, sample_rate):
        self.sample_rate = sample_rate
        self.time_axis = np.arange(0, self.duration, 1.0/self.sample_rate, dtype=float) + self.time_start
        self.amplitude_axis = self._sample_amplitudes(self.time_axis)

    def update_phase(self, phase):
        self.phase = phase
        self.amplitude_axis = self._sample_amplitudes(self.time_axis)
    
class SineWaveform(CosineWaveform):

    def __post_init__(self):
        # to convert Sinusoid to sine
        self.frequency *= -1
        self.phase = np.pi/2 - self.phase
        super().__post_init__()

class ComplexSinusoid(Sinusoid):
    """
    Class to represent a complex sinusoid given as:

    x(n) = Ae^{j(ωt+phase)} = A(cos(ωt+phase) + jsin(ωt+phase))
    """

    def _sample_amplitudes(self, time_axis: np.array):
        phi = self.angular_frequency * time_axis
        return self.amplitude*np.exp(1j*(phi+ self.phase)) 
    
    # Plotting
    def plot(self, sample_rate:int = None):
        """
        Plot one cycle of the sinusoid in time domain using matplolib
        
        Args:
            sample_rate (int): sampling rate for the sinusoid. Default 100 times the frequency
        """

        if sample_rate == None:
            sample_rate = 2 * np.abs(self.frequency) + 1

        time_axis = np.arange(0, np.abs(1.0/self.frequency), 1.0/sample_rate)
        amplitude_axis = self._sample_amplitudes(time_axis)
        
        plt.plot(time_axis, np.real(amplitude_axis))
        plt.plot(time_axis, np.imag(amplitude_axis))
        plt.legend(['real', 'imag'], loc='upper right')
        plt.ylabel("Amplitude")
        plt.xlabel("Time (s)")
        plt.show()

class ComplexWaveform(Waveform):
    time_axis: npt.NDArray[np.float_] = field(init=False, repr=False)
    amplitude_axis: npt.NDArray[np.float_] = field(init=False, repr=False)
    # Plotting
    def plot(self):
        plt.plot(self.time_axis, np.real(self.amplitude_axis))
        plt.plot(self.time_axis, np.imag(self.amplitude_axis))
        plt.ylabel("Amplitude")
        plt.xlabel("Time (s)")
        plt.show()

# TODO: edit __add__ to work with complex
@dataclass
class ComplexSinusoidWaveform(ComplexWaveform, ComplexSinusoid):
    def __post_init__(self):
        """
        Use Nyquist teorem as default sample rate if has no value.
        """
        if self.sample_rate == None:
            self.sample_rate = 2 * np.abs(self.frequency) + 1     

    @property
    def time_axis(self):
        return np.arange(0, self.duration, 1.0/self.sample_rate) + self.time_start
    
    @property
    def amplitude_axis(self):
        return self._sample_amplitudes(self.time_axis)
    
    def conjugate(self):
        return ComplexSinusoidWaveform(
            self.amplitude, 
            -1*self.frequency, 
            -1*self.phase, 
            self.duration,
            self.time_start,
            self.sample_rate
            )
    
    # Plotting
    def plot(self):
        plt.plot(self.time_axis, np.real(self.amplitude_axis))
        plt.plot(self.time_axis, np.imag(self.amplitude_axis))
        plt.legend(['real', 'imag'], loc='upper right')
        plt.ylabel("Amplitude")
        plt.xlabel("Time (s)")
        plt.show()
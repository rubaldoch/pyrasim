from dataclasses import dataclass
from pyrasim.constants import LIGHT_SPEED
from pyrasim.signals import SineWaveform

class SteppedFrequencyParams():
    pass

@dataclass
class SteppedFrequencyCW():
    """
    N_bursts: int
    n_pulses: int
    target_range: float (m)
    target_velocity: float (ms-1)
    freq_step_size: float   (Hz)
    freq_start: float   (Hz)
    pulse_width: float  (s)
    pulse_repetion_period: float    (s)
    """
    N_bursts: int
    n_pulses: int
    target_range: float
    target_velocity: float
    freq_step_size: float
    freq_start: float
    pulse_width: float
    pulse_repetion_interval: float
    transmitted_amplitude: float
    transmitted_relative_phase: float

    def transmitted_waveform(self, i: int) -> SineWaveform:
        """
        x_i(t)
        pg. 204
        """
        freq_i = self.freq_start + i * self.freq_step_size
        return SineWaveform(
                amplitude = self.transmitted_amplitude, 
                frequency=freq_i, 
                phase=self.transmitted_relative_phase, 
                time_start=i*self.pulse_repetion_interval,
                duration=self.pulse_width
                )

    def received_waveform(self, i: int):
        """
        y_i(t)=B_i
        pg. 205
        """
        freq_i = self.freq_start + i * self.freq_step_size
        range_delay = self.target_range/(LIGHT_SPEED/2)
        return SineWaveform(
                amplitude = self.transmitted_amplitude, 
                frequency = freq_i, 
                phase = self.transmitted_relative_phase, 
                time_start = i*self.pulse_repetion_interval+range_delay,
                duration=self.pulse_width
                )

    def reference_waveform(self, i: int):
        """
        z_i(t)
        """
        freq_i = self.freq_start + i * self.freq_step_size
        return SineWaveform(
                amplitude=self.transmitted_amplitude, 
                frequency=freq_i, 
                phase=self.transmitted_relative_phase, 
                time_start=i*self.pulse_repetion_interval,
                duration=self.pulse_repetion_interval
                 )
    

    def operate(self):
        for i in range(self.n_pulses):
            x = self.transmitted_waveform(i)
            y = self.transmitted_waveform(i)
            z = self.transmitted_waveform(i)
            
            samp_time = i*self.pulse_repetion_interval + (2*self.target_range)/LIGHT_SPEED


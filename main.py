import matplotlib.pyplot as plt
from pyrasim.sfcw import SteppedFrequencyCW


sfcw = SteppedFrequencyCW(1, 10, 3, 0, 10e6, 100e6, 1e-7, 3e-7, 1, 0)
x_t, x_a = sfcw.transmitted_waveform(0)
y_t, y_a = sfcw.received_waveform(0)
z_t, z_a = sfcw.reference_waveform(0)

fig, ax = plt.subplots(nrows=3, sharex=True)
ax[0].plot(x_t, x_a)
ax[0].set_title("Transmitted Waveform")
ax[1].plot(y_t, y_a)
ax[1].set_title("Received Waveform")
ax[2].plot(z_t, z_a)
ax[2].set_title("Reference Waveform")
plt.show()
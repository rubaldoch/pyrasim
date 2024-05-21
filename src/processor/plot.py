def make_recv_signal_plot(fig, axs, cur_freq, ref_data, meas_data):
    ax_real, ax_img = axs
    # In phase plot of ref and meas signals
    ax_real.clear()
    ax_real.set_title("In-phase signals")

    ax_real.plot(np.real(ref_data), color='black')
    ax_real.plot(np.real(meas_data), color='red')

    ax_real.legend(
        ['Reference Channel', 'Measurement Channel'], loc="upper right")
    ax_real.set_ylabel(r'\textbf{Amplitude}')
    ax_real.set_xlim([0, n_points_per_channel_zmq])
    ax_real.set_ylim([-1.2, 1.2])

    # update figure title
    fig.suptitle(f"Received Sine Wave at " +
                 r' $f_{BB}=$' + f"{cur_freq/1e6} MHz", fontsize=12)

    # Quadrature plot of ref and meas signals
    ax_img.clear()
    ax_img.set_title("Quadrature signals")

    ax_img.plot(np.imag(ref_data), color='black')
    ax_img.plot(np.imag(meas_data), color='green')

    ax_img.legend(
        ['Reference Channel', 'Measurement Channel'], loc="upper right")
    ax_img.set_ylabel(r'\textbf{Amplitude}')
    ax_img.set_xlabel(r'\textbf{Sample number}')
    ax_img.set_ylim([-1.2, 1.2])


def make_recv_signal_plot_mosaic(fig, axs, cur_freq, ref_data, meas_data):
    ax_real = axs['upper left']
    ax_img = axs['lower left']
    ax_freq = axs['right']

    # Time domain plots
    make_recv_signal_plot(fig, (ax_real, ax_img),
                          cur_freq, ref_data, meas_data)

    # Power Spectral Density
    ax_freq.clear()
    ax_freq.set_title("Power Spectral Density")
    ax_freq.psd(ref_data, NFFT=n_points_per_channel_zmq // 2,
                pad_to=n_points_per_channel_zmq, Fs=samp_rate)
    ax_freq.psd(meas_data, NFFT=n_points_per_channel_zmq // 2,
                pad_to=n_points_per_channel_zmq, Fs=samp_rate)

    ax_freq.legend(
        ['Reference Channel', 'Measurement Channel'], loc="upper right")


def takahashi_method(meas_data, ref_data, factor_a: float = 1/4, factor_b: float = 3/4):
    """Local Oscillator Phase Compensation Technique

    This combines measurement and reference data by dividing 
    the average of each one.

    Args:
        meas_data (ndarray) : measurement data.
        ref_data (ndarray) : reference data.
        factor_a (float) : idx_left = factor_a*n
        factor_a (float) : idx_right = factor_b*n
    Returns:
        avg_data (np.complex) : combined data
    """
    n = len(meas_data)
    a = int(factor_a * n)
    b = int(factor_b * n)
    avg_meas = np.mean(meas_data[a:b])
    avg_ref = np.mean(ref_data[a:b])
    avg_data = avg_meas/avg_ref
    return avg_data


def plot_takahashi_method(takahashi_vector, fig_taka, ax_taka, plot_title="Range Profile", legend_suffix="A", c=2.998e8, delta_freq=10e6, normalize=True):

    n_points = len(takahashi_vector)
    y = np.fft.ifft(takahashi_vector, n_points)
    y = np.abs(y)/np.max(np.abs(y)) if normalize else np.abs(y)
    x = np.linspace(0, n_points, n_points)

    ax_taka.clear()
    ax_taka.set_title("Quadrature signals")

    ax_taka.plot(x=x*c/(2*n_points*delta_freq), y=y, color='green')
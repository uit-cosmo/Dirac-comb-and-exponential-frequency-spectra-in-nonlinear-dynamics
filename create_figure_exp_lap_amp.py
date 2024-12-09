"""
Power spectral density and autocorrelation function for periodic arrivals and exponentially and laplace distributed amplitudes.

Figure 3 in the paper.

TODO: Fix dirac delta amplitudes.
"""

import numpy as np
from scipy import signal
import fppanalysis as fa
import support_functions as sf
import superposedpulses.forcing as frc
import superposedpulses.point_model as pm
import superposedpulses.pulse_shape as ps
from closedexpressions import PSD_periodic_arrivals, autocorr_periodic_arrivals
import matplotlib.pyplot as plt
import cosmoplots

plt.style.use("cosmoplots.default")

fig, ax = cosmoplots.figure_multiple_rows_columns(rows=1, columns=2)
cosmoplots.change_log_axis_base(ax[0], "y")


class ExpAmp(frc.ForcingGenerator):
    def __init__(self):
        pass

    def get_forcing(self, times: np.ndarray, waiting_time: float) -> frc.Forcing:
        total_pulses = int(max(times) / waiting_time)
        arrival_time_indx = (
            np.arange(start=0, stop=99994, step=5) * 100
        )  # multiplied with inverse dt
        amplitudes = np.random.default_rng().exponential(scale=1.0, size=total_pulses)
        durations = np.ones(shape=total_pulses)
        return frc.Forcing(
            total_pulses, times[arrival_time_indx], amplitudes, durations
        )

    def set_amplitude_distribution(
        self,
        amplitude_distribution_function,
    ):
        pass

    def set_duration_distribution(self, duration_distribution_function):
        pass


model = pm.PointModel(waiting_time=5, total_duration=100000, dt=0.01)
model.set_pulse_shape(ps.LorentzShortPulseGenerator(tolerance=1e-5))
# model.set_amplitude_distribution("exp")
model.set_custom_forcing_generator(ExpAmp())

T, S = model.make_realization()

S_norm = (S - S.mean()) / S.std()

f, Pxx = signal.welch(x=S_norm, fs=100, nperseg=S.size / 10)
ax[0].plot(f, Pxx, label=r"$A \sim \mathrm{Exp}$")

PSD = PSD_periodic_arrivals(2 * np.pi * f, td=1, gamma=0.2, A_rms=1, A_mean=1, dt=0.01)
ax[0].plot(
    f,
    PSD,
    "--k",
    label=r"$S_{\widetilde{\Phi}}(\tau_\mathrm{d} f), \, \langle A \rangle \ne 0$",
)

tb, R = fa.corr_fun(S_norm, S_norm, dt=0.01, norm=False, biased=True, method="auto")
ax[1].plot(tb, R, label=r"$A \sim \mathrm{Exp}$")

t = np.linspace(0, 50, 1000)
R_an = autocorr_periodic_arrivals(t, gamma=0.2, A_mean=1, A_rms=1, norm=True)
ax[1].plot(
    t,
    R_an,
    "--k",
    label=r"$R_{\widetilde{\Phi}}(t/\tau_\mathrm{d}),\, \langle A \rangle \ne 0$",
)


class AsymLaplaceAmp(frc.ForcingGenerator):
    def __init__(self):
        pass

    def get_forcing(self, times: np.ndarray, waiting_time: float) -> frc.Forcing:
        total_pulses = int(max(times) / waiting_time)
        arrival_time_indx = (
            np.arange(start=0, stop=99994, step=5) * 100
        )  # multiplied with inverse dt
        kappa = 0.5
        amplitudes = sf.sample_asymm_laplace(
            alpha=0.5 / np.sqrt(1.0 - 2.0 * kappa * (1.0 - kappa)),
            kappa=kappa,
            size=total_pulses,
        )
        durations = np.ones(shape=total_pulses)
        return frc.Forcing(
            total_pulses, times[arrival_time_indx], amplitudes, durations
        )

    def set_amplitude_distribution(
        self,
        amplitude_distribution_function,
    ):
        pass

    def set_duration_distribution(self, duration_distribution_function):
        pass


model = pm.PointModel(waiting_time=5, total_duration=100000, dt=0.01)
model.set_pulse_shape(ps.LorentzShortPulseGenerator(tolerance=1e-5))
model.set_custom_forcing_generator(AsymLaplaceAmp())

T, S = model.make_realization()

S_norm = (S - S.mean()) / S.std()

f, Pxx = signal.welch(x=S_norm, fs=100, nperseg=S.size / 10)
ax[0].plot(f, Pxx, label=r"$A \sim \mathrm{Laplace}$")

PSD = PSD_periodic_arrivals(2 * np.pi * f, td=1, gamma=0.2, A_rms=1, A_mean=0, dt=0.01)
ax[0].plot(
    f,
    PSD,
    "--g",
    label=r"$S_{\widetilde{\Phi}}(\tau_\mathrm{d} f), \, \langle A \rangle = 0$",
)

tb, R = fa.corr_fun(S_norm, S_norm, dt=0.01, norm=False, biased=True, method="auto")
ax[1].plot(tb, R, label=r"$A \sim \mathrm{Laplace}$")

R_an = autocorr_periodic_arrivals(t, gamma=0.2, A_mean=0, A_rms=1, norm=True)
ax[1].plot(
    t,
    R_an,
    "--g",
    label=r"$R_{\widetilde{\Phi}}(t/\tau_\mathrm{d}), \, \langle A \rangle = 0$",
)

ax[0].legend()
ax[0].set_xlim(-0.03, 1)
ax[0].set_ylim(1e-4, 1e3)
ax[0].set_xlabel(r"$\tau_\mathrm{d} f$")
ax[0].set_ylabel(r"$S_{\widetilde{\Phi}}(\tau_\mathrm{d} f)$")

ax[1].set_xlim(0, 50)
ax[1].set_xlabel(r"$t/\tau_\mathrm{d}$")
ax[1].set_ylabel(r"$R_{\widetilde{\Phi}}(t/\tau_\mathrm{d})$")
ax[1].legend()

fig.savefig("exp_lap.eps")

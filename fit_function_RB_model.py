from plot_lorentz_time_series import (
    # generate_fpp,
    calculate_duration_time,
    calculate_fitrange,
    skewed_lorentz,
)
import numpy as np
from scipy.optimize import minimize
from scipy.signal import find_peaks, fftconvolve


def generate_fpp(var, normalized_data, tkern, dt, td, T):
    """generated normalized filtered point process as a fit for given data"""
    pos_peak_loc = find_peaks(normalized_data, height=0.0001)[0]
    neg_peak_loc = find_peaks(-normalized_data, height=0.0001)[0]
    pos_scale, neg_scale, lam, offset = var
    forcing = np.zeros(T.size)
    forcing[pos_peak_loc] = normalized_data[pos_peak_loc] * pos_scale
    forcing[neg_peak_loc] = normalized_data[neg_peak_loc] * neg_scale

    kern = skewed_lorentz(tkern, dt, lam, td, m=offset)

    time_series_fit = fftconvolve(forcing, kern, "same")
    time_series_fit = (time_series_fit - time_series_fit.mean()) / time_series_fit.std()
    return time_series_fit, forcing


def generate_fpp_fixed_amp(var, normalized_data, tkern, dt, td, T):
    """generated normalized filtered point process as a fit for given data"""
    pos_peak_loc = find_peaks(normalized_data, height=0.0001)[0]
    neg_peak_loc = find_peaks(-normalized_data, height=0.0001)[0]
    lam, offset = var
    forcing = np.zeros(T.size)
    forcing[pos_peak_loc] = normalized_data[pos_peak_loc] * 1
    forcing[neg_peak_loc] = normalized_data[neg_peak_loc] * 1

    kern = skewed_lorentz(tkern, dt, lam, td, m=offset)

    time_series_fit = fftconvolve(forcing, kern, "same")
    time_series_fit = (time_series_fit - time_series_fit.mean()) / time_series_fit.std()
    return time_series_fit, forcing


def generate_fpp_U(td, normalized_data, tkern, dt, T, pulse, lam, shuffled=False):
    """generated normalized filtered point process as a fit for given data"""
    pos_peak_loc = find_peaks(normalized_data, height=0, distance=200)[0]
    forcing = np.zeros(T.size)
    if shuffled:
        shuffled_positions = np.copy(pos_peak_loc)
        rng = np.random.default_rng()
        rng.shuffle(shuffled_positions)
        forcing[pos_peak_loc] = normalized_data[shuffled_positions] * 1
        print(shuffled_positions)
    else:
        forcing[pos_peak_loc] = normalized_data[pos_peak_loc] * 1

    def double_exp(tkern, lam, td):
        kern = np.zeros(tkern.size)
        kern[tkern < 0] = np.exp(tkern[tkern < 0] / lam / td)
        kern[tkern >= 0] = np.exp(-tkern[tkern >= 0] / (1 - lam) / td)
        return kern

    if pulse == "Lorentz":
        kern = skewed_lorentz(tkern, dt, 0.0, td, m=0)
    elif pulse == "sech":
        kern = (np.pi * np.cosh(tkern / td)) ** (-1)
    elif pulse == "gauss":
        kern = np.exp(-((tkern / td) ** 2) / 2) / (np.sqrt(2 * np.pi))
    elif pulse == "exp":
        kern = double_exp(tkern, lam, td)
    else:
        raise ValueError("pulse shape not implemented")

    time_series_fit = fftconvolve(forcing, kern, "same")
    time_series_fit = (time_series_fit - time_series_fit.mean()) / time_series_fit.std()
    return time_series_fit, forcing


def generate_fpp_K(td, normalized_data, tkern, dt, T, pulse, shuffled=False, lam=0.5, distance=200):
    """generated normalized filtered point process as a fit for given data"""
    pos_peak_loc = find_peaks(normalized_data, height=1.0, distance=distance)[0]
    forcing = np.zeros(T.size)
    if shuffled:
        shuffled_positions = np.copy(pos_peak_loc)
        rng = np.random.default_rng()
        rng.shuffle(shuffled_positions)
        forcing[pos_peak_loc] = normalized_data[shuffled_positions] * 1
        print(shuffled_positions)
    else:
        forcing[pos_peak_loc] = normalized_data[pos_peak_loc] * 1

    def double_exp(tkern, lam, td):
        kern = np.zeros(tkern.size)
        kern[tkern < 0] = np.exp(tkern[tkern < 0] / lam / td)
        kern[tkern >= 0] = np.exp(-tkern[tkern >= 0] / (1 - lam) / td)
        return kern

    if pulse == "Lorentz":
        kern = skewed_lorentz(tkern, dt, 0.0, td, m=0)
    elif pulse == "sech":
        kern = (np.pi * np.cosh(tkern / td)) ** (-1)
    elif pulse == "gauss":
        kern = np.exp(-((tkern / td) ** 2) / 2) / (np.sqrt(2 * np.pi))
    elif pulse == "exp":
        kern = double_exp(tkern, lam, td)
    else:
        raise ValueError("pulse shape not implemented")

    time_series_fit = fftconvolve(forcing, kern, "same")
    time_series_fit = (time_series_fit - time_series_fit.mean()) / time_series_fit.std()
    return time_series_fit, forcing


def generate_fpp_dipole(var, normalized_data, tkern, dt, td, T):
    """generated normalized filtered point process as a fit for given data"""
    pos_peak_loc = find_peaks(normalized_data, height=0.0001)[0]
    pos_scale, lam, offset = var
    forcing = np.zeros(T.size)
    forcing[pos_peak_loc] = normalized_data[pos_peak_loc] * pos_scale

    kern_pos = skewed_lorentz(tkern, dt, lam, td, m=offset)
    kern_neg = -skewed_lorentz(tkern, dt, -lam, td, m=offset + 2.5)
    kern = kern_pos + kern_neg

    # import matplotlib.pyplot as plt
    # plt.plot(tkern, kern)
    # plt.xlim(-0.01, 0.02)
    # plt.show()

    time_series_fit = fftconvolve(forcing, kern, "same")
    time_series_fit = (time_series_fit - time_series_fit.mean()) / time_series_fit.std()
    return time_series_fit, forcing


def return_peaks(data, T):
    pos_peak_loc = find_peaks(data, height=0.0001)[0]
    neg_peak_loc = find_peaks(-data, height=0.0001)[0]
    peaks = sorted(np.append(pos_peak_loc, neg_peak_loc))
    return T[peaks], data[peaks], peaks


def create_fit_RB_fixed_amp(regime, f, dt, PSD, normalized_data, T):
    """calculates fit for Lorenz system time series"""
    symbols = ""

    fitrange = {"4e5": (f < 1600) & (f > 700), "2e6": (f < 5200) & (f > 3500)}
    duration_time = calculate_duration_time(
        f[fitrange[regime]], PSD[(fitrange[regime])]
    )

    kernrad = 2**18
    time_kern = np.arange(-kernrad, kernrad + 1) * dt

    def obj_fun(x):
        return 0.5 * np.sum(
            (
                generate_fpp_fixed_amp(
                    x, normalized_data, time_kern, dt, duration_time, T
                )[0]
                ** 2
                - normalized_data**2
            )
            ** 2
        )

    res = minimize(
        obj_fun,
        [0.0, 0.0],
        bounds=((-0.99, 0.99), (-0.5, 0.5)),
    )
    time_series_fit, forcing = generate_fpp_fixed_amp(
        res.x, normalized_data, time_kern, dt, duration_time, T
    )
    return time_series_fit, symbols, duration_time, forcing


def create_fit_RB(regime, f, dt, PSD, normalized_data, T):
    """calculates fit for Lorenz system time series"""
    symbols = ""

    fitrange = {"4e5": (f < 1600) & (f > 700), "2e6": (f < 5200) & (f > 3500)}
    duration_time = calculate_duration_time(
        f[fitrange[regime]], PSD[(fitrange[regime])]
    )

    kernrad = 2**18
    time_kern = np.arange(-kernrad, kernrad + 1) * dt

    def obj_fun(x):
        return 0.5 * np.sum(
            (
                generate_fpp(x, normalized_data, time_kern, dt, duration_time, T)[0]
                ** 2
                - normalized_data**2
            )
            ** 2
        )

    res = minimize(
        obj_fun,
        [1.0, 1.0, 0.0, 0.0],
        bounds=((0.0, 2.0), (0.0, 2.0), (-0.99, 0.99), (-0.5, 0.5)),
    )
    time_series_fit, forcing = generate_fpp(
        res.x, normalized_data, time_kern, dt, duration_time, T
    )
    return time_series_fit, symbols, duration_time, forcing


def create_fit_K(f, dt, normalized_data, T, pulse, td, shuffled=False, lam=0.5, distance=200):
    """calculates fit for Lorenz system time series"""
    symbols = ""

    kernrad = 2**18
    time_kern = np.arange(-kernrad, kernrad + 1) * dt

    # def obj_fun(x):
    #     return 0.5 * np.sum(
    #         (
    #             generate_fpp_K(x, normalized_data, time_kern, dt, T, pulse, lam=0.5)[0]
    #             ** 2
    #             - normalized_data**2
    #         )
    #         ** 2
    #     )
    #
    # res = minimize(obj_fun, x0=0.002, bounds=((0.001, 0.01),))
    # time_series_fit, forcing = generate_fpp_K(
    #     res.x, normalized_data, time_kern, dt, T, pulse, lam=0.5
    # )
    time_series_fit, forcing = generate_fpp_K(
        td, normalized_data, time_kern, dt, T, pulse, distance=distance, lam=lam
    )
    return time_series_fit, symbols, td, forcing


def create_fit_U(f, dt, normalized_data, T, pulse, td, lam, shuffled=False):
    """calculates fit for Lorenz system time series"""
    symbols = ""

    kernrad = 2**18
    time_kern = np.arange(-kernrad, kernrad + 1) * dt

    # def obj_fun(x):
    #     return 0.5 * np.sum(
    #         (
    #             generate_fpp_U(x, normalized_data, time_kern, dt, T, pulse, lam=0.5)[0]
    #             ** 2
    #             - normalized_data**2
    #         )
    #         ** 2
    #     )
    #
    # res = minimize(obj_fun, x0=0.13, bounds=((0.05, 0.3),))
    time_series_fit, forcing = generate_fpp_U(
        td, normalized_data, time_kern, dt, T, pulse, lam
    )
    # print(res.x)
    return time_series_fit, symbols, td, forcing


def create_fit_RB_dipole(regime, f, dt, PSD, normalized_data, T):
    """calculates fit for Lorenz system time series"""
    symbols = ""

    fitrange = {"4e5": (f < 1600) & (f > 700), "2e6": (f < 5200) & (f > 3500)}
    duration_time = calculate_duration_time(
        f[fitrange[regime]], PSD[(fitrange[regime])]
    )

    kernrad = 2**18
    time_kern = np.arange(-kernrad, kernrad + 1) * dt

    def obj_fun(x):
        return 0.5 * np.sum(
            (
                generate_fpp_dipole(
                    x, normalized_data, time_kern, dt, duration_time, T
                )[0]
                ** 2
                - normalized_data**2
            )
            ** 2
        )

    res = minimize(
        obj_fun,
        [1.0, 0.0, 0.0],
        bounds=((0.0, 2.0), (-0.99, 0.99), (-0.5, 0.5)),
    )
    time_series_fit, forcing = generate_fpp_dipole(
        res.x, normalized_data, time_kern, dt, duration_time, T
    )
    return time_series_fit, symbols, duration_time, forcing


def constrained_fit_RB(regime, f, dt, PSD, normalized_data, T):
    """calculates fit for Lorenz system time series"""

    time_peaks, peaks, peak_indices = return_peaks(normalized_data, T)

    symbols = ""

    fitrange = {"4e5": (f < 1600) & (f > 700), "2e6": (f < 5200) & (f > 3500)}
    duration_time = calculate_duration_time(
        f[fitrange[regime]], PSD[(fitrange[regime])]
    )

    kernrad = 2**18
    time_kern = np.arange(-kernrad, kernrad + 1) * dt

    def constraint_func(x):
        fit = generate_fpp(x, normalized_data, time_kern, dt, duration_time, T)[0]
        # print(fit[peak_indices])
        # return fit[peak_indices] - peaks
        return fit[peak_indices[:2]] - peaks[:2]

    def obj_fun(x):
        return 0.5 * np.sum(
            (
                generate_fpp(x, normalized_data, time_kern, dt, duration_time, T)[0]
                ** 2
                - normalized_data**2
            )
            ** 2
        )

    res = minimize(
        obj_fun,
        [1.0, 1.0, 0.0, 0.0],
        bounds=((0.0, 2.0), (0.0, 2.0), (-0.99, 0.99), (-0.5, 0.5)),
        # constraints={"type": "eq", "fun": constraint_func},
    )
    time_series_fit, forcing = generate_fpp(
        res.x, normalized_data, time_kern, dt, duration_time, T
    )
    return time_series_fit, symbols, duration_time, forcing

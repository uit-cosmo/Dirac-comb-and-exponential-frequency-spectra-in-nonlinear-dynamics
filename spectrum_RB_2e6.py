import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from fit_function_RB_model import create_fit_RB

ts = np.load("RB_time_series_2e6.npy")

intervals_start = [10000, 18600, 21200, 28000, 30500, 33000, 37800, 40500, 45400, 52600]

dt = 0.01 / 200

Pxx_average = [0] * 301
Pxx_average_fit = [0] * 301

for i in range(len(intervals_start)):
    # + 600 in order to get the constant part
    ts_interval = ts[intervals_start[i] + 600 : intervals_start[i] + 1200]
    ts_interval = (ts_interval - np.mean(ts_interval)) / np.std(ts_interval)
    # plt.plot(ts_interval)
    # plt.show()
    time = np.linspace(0, dt * len(ts_interval) - dt, num=len(ts_interval))
    f, Pxx = signal.welch(ts_interval, 1 / dt, nperseg=len(ts_interval) / 1)

    time_series_fit, symbols, duration_time = create_fit_RB(
        "2e6", f, dt, Pxx, ts_interval, time
    )

    f_fit, Pxx_fit = signal.welch(
        time_series_fit, 1 / dt, nperseg=len(time_series_fit) / 1
    )

    Pxx_average += Pxx
    Pxx_average_fit += Pxx_fit

    print(f"Done with {i+1}/{len(intervals_start)}")

Pxx_average /= 10
Pxx_average_fit /= 10
time = np.linspace(0, dt * len(ts) - dt, num=len(ts))

plt.figure()
plt.xlabel("t")
plt.ylabel("theta")
plt.plot(time, ts)

plt.figure()
plt.semilogy(f, Pxx_average)
plt.semilogy(f_fit, Pxx_average_fit)
plt.xlabel("f")
plt.ylabel("PSD(f)")
plt.show()

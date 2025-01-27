import numpy as np
from fppanalysis import cond_av
from scipy import signal
import matplotlib.pyplot as plt
from support_functions import create_fit
import cosmoplots


axes_size = cosmoplots.set_rcparams_dynamo(plt.rcParams, num_cols=1, ls="thin")

K = np.load("./RB_data/K_1.6e-3_data.npy")
time = np.load("./RB_data/time_1.6e-3_data.npy")

dt = time[1] - time[0]

_, K_av, _, _, _, wait = cond_av(K, time, smin=1, window=True, delta=50)

wait = wait[wait > 50]
plt.hist(wait / np.mean(wait), 32, density=True)
plt.xlabel(r"$\tau_w/\langle\tau_w\rangle$")
plt.ylabel(r"$P(\tau_w/\langle\tau_w\rangle)$")
plt.savefig("P(tau)_1_6e-3.eps", bbox_inches="tight")
plt.show()

K = (K - np.mean(K)) / np.std(K)
fK, PK = signal.welch(K, 1 / dt, nperseg=len(K) / 4)

K_fit = create_fit(dt, K, time, td=8, lam=0.4, distance=50)

plt.plot(time, K)
plt.plot(time, K_fit, "--")
plt.xlabel(r"$t$")
plt.ylabel(r"$\widetilde{K}$")
plt.xlim(20000, 22000)
plt.savefig("K_fit_1_6e-3.eps", bbox_inches="tight")
plt.show()


f, PK_fit = signal.welch(K_fit, 1 / dt, nperseg=len(K_fit) / 4)

plt.semilogy(fK, PK)
plt.semilogy(f, PK_fit, "--")
plt.xlabel(r"$f$")
plt.ylabel(r"$S_{\widetilde{K}}\left( f \right)$")
plt.xlim(-0.01, 0.1)
plt.ylim(1e-2, None)
plt.savefig("S(K)_fit_1_6e-3.eps", bbox_inches="tight")
plt.show()

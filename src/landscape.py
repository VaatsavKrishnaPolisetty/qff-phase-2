"""Objective landscape (kit Section 8): sampled mean QUBO cost over a (gamma, beta) grid.

Grid >= 20 x 20, beta in [0, pi], gamma in [0, gamma_max], 1024 shots per point, Processor D,
official noise. The Hamiltonian is divided by its largest coefficient magnitude (`scale`);
gamma is in those scaled units. The plotted value is the true (unscaled) QUBO cost.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from . import knapsack as K
from .circuits import build_qaoa_circuit, sample

LANDSCAPE_SHOTS = 1024


def noisy_landscape(h, J, scale, proc, gammas, betas, shots: int = LANDSCAPE_SHOTS, verbose: bool = True):
    """Z[i, j] = sampled mean QUBO cost at beta=betas[i], gamma=gammas[j]."""
    Z = np.zeros((len(betas), len(gammas)))
    total = Z.size
    done = 0
    for i, b in enumerate(betas):
        for j, g in enumerate(gammas):
            qc = build_qaoa_circuit(g, b, h, J, scale)
            counts, _ = sample(qc, proc, noisy=True, shots=shots)
            Z[i, j] = K.evaluate_counts(counts)["mean_qubo_cost"]
            done += 1
        if verbose:
            print(f"landscape: {done}/{total} points", flush=True)
    return Z


def load_or_compute(path, recompute: bool, **kw):
    """RECOMPUTE flag: reload the saved grid unless recompute=True (keeps the notebook < 30 min)."""
    path = Path(path)
    if path.exists() and not recompute:
        d = np.load(path)
        return d["Z"], d["gammas"], d["betas"]
    gammas, betas = kw["gammas"], kw["betas"]
    Z = noisy_landscape(kw["h"], kw["J"], kw["scale"], kw["proc"], gammas, betas)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(path, Z=Z, gammas=gammas, betas=betas)
    return Z, gammas, betas


def plot_landscape(Z, gammas, betas, best_gamma, best_beta, title, path=None, ax=None):
    """Heatmap with the optimised (gamma, beta) marked."""
    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 5.5))
    else:
        fig = ax.figure
    im = ax.imshow(Z, origin="lower", aspect="auto", cmap="viridis",
                   extent=[gammas[0], gammas[-1], betas[0], betas[-1]])
    fig.colorbar(im, ax=ax, label="mean QUBO cost (lower is better)")
    ax.scatter([best_gamma], [best_beta], marker="*", s=260, c="red", edgecolors="white",
               label=f"optimised ($\\gamma$={best_gamma:.3f}, $\\beta$={best_beta:.3f})", zorder=5)
    ax.set_xlim(gammas[0], gammas[-1])      # keep the grid range even if the optimum lies outside it
    ax.set_ylim(betas[0], betas[-1])
    ax.set_xlabel(r"$\gamma$ (scaled Hamiltonian)")
    ax.set_ylabel(r"$\beta$")
    ax.set_title(title)
    ax.legend(loc="upper right", fontsize=8)
    if path is not None:
        fig.savefig(path, dpi=150, bbox_inches="tight")
    return fig

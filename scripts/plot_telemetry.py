#!/usr/bin/env python3
# Generate academic-grade telemetry charts for the RCT open-science release.
# Reads CSVs from ../data/, writes PNGs to ../docs/. No network access.
# Usage: python3 scripts/plot_telemetry.py
"""Plot RCT telemetry: 3D MIPT transition curve and BLP backflow witness."""
import csv
import os
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
DOCS = os.path.join(HERE, "..", "docs")

plt.rcParams.update(
    {
        "figure.dpi": 150,
        "savefig.dpi": 150,
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.labelsize": 10,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
        "axes.grid": True,
        "grid.alpha": 0.3,
    }
)


def read_mipt(path):
    """Read MIPT sweep CSV: p, mean_S, std, meas_per_traj."""
    ps, means, stds, meas = [], [], [], []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            ps.append(float(row["p"]))
            means.append(float(row["mean_S"]))
            stds.append(float(row["std_S"]))
            meas.append(float(row["meas_per_traj"]))
    return ps, means, stds, meas


def read_blp(path):
    """Read BLP series CSV: step, D_memory, D_markov_info_only."""
    steps, mem, mar = [], [], []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            steps.append(int(row["step"]))
            mem.append(float(row["D_memory"]))
            mar.append(float(row["D_markov_info_only"]))
    return steps, mem, mar


def chart_a_mipt(ps, means, stds, outpath):
    """Chart A: 3D MIPT volume-law plateau to area-law floor, pc ~ 0.150."""
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    ax.errorbar(
        ps,
        means,
        yerr=stds,
        fmt="o-",
        capsize=3,
        elinewidth=1.2,
        markersize=5,
        label="mean half-cut entropy S (8 shots/point)",
    )
    ax.axhline(8.0, color="gray", linestyle=":", linewidth=1.0, label="max (8 bits, N=16)")
    ax.axvline(0.150, color="crimson", linestyle="--", linewidth=1.2, label=r"$p_c \approx 0.150$ (mid-entropy crossing)")
    ax.annotate(
        "volume-law plateau\n7.61 bits (95% of max)",
        xy=(0.02, 7.609),
        xytext=(0.06, 7.9),
        fontsize=9,
        arrowprops={"arrowstyle": "->", "color": "black", "lw": 1.0},
    )
    ax.annotate(
        "area-law floor\n~2.3 bits",
        xy=(0.40, 2.310),
        xytext=(0.28, 1.6),
        fontsize=9,
        arrowprops={"arrowstyle": "->", "color": "black", "lw": 1.0},
    )
    ax.set_xlabel("measurement rate p (per qubit per layer)")
    ax.set_ylabel("mean half-cut entropy S (bits, max 8)")
    ax.set_title("3D Measurement-Induced Phase Transition (N=16)\n48 layers x 8 Haar SU(4), RT-sourced geometry")
    ax.set_xlim(0.0, 0.42)
    ax.set_ylim(0.0, 8.6)
    ax.legend(loc="center right")
    fig.tight_layout()
    fig.savefig(outpath)
    plt.close(fig)
    print(f"wrote {outpath}")


def chart_b_blp(steps, mem, mar, outpath):
    """Chart B: BLP trace distance with 5 backflow revivals vs forgetful arm."""
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    ax.plot(steps, mem, "o-", markersize=5, label="memory arm D(t) — 5 rises, max +0.20")
    ax.plot(
        steps,
        mar,
        "s--",
        markersize=4,
        alpha=0.55,
        label="forgetful arm D(t) (informational control)",
    )
    # Highlight the headline revival 0.664 -> 0.862 (steps 10 -> 11).
    ax.annotate(
        "revival +0.20\n0.664 -> 0.862",
        xy=(11, 0.862),
        xytext=(7.5, 1.0),
        fontsize=9,
        arrowprops={"arrowstyle": "->", "color": "black", "lw": 1.0},
    )
    ax.set_xlabel("event step")
    ax.set_ylabel("BLP trace distance D")
    ax.set_title("Non-Markovian Backflow: BLP Witness (NC=3 exact dual-mode, t=1.8 script)")
    ax.set_xlim(-0.3, 13.3)
    ax.set_ylim(0.55, 1.12)
    ax.legend(loc="lower left")
    fig.tight_layout()
    fig.savefig(outpath)
    plt.close(fig)
    print(f"wrote {outpath}")


def main():
    ps, means, stds, meas = read_mipt(os.path.join(DATA, "mipt_sweep.csv"))
    del meas  # plotted implicitly via the sweep design; kept in CSV for audit
    chart_a_mipt(ps, means, stds, os.path.join(DOCS, "chart_a_mipt.png"))
    steps, mem, mar = read_blp(os.path.join(DATA, "blp_series.csv"))
    chart_b_blp(steps, mem, mar, os.path.join(DOCS, "chart_b_blp.png"))


if __name__ == "__main__":
    main()

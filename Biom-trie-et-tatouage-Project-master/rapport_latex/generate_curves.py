"""
Generate professional DET, ROC, and Distance Distribution curves
for the SecurAccess biometric report.
Saves PNG files directly into rapport_latex/.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
from pathlib import Path

# ── Output directory ──────────────────────────────────────────────────────────
OUT = Path(__file__).parent

# ── Style setup (modern, clean) ──────────────────────────────────────────────
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Inter", "Segoe UI", "Arial"],
    "font.size": 12,
    "axes.titlesize": 16,
    "axes.titleweight": "bold",
    "axes.labelsize": 13,
    "axes.linewidth": 0.8,
    "axes.edgecolor": "#cbd5e1",
    "axes.facecolor": "#fafbfc",
    "figure.facecolor": "#ffffff",
    "grid.color": "#e2e8f0",
    "grid.linewidth": 0.6,
    "xtick.color": "#5b6e8c",
    "ytick.color": "#5b6e8c",
    "text.color": "#1e2a3e",
    "legend.framealpha": 0.9,
    "legend.edgecolor": "#e2e8f0",
})

# ── Performance data from the report ─────────────────────────────────────────
# Threshold, FAR (%), FRR (%)
data = np.array([
    [0.50, 0.0,  22.0],
    [0.55, 0.0,  17.5],
    [0.60, 0.0,  12.5],
    [0.65, 0.0,   8.0],
    [0.70, 0.0,   5.0],
    [0.75, 0.0,   3.2],
    [0.78, 0.5,   2.5],
    [0.80, 1.5,   1.8],
    [0.82, 1.8,   1.8],  # EER point
    [0.85, 2.5,   1.2],
    [0.90, 4.2,   0.5],
    [0.95, 6.5,   0.1],
    [1.00, 8.7,   0.0],
    [1.10, 12.0,  0.0],
    [1.20, 16.5,  0.0],
])

thresholds = data[:, 0]
far = data[:, 1]
frr = data[:, 2]
tar = 100 - frr  # True Acceptance Rate


# =============================================================================
# 1. DET Curve — FAR vs FRR
# =============================================================================
def generate_det_curve():
    fig, ax = plt.subplots(figsize=(8, 6))

    ax.plot(far, frr, color="#3b82f6", linewidth=2.5, marker="o",
            markersize=6, markerfacecolor="white", markeredgewidth=2,
            markeredgecolor="#3b82f6", label="Courbe DET", zorder=5)

    # EER point
    eer_idx = 8  # index where FAR ≈ FRR ≈ 1.8%
    ax.plot(far[eer_idx], frr[eer_idx], "o", color="#ef4444", markersize=12,
            markeredgewidth=2, markerfacecolor="#ef4444", zorder=6)
    ax.annotate(f"EER ≈ {far[eer_idx]:.1f}%",
                xy=(far[eer_idx], frr[eer_idx]),
                xytext=(far[eer_idx] + 2.5, frr[eer_idx] + 3),
                fontsize=12, fontweight="bold", color="#ef4444",
                arrowprops=dict(arrowstyle="->", color="#ef4444", lw=1.5))

    # Operating point (threshold = 0.75)
    op_idx = 5  # threshold 0.75
    ax.plot(far[op_idx], frr[op_idx], "s", color="#22c55e", markersize=12,
            markeredgewidth=2, markerfacecolor="#22c55e", zorder=6)
    ax.annotate(f"Seuil opérationnel\n(t=0.75, FAR=0%, FRR=3.2%)",
                xy=(far[op_idx], frr[op_idx]),
                xytext=(far[op_idx] + 3, frr[op_idx] + 5),
                fontsize=11, fontweight="bold", color="#22c55e",
                arrowprops=dict(arrowstyle="->", color="#22c55e", lw=1.5))

    # Diagonal (EER line)
    ax.plot([0, 25], [0, 25], "--", color="#94a3b8", linewidth=1, alpha=0.7,
            label="FAR = FRR (diagonale)")

    ax.set_xlabel("FAR — False Acceptance Rate (%)")
    ax.set_ylabel("FRR — False Rejection Rate (%)")
    ax.set_title("Courbe DET — Detection Error Tradeoff")
    ax.set_xlim(-0.5, 18)
    ax.set_ylim(-0.5, 24)
    ax.legend(loc="upper right", fontsize=11)
    ax.grid(True, alpha=0.5)

    # Fill the "good zone"
    ax.fill_between([0, 2], [0, 0], [4, 4], alpha=0.08, color="#22c55e")
    ax.text(0.3, 1.0, "Zone optimale", fontsize=10, color="#22c55e",
            fontstyle="italic", alpha=0.8)

    fig.tight_layout()
    path = OUT / "courbe_det.png"
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] Saved: {path}")


# =============================================================================
# 2. ROC Curve — TAR vs FAR
# =============================================================================
def generate_roc_curve():
    fig, ax = plt.subplots(figsize=(8, 6))

    ax.plot(far, tar, color="#8b5cf6", linewidth=2.5, marker="o",
            markersize=6, markerfacecolor="white", markeredgewidth=2,
            markeredgecolor="#8b5cf6", label="Courbe ROC", zorder=5)

    # Fill area under curve
    ax.fill_between(far, tar, alpha=0.08, color="#8b5cf6")

    # Operating point
    op_idx = 5
    ax.plot(far[op_idx], tar[op_idx], "s", color="#22c55e", markersize=12,
            markeredgewidth=2, markerfacecolor="#22c55e", zorder=6)
    ax.annotate(f"Seuil opérationnel\n(FAR=0%, TAR=96.8%)",
                xy=(far[op_idx], tar[op_idx]),
                xytext=(far[op_idx] + 3, tar[op_idx] - 6),
                fontsize=11, fontweight="bold", color="#22c55e",
                arrowprops=dict(arrowstyle="->", color="#22c55e", lw=1.5))

    # Ideal point
    ax.plot(0, 100, "*", color="#f59e0b", markersize=18, zorder=6)
    ax.annotate("Idéal (0%, 100%)", xy=(0, 100), xytext=(2, 93),
                fontsize=11, color="#f59e0b", fontweight="bold",
                arrowprops=dict(arrowstyle="->", color="#f59e0b", lw=1.5))

    # Random classifier
    ax.plot([0, 100], [0, 100], "--", color="#94a3b8", linewidth=1, alpha=0.7,
            label="Classificateur aléatoire")

    ax.set_xlabel("FAR — False Acceptance Rate (%)")
    ax.set_ylabel("TAR — True Acceptance Rate (%)")
    ax.set_title("Courbe ROC — Receiver Operating Characteristic")
    ax.set_xlim(-0.5, 18)
    ax.set_ylim(75, 101)
    ax.legend(loc="lower right", fontsize=11)
    ax.grid(True, alpha=0.5)

    fig.tight_layout()
    path = OUT / "courbe_roc.png"
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] Saved: {path}")


# =============================================================================
# 3. Distance Distribution — intra-class vs inter-class
# =============================================================================
def generate_distance_distribution():
    np.random.seed(42)

    # Simulated distributions
    intra = np.random.normal(0.35, 0.12, 500)   # Same person → low distance
    inter = np.random.normal(0.95, 0.18, 500)    # Different people → high distance
    intra = intra[intra > 0]
    inter = inter[inter > 0]

    fig, ax = plt.subplots(figsize=(8, 6))

    ax.hist(intra, bins=40, alpha=0.65, color="#22c55e", edgecolor="white",
            linewidth=0.5, label="Intra-classe (même personne)", density=True)
    ax.hist(inter, bins=40, alpha=0.65, color="#ef4444", edgecolor="white",
            linewidth=0.5, label="Inter-classe (imposteurs)", density=True)

    # Threshold lines
    ax.axvline(x=0.75, color="#3b82f6", linewidth=2, linestyle="--",
               label="Seuil strict (t=0.75)")
    ax.axvline(x=0.90, color="#f59e0b", linewidth=2, linestyle="--",
               label="Seuil de revue (t=0.90)")

    # Zone labels
    ax.fill_betweenx([0, 5], 0.75, 0.90, alpha=0.06, color="#f59e0b")
    ax.text(0.80, 3.5, "Zone\nde revue", fontsize=10, color="#f59e0b",
            ha="center", fontstyle="italic")
    ax.text(0.40, 3.5, "ACCEPTÉ", fontsize=11, color="#22c55e",
            ha="center", fontweight="bold", alpha=0.7)
    ax.text(1.10, 3.5, "REJETÉ", fontsize=11, color="#ef4444",
            ha="center", fontweight="bold", alpha=0.7)

    ax.set_xlabel("Distance euclidienne (L2)")
    ax.set_ylabel("Densité")
    ax.set_title("Distribution des distances intra-classe et inter-classe")
    ax.set_xlim(0, 1.6)
    ax.legend(loc="upper right", fontsize=10)
    ax.grid(True, alpha=0.4)

    fig.tight_layout()
    path = OUT / "distribution_distances.png"
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] Saved: {path}")


# =============================================================================
# Run all
# =============================================================================
if __name__ == "__main__":
    print("Generating charts for SecurAccess report...\n")
    generate_det_curve()
    generate_roc_curve()
    generate_distance_distribution()
    print("\n[DONE] All 3 charts generated successfully!")

#!/usr/bin/env python3
"""
Export MP1a analytical charts (Questions 1–3) to PNG and SVG in this folder.

Run: python3 export_mp1_charts.py

Requires: pandas, numpy, matplotlib
"""

from __future__ import annotations

from math import ceil
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd


def load_frame() -> tuple[pd.DataFrame, str]:
    base_dir = Path(__file__).resolve().parent
    chat_dir = base_dir / "chat_regular"
    paths = sorted(chat_dir.glob("chat*.csv"))
    if not paths:
        paths = sorted(base_dir.glob("chat*.csv"))
    if not paths:
        raise FileNotFoundError(
            "No chat*.csv found in chat_regular/ or next to this script."
        )
    df = pd.concat(
        [pd.read_csv(p).assign(source_file=p.name) for p in paths],
        ignore_index=True,
    )
    df["stream_id"] = (
        df["source_file"].str.removesuffix(".csv").str.removeprefix("chat_")
    )
    primary_id = df.groupby("stream_id")["video_offset_sec"].max().idxmax()
    return df, primary_id


def export_all(out_dir: Path | None = None) -> list[Path]:
    out_dir = out_dir or Path(__file__).resolve().parent
    df, primary_id = load_frame()

    primary = df[df["stream_id"] == primary_id].copy()
    primary["offset_min_bin_5"] = (primary["video_offset_sec"] // 300) * 5
    primary_for_who = primary.dropna(subset=["author_channel_id"])

    written: list[Path] = []

    def save_both(fig: plt.Figure, stem: str) -> None:
        for ext in ("png", "svg"):
            path = out_dir / f"{stem}.{ext}"
            fig.savefig(
                path,
                dpi=150 if ext == "png" else None,
                bbox_inches="tight",
                facecolor="white",
            )
            written.append(path)
        plt.close(fig)

    # ----- Question 1 -----
    bin_df = (
        primary.groupby("offset_min_bin_5", as_index=False)
        .size()
        .rename(columns={"size": "messages_in_bin"})
    )
    bin_df["messages_per_min"] = bin_df["messages_in_bin"] / 5.0
    top_n = 12
    top_bins = bin_df.nlargest(top_n, "messages_per_min").sort_values(
        "messages_per_min"
    )
    labels = top_bins["offset_min_bin_5"].apply(
        lambda m: f"Minutes {int(m)} to {int(m + 5)} from stream start"
    )

    fig1, ax1 = plt.subplots(figsize=(9, 6.5))
    ax1.barh(labels, top_bins["messages_per_min"], color="#636efa")
    ax1.set_xlabel("Messages per minute (messages in 5-min bin / 5)")
    ax1.set_ylabel("Time window")
    ax1.set_title(
        "Question 1: Where chat rate peaks on the primary stream "
        "(twelve busiest 5-minute windows)"
    )
    ax1.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    fig1.tight_layout()
    save_both(fig1, "mp1_q1_volume_bursts")

    # ----- Question 2 -----
    counts = primary_for_who["author_channel_id"].value_counts()
    n_users = counts.size
    k_top = max(1, int(np.ceil(0.10 * n_users)))
    pct_top = 100 * counts.head(k_top).sum() / counts.sum()
    groups = [
        "Top 10% busiest\naccounts\n(by message count)",
        "All other\naccounts\ncombined",
    ]
    vals = [pct_top, 100 - pct_top]
    colors = ["#EF553B", "#636efa"]

    fig2, ax2 = plt.subplots(figsize=(7.5, 5.5))
    bars = ax2.bar(groups, vals, color=colors, width=0.55)
    ax2.set_ylabel("Percent of all messages on this stream (%)")
    ax2.set_xlabel("Author group")
    ax2.set_title(
        "Question 2: Concentration of messages among the busiest tenth "
        "of authors (primary stream)"
    )
    ax2.set_ylim(0, max(100, pct_top * 1.12))
    for b, v in zip(bars, vals):
        ax2.text(
            b.get_x() + b.get_width() / 2,
            b.get_height() + 1.0,
            f"{v:.1f}%",
            ha="center",
            va="bottom",
            fontsize=11,
        )
    fig2.tight_layout()
    save_both(fig2, "mp1_q2_author_concentration")

    # ----- Question 3 -----
    p3 = primary.copy()
    author_totals = p3.groupby("author_channel_id").size().sort_values(ascending=False)
    k10 = max(1, ceil(0.10 * author_totals.size))
    heavy = set(author_totals.head(k10).index)
    p3["from_heavy_posters"] = p3["author_channel_id"].isin(heavy)

    per_bin = (
        p3.groupby("offset_min_bin_5", as_index=False)
        .agg(
            messages_in_bin=("author_channel_id", "size"),
            different_people=("author_channel_id", pd.Series.nunique),
            pct_lines_from_heavy=("from_heavy_posters", "mean"),
        )
    )
    mid = per_bin["messages_in_bin"].median()
    per_bin["kind"] = np.where(
        per_bin["messages_in_bin"] >= mid,
        "Busier bins\n(at or above median\nmessages per window)",
        "Quieter bins\n(below median\nmessages per window)",
    )

    summary = (
        per_bin.groupby("kind", observed=True)
        .agg(
            avg_different_people=("different_people", "mean"),
            avg_pct_from_heavy=("pct_lines_from_heavy", "mean"),
        )
        .reset_index()
    )
    summary["pct_heavy"] = 100 * summary["avg_pct_from_heavy"]
    order = sorted(summary["kind"].tolist(), reverse=True)
    s2 = summary.set_index("kind").loc[order].reset_index()

    fig3, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(11, 5))
    x = np.arange(len(s2))
    w = 0.55
    ax_l.bar(x, s2["avg_different_people"], width=w, color="#636efa")
    ax_l.set_xticks(x)
    ax_l.set_xticklabels(s2["kind"], fontsize=9)
    ax_l.set_ylabel("Mean count (unique authors per 5-min bin)")
    ax_l.set_xlabel("Activity group (median split on messages per bin)")
    ax_l.set_title("Mean unique authors per 5-minute bin")

    ax_r.bar(x, s2["pct_heavy"], width=w, color="#EF553B")
    ax_r.set_xticks(x)
    ax_r.set_xticklabels(s2["kind"], fontsize=9)
    ax_r.set_ylabel("Mean percent of lines from heaviest 10% of posters (%)")
    ax_r.set_xlabel("Activity group (median split on messages per bin)")
    ax_r.set_title("Mean percent of lines from heaviest 10% of posters")
    ax_r.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f"))

    fig3.suptitle(
        "Question 3: Participation breadth vs heavy-poster dominance in quieter "
        "versus busier 5-minute bins (median split, primary stream)",
        fontsize=12,
        y=1.02,
    )
    fig3.text(
        0.01,
        -0.02,
        "Quieter or busier = bins below or above the median message count per "
        "5-minute window (not first vs second half of runtime).",
        fontsize=9,
        wrap=True,
    )
    fig3.tight_layout()
    save_both(fig3, "mp1_q3_participation_high_vs_low")

    return written


if __name__ == "__main__":
    for path in export_all():
        print(path)

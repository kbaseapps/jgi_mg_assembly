import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.ticker import ScalarFormatter
import pandas as pd
import os

def generate_graphics(cov_file, output_dir):
    df = pd.read_table(cov_file)
    fold_vs_len_file = _generate_fold_vs_length(df, output_dir, "png")
    fold_vs_gc_file = _generate_fold_vs_gc(df, output_dir, "png")
    gc_hist_file = _generate_gc_histogram(df, output_dir, "png")
    return {
        "avg_fold_vs_len": fold_vs_len_file,
        "gc_vs_avg_fold": fold_vs_gc_file,
        "gc_hist": gc_hist_file
    }

def _generate_fold_vs_length(df, output_dir, suffix):
    """
    df = dataframe, expected to have Avg_fold and Length columns
    Makes a file called "avg_fold_vs_len.{suffix}" and returns the full path to it.
    """
    fig, ax = plt.subplots(figsize=(6,6))
    plt.yticks(rotation=90, va='center')
    plt.plot(df.Length, df.Avg_fold, '+')
    ax.set_yscale('log')
    ax.yaxis.set_major_formatter(ScalarFormatter())
    ax.set(xlabel="Contigs Length (bp)", ylabel="Average coverage fold (x)", title="Contigs average fold coverage vs. Contigs length")

    outfile = os.path.join(output_dir, "avg_fold_vs_len.{}".format(suffix))
    fig.savefig(outfile, dpi=100)
    return outfile

def _generate_fold_vs_gc(df, output_dir, suffix):
    fig, ax = plt.subplots(figsize=(6,6))
    plt.yticks(rotation=90, va='center')
    plt.plot(df.Avg_fold, df.Ref_GC, '+')
    ax.set_xscale('log')
    ax.xaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax.set(xlabel="Average coverage fold (x)", ylabel="GC (%)", title="Contigs average fold coverage vs. GC")

    outfile = os.path.join(output_dir, "gc_vs_avg_fold.{}".format(suffix))
    fig.savefig(outfile, dpi=100)
    return outfile

def _generate_gc_histogram(df, output_dir, suffix):
    fig, ax = plt.subplots(figsize=(6,6))
    plt.yticks(rotation=90, va='center')
    plt.hist(df[df['Length'].gt(0)].Ref_GC*100, [v/10.0 for v in range(0, 1020, 15)], lw=1, fill=False, fc=(0, 0, 0))
    ax.set(ylabel="# of contigs", xlabel="GC (%)", title="GC Histogram for contigs")

    outfile = os.path.join(output_dir, "gc_hist.{}".format(suffix))
    fig.savefig(outfile, dpi=100)
    return outfile

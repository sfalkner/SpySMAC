#!/usr/bin/env python

from argparse import ArgumentParser
import sys
import itertools

from matplotlib.pyplot import tight_layout, figure, subplots_adjust,\
    subplot, savefig, show, setp
import matplotlib.gridspec
import numpy as np
from matplotlib.ticker import FormatStrFormatter


def plot_scatter_plot(x_data, y_data, labels, title="", save="", debug=False,
                      min_val=None, max_val=1000, grey_factor=1, linefactors=None,
                      user_fontsize=20, dpi=100):
    regular_marker = 'x'
    timeout_marker = '+'
    grey_marker = '.'
    c_angle_bisector = "#e41a1c"  # Red
    c_good_points = "#999999"     # Grey
    c_other_points = "k"
    size = 1
    st_ref = "--"

    ticklabel_size = user_fontsize
    linefactor_size = user_fontsize - 2
    label_size = user_fontsize + 1

    #------
    # maximum_value: location for timeout points
    # max_val      : Initially user-defined timeout, then set to axes limit
    # time_out_val : location for timeout points
    # -----

    maximum_value = max_val

    # Colors
    ref_colors = itertools.cycle([  # "#e41a1c",    # Red
                                 "#377eb8",    # Blue
                                 "#4daf4a",    # Green
                                 "#984ea3",    # Purple
                                 "#ff7f00",    # Orange
                                 "#ffff33",    # Yellow
                                 "#a65628",    # Brown
                                 "#f781bf",    # Pink
                                 # "#999999",    # Grey
                                 ])

    # Set up figure
    ratio = 1
    gs = matplotlib.gridspec.GridSpec(ratio, 1)
    fig = figure(1, dpi=100)
    fig.suptitle(title, fontsize=16, y=1.02)
    ax1 = subplot(gs[0:ratio, :], aspect='equal')
    ax1.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.5)

    # set initial limits
    if min_val is not None:
        auto_min_val = min([min(x_data), min(y_data), min_val])
    else:
        auto_min_val = min([min(x_data), min(y_data)])
    auto_max_val = maximum_value
    timeout_val = maximum_value *2 #+ 10**int((np.log10(max_val)))

    # Plot angle bisector and reference_lines
    out_up = auto_max_val
    out_lo = auto_min_val

    ax1.plot([out_lo, out_up], [out_lo, out_up], c=c_angle_bisector)

    if linefactors is not None:
        for f in linefactors:
            c = next(ref_colors)
            # Lower reference lines
            ax1.plot([f*out_lo, out_up], [out_lo, (1.0/f)*out_up], c=c,
                     linestyle=st_ref, linewidth=size*1.5)
            # Upper reference lines
            ax1.plot([out_lo, (1.0/f)*out_up], [f*out_lo, out_up], c=c,
                     linestyle=st_ref, linewidth=size*1.5)
            offset = 1.1
            if int(f) == f:
                lf_str = "%dx" % f
            else:
                lf_str = "%2.1fx" % f
            ax1.text((1.0/f)*out_up, out_up*offset, lf_str, color=c,
                     fontsize=linefactor_size)
            ax1.text(out_up*offset, (1.0/f)*out_up, lf_str, color=c,
                     fontsize=linefactor_size)


    #######
    #  Scatter
    grey_idx = list()
    timeout_x = list()
    timeout_y = list()
    timeout_both = list()
    rest_idx = list()
    for idx_x, x in enumerate(x_data):
        if x >= max_val > y_data[idx_x]:
            # timeout of x algo
            timeout_x.append(idx_x)
        elif y_data[idx_x] >= max_val > x:
            # timeout of y algo
            timeout_y.append(idx_x)
        elif y_data[idx_x] >= max_val and x >= max_val:
            # timeout of both algos
            timeout_both.append(idx_x)
        elif y_data[idx_x] < grey_factor*x and x < grey_factor*y_data[idx_x]:
            grey_idx.append(idx_x)
        else:
            rest_idx.append(idx_x)

    # Regular points
    if len(grey_idx) > 1:
        ax1.scatter(x_data[grey_idx], y_data[grey_idx], marker=grey_marker,
                    c=c_good_points)
    ax1.scatter(x_data[rest_idx], y_data[rest_idx], marker=regular_marker,
                c=c_other_points)

    # max_val lines
    ax1.plot([maximum_value, maximum_value], [auto_min_val, maximum_value],
             c=c_other_points, linestyle="--", zorder=0, linewidth=size)
    ax1.plot([auto_min_val, maximum_value], [maximum_value, maximum_value],
             c=c_other_points, linestyle="--", zorder=0, linewidth=size)

    # Timeout points
    ax1.scatter([timeout_val]*len(timeout_x), y_data[timeout_x],
                marker=timeout_marker, c=c_other_points)
    ax1.scatter([timeout_val]*len(timeout_both), [timeout_val]*len(timeout_both),
                marker=timeout_marker, c=c_other_points)
    ax1.scatter(x_data[timeout_y], [timeout_val]*len(timeout_y),
                marker=timeout_marker, c=c_other_points)

    # Plot timeout line
#    ax1.plot([timeout_val, timeout_val], [auto_min_val, timeout_val],
#             c=c_other_points, linestyle=":", zorder=0)
#    ax1.plot([auto_min_val, timeout_val], [timeout_val, timeout_val],
#             c=c_other_points, linestyle=":", zorder=0)

    if debug:
        # debug option
        ax1.scatter(x_data, y_data, marker="o", facecolor="", s=50,
                    label="original data")

    # Set axes scale and limits
    ax1.set_xscale("log")
    ax1.set_yscale("log")

    # Set axes labels
    ax1.set_xlabel(labels[0], fontsize=label_size)
    ax1.set_ylabel(labels[1], fontsize=label_size)

    if debug:
        # Plot legend
        leg = ax1.legend(loc='best', fancybox=True)
        leg.get_frame().set_alpha(0.5)

    # Save or show figure
    tight_layout()
    subplots_adjust(top=0.85)
    
    max_val = timeout_val*2
    auto_min_val *= 0.9
    ax1.set_autoscale_on(False)
    if max_val is not None and min_val is None:
        # User sets max val
        ax1.set_ylim([auto_min_val, max_val])
        ax1.set_xlim(ax1.get_ylim())
    elif max_val > min_val and max_val is not None and min_val is not None:
        # User sets both, min and max -val
        ax1.set_ylim([min_val, max_val])
        ax1.set_xlim(ax1.get_ylim())
    else:
        # User sets nothing
        ax1.set_xlim([auto_min_val, max_val])
        ax1.set_ylim(ax1.get_xlim())

    # Plot maximum value as tick
    if int(maximum_value) == maximum_value:
        maximum_value = int(maximum_value)
        maximum_str = r"$%d$" % maximum_value
    else:
        maximum_str = r"$%5.2f$" % maximum_value

    if int(np.log10(maximum_value)) != np.log10(maximum_value):
        # If we do not already have this ticklabel as a regular label
        ax1.text(ax1.get_ylim()[0] - 0.1 * np.abs(ax1.get_ylim()[0]),
                 maximum_value,
                 maximum_str,
                 horizontalalignment='right', verticalalignment="center",
                 fontsize=user_fontsize)
        ax1.text(maximum_value,
                 ax1.get_ylim()[0] - 0.1 * np.abs(ax1.get_ylim()[0]),
                 maximum_str,
                 horizontalalignment='center', verticalalignment="top",
                 fontsize=user_fontsize)

    # Plot 'timeout'
    ax1.text(ax1.get_xlim()[0] - 0.1 * np.abs(ax1.get_ylim()[0]),
             timeout_val,
             "timeout ", horizontalalignment='right',
             verticalalignment="center", fontsize=user_fontsize)
    ax1.text(timeout_val,
             ax1.get_ylim()[0] - 0.1 * np.abs(ax1.get_ylim()[0]),
             "timeout ",  horizontalalignment='center', verticalalignment="top",
             fontsize=user_fontsize, rotation=45)

    #########
    # Adjust ticks > max_val
    ax1.xaxis.set_ticks_position('bottom')
    ax1.yaxis.set_ticks_position('left')
    # major axes
    for tic in ax1.xaxis.get_major_ticks():
        if tic._loc > maximum_value:
            tic.tick1On = tic.tick2On = False
    for tic in ax1.yaxis.get_major_ticks():
        if tic._loc > maximum_value:
            tic.tick1On = tic.tick2On = False

    # minor axes
    for tic in ax1.xaxis.get_minor_ticks():
        if tic._loc > maximum_value:
            tic.tick1On = tic.tick2On = False
    for tic in ax1.yaxis.get_minor_ticks():
        if tic._loc > maximum_value:
            tic.tick1On = tic.tick2On = False

    # tick labels
    ticks_x = ax1.get_xticks()
    new_ticks_label = list()
    for l_idx in range(len(ticks_x)):
        if ticks_x[l_idx] < maximum_value:
            new_ticks_label.append(ticks_x[l_idx])
    ax1.set_xticklabels(new_ticks_label)  # , rotation=45)

    ticks_y = ax1.get_yticks()
    new_ticks_label = list()
    for l_idx in range(len(ticks_y)):
        if ticks_x[l_idx] < maximum_value:
            if 0 < ticks_x[l_idx] < 1:
                new_ticks_label.append(str(r"$10^{%d}$" % int(np.log10(ticks_x[l_idx]))))
            if 1 <= ticks_x[l_idx] < 1000:
                new_ticks_label.append(str(r"$%d^{ }$" % int(ticks_x[l_idx])))
            if 1000 <= ticks_x[l_idx]:
                new_ticks_label.append(str(r"$10^{%d}$" % int(np.log10(ticks_x[l_idx]))))
    ax1.set_yticklabels(new_ticks_label)  # , rotation=45)
    ax1.set_xticklabels(new_ticks_label)

    # Change fontsize for ticklabels
    setp(ax1.get_yticklabels(), fontsize=ticklabel_size)
    setp(ax1.get_xticklabels(), fontsize=ticklabel_size)
    tight_layout()
    if save != "":
        savefig(save, dpi=dpi, facecolor='w', edgecolor='w',
                orientation='portrait', papertype=None, format=None,
                transparent=False, pad_inches=0.02, bbox_inches='tight')
    else:
        show()

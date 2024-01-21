# Le module contient des fonctions pour générer des timelines pour la visualisation des faits et procédures.
import subprocess
from datetime import date

from matplotlib import pyplot as plt
import numpy as np

# TODO transformer la fonction en classe.

def build_timeline(dates:dict, plot_title:str, output_filepath:str=None):

    min_date = date(np.min(list(dates.keys())).year - 2, np.min(list(dates.keys())).month, np.min(list(dates.keys())).day)
    max_date = date(np.max(list(dates.keys())).year + 2, np.max(list(dates.keys())).month, np.max(list(dates.keys())).day)

    # Textes/évènements associés aux dates.
    labels = ['{0:%d %b %Y}:\n{1}'.format(d, l) for d, l in dates.items()]

    fig, ax = plt.subplots(figsize=(15, 4), constrained_layout=True)
    _ = ax.set_ylim(-2, 1.75)
    _ = ax.set_xlim(min_date, max_date)
    _ = ax.axhline(0, xmin=0.05, xmax=0.95, c='deeppink', zorder=1)

    _ = ax.scatter(dates.keys(), np.zeros(len(dates.keys())), s=120, c='palevioletred', zorder=2)
    _ = ax.scatter(dates.keys(), np.zeros(len(dates.keys())), s=30, c='darkmagenta', zorder=3)

    label_offsets = np.zeros(len(dates.keys()))
    label_offsets[::2] = 0.35
    label_offsets[1::2] = -0.7
    for i, (d, l) in enumerate(dates.items()):
        _ = ax.text(d, label_offsets[i], l, ha='center', fontfamily='serif', fontweight='bold', color='royalblue',fontsize=12)

        stems = np.zeros(len(dates.keys()))
    stems[::2] = 0.3
    stems[1::2] = -0.3
    # markerline, stemline, baseline = ax.stem(dates, stems, use_line_collection=True)
    markerline, stemline, baseline = ax.stem(dates.keys(), stems)
    _ = plt.setp(markerline, marker=',', color='darkmagenta')
    _ = plt.setp(stemline, color='darkmagenta')

    # Cacher les lignes extérieures.
    for spine in ["left", "top", "right", "bottom"]:
        _ = ax.spines[spine].set_visible(False)

    # Cacher les ticks.
    _ = ax.set_xticks([])
    _ = ax.set_yticks([])

    _ = ax.set_title(plot_title, fontweight="bold", fontfamily='serif', fontsize=16,
                    color='royalblue')

    if output_filepath:
        # Exporter la timaline.
        plt.savefig(output_filepath)
        subprocess.run(('xclip', '-selection', 'clipboard',  '-t', 'image/png', '-i', output_filepath))


# Définir une fonction interactive de construction de timelines.
def run_timeline_maker(output_filepath:str):
    dates = {}
    while True:
        raw_input = input('Enter date dd/mm/yyyy and event separated by coma.')
        if raw_input.strip().lower() in ['q', 'quit']:
            break
        date, event = raw_input.split(',')
        date = [int(_) for _ in date.strip().split('/')]
        date.reverse()
        event = event.strip()
        dates[date(*date)] = event

    title = input('Enter plot title.')

    build_timeline(dates, title, output_filepath)

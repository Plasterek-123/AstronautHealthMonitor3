import flet as ft
from .common import metric, note

def build(ctx):
    r = ctx.current
    return ft.Column(spacing=9, controls=[metric('Breathing depth (tidal volume)', f"{r['tidal_volume']:.6f}", 'm³'), metric('Respiratory rate', r['breath'], 'breaths/min'), metric('Irregular breathing rhythm', 'Yes' if r['irregular_breathing'] else 'No'), metric('Breathing difficulty', 'Yes' if r['breathing_difficulty'] else 'No'), note('Irregular breathing rhythm is separate from a cardiac arrhythmia diagnosis.')])

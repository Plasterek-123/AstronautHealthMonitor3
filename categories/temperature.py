import flet as ft
from config import CYAN
from overlays import thermal_legend_svg
from .common import metric, note

def build(ctx):
    r = ctx.current
    selected = ctx.state.setdefault('limb', 'Left arm')
    limb = ft.Dropdown(label='Selected limb', value=selected, options=[ft.DropdownOption(key=n) for n in ('Left arm', 'Right arm', 'Left leg', 'Right leg')], on_select=lambda e: choose(ctx, e.control.value))
    return ft.Column(spacing=9, controls=[metric('Average body temperature', f"{r['temp']:.1f}", '°C'), limb, metric(selected, f"{r['limb_temp']:.1f}", '°C'), ft.Image(src=thermal_legend_svg(), width=300, height=65, fit=ft.BoxFit.CONTAIN), note('Fixed color scale: 30–40 °C. Colors show temperature, not a risk threshold.')])

def txt_legend():
    from config import txt
    return txt('Cooler  ● blue → amber → red ●  Warmer', 12, CYAN)

def choose(ctx, value):
    ctx.state['limb'] = value
    ctx.refresh_details()
    ctx.refresh_overlay()
    ctx.page.update()

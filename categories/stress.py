import math
import flet as ft
from config import txt, GRAY, WHITE, CYAN
from logic import stress_label
from .common import metric, note, trend_svg

def build(ctx):
    r = ctx.current
    scale = ctx.state.setdefault('stress_window', 'Hours')
    samples = 24 if scale == 'Hours' else 7
    values = [max(0, min(100, r['stress'] + 14 * math.sin(i * 0.7) - 5 * math.cos(i * 0.4))) for i in range(samples)]

    def window(name):
        ctx.state['stress_window'] = name
        ctx.refresh_details()
        ctx.page.update()
    return ft.Column(spacing=9, controls=[metric('Stress score', r['stress'], '/ 100'), metric('Level', stress_label(r['stress'])), ft.Row(controls=[ctx.live_metric('hr', 'Heart rate', r['hr'], 'BPM'), ctx.live_metric('breath', 'Breathing', r['breath'], '/min')], wrap=True), ft.Row(controls=[ft.Button(content=n, on_click=lambda e, x=n: window(x)) for n in ('Hours', 'Week')]), txt('Last 24 hours' if scale == 'Hours' else 'Last 7 days', 13, WHITE, True), ft.Image(src=trend_svg(values), width=310, height=130, fit=ft.BoxFit.CONTAIN), note('0–29 Low · 30–59 Normal · 60–79 Medium · 80–100 High'), note('Score derived from heart and respiratory rates. Historical points are generated examples, not recorded measurements.')])

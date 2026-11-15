import flet as ft
from config import txt, box, WHITE, GRAY, CYAN
from logic import ecg_svg
from .common import metric, note

def build(ctx):
    r = ctx.current
    ctx.detail_ecg = ft.Image(src=ecg_svg(ctx.state['tick'], r['hr'], width=600, height=150), height=135, fit=ft.BoxFit.FILL, gapless_playback=True)
    return ft.Column(spacing=12, horizontal_alignment=ft.CrossAxisAlignment.STRETCH, controls=[ft.Row(wrap=True, controls=[ctx.live_metric('hr', 'Heart rate', r['hr'], 'BPM'), ctx.live_metric('pressure', 'Blood pressure', r['pressure'], 'mmHg')]), box(ft.Column(spacing=8, controls=[txt('ECG', 12, CYAN, True), ctx.detail_ecg]), 12), note('Blood pressure is displayed without automatic clinical interpretation.')])

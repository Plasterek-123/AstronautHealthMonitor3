import flet as ft
from config import txt, GREEN, RED, CYAN, WHITE
from .common import metric, note
from .sleep_chart import sleep_chart

def build(ctx):
    r = ctx.current
    good = r['sleep_quality'] == 'Good'
    return ft.Column(spacing=12, horizontal_alignment=ft.CrossAxisAlignment.STRETCH, controls=[ft.Row(controls=[ft.Icon(ft.Icons.CHECK_CIRCLE if good else ft.Icons.WARNING_AMBER, color=GREEN if good else RED), txt(r['sleep_quality'] + ' sleep', 18, GREEN if good else RED, True)]), note('Summary considers duration, awakenings and the deep-sleep share in the demo scenario.'), metric('Estimated sleep duration', r['sleep'], 'h'), metric('Awakenings', r['awakenings']), *[txt(f'{name}: {value}%', 13, color, True) for name, value, color in zip(('Light', 'Deep', 'REM'), r['sleep_stages'], (CYAN, '#C1B1FF', GREEN))], note('Light: the body settles and activity usually decreases.'), note('Deep: typically slower heart rate and low movement.'), note('REM: active brain, changing heart rhythm and reduced muscle tone.')])

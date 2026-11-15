import math
import flet as ft
from config import box, txt, WHITE, GRAY, CYAN, YELLOW, GREEN, RED
from crew import current_readings, persist_crew, CREW, is_own_profile, CREW_ALERT_SCENARIOS, set_crew_alert_scenario

def build_settings_screen(state, page, change_mode, toggle_pause):
    if not is_own_profile(state):
        return box(ft.Column(spacing=12, controls=[txt('Private profile', 21, WHITE, True), txt('Manual measurements and settings are available only for your own profile. Select Crew member 01 to edit your data.', 14, GRAY)]))
    demo_sex = state['nutrition_profile'].get('sex', 'Male')
    demo = ft.Dropdown(label='Astronaut profile', value=demo_sex, options=[ft.DropdownOption(key='Male', text='Astronaut Alex · Male'), ft.DropdownOption(key='Female', text='Astronaut Maya · Female')])

    def choose_demo(e):
        sex = e.control.value
        state['nutrition_profile'] = {**state['nutrition_profile'], **(dict(sex='Female', weight=62.0, height=168.0, age=32, activity=1.55) if sex == 'Female' else dict(sex='Male', weight=75.0, height=178.0, age=30, activity=1.55))}
        state['nutrition_targets'] = {}
        try:
            persist_crew(state)
        except OSError:
            feedback.value = 'Could not save profile.'
            feedback.color = RED
            page.update()
            return
        change_mode(state['mode'])
        feedback.value = 'Astronaut profile changed.'
        feedback.color = GREEN
        page.update()
    demo.on_select = choose_demo
    status = txt('Running' if state['running'] else 'Paused', 13, CYAN)
    selected = txt('Current scenario: ' + state['mode'], 13, CYAN)
    feedback = txt('', 12, GREEN)
    r = current_readings(state)
    specs = [('hr', 'Heart rate (BPM)', 20, 250), ('breath', 'Respiratory rate (/min)', 1, 80), ('spo2', 'SpO2 (%)', 0, 100), ('temp', 'Body temperature (°C)', 25, 45), ('limb_temp', 'Limb temperature (°C)', 10, 45), ('tidal_volume', 'Breathing depth (m³)', 1e-05, 0.01), ('stress', 'Stress score (0–100)', 0, 100), ('sleep', 'Sleep duration (h)', 0, 24), ('awakenings', 'Awakenings', 0, 50), ('absorbed_dose', 'Absorbed dose (Gy)', 0, 10)]
    fields = {key: ft.TextField(label=label, value=str(r[key]), col={'xs': 12, 'sm': 6, 'md': 4}, keyboard_type=ft.KeyboardType.NUMBER) for key, label, _, _ in specs}
    pressure = ft.TextField(label='Blood pressure (e.g. 110/70)', value=r['pressure'])
    stages = [ft.TextField(label=n + ' sleep (%)', value=str(v), col={'xs': 12, 'sm': 4}, keyboard_type=ft.KeyboardType.NUMBER) for n, v in zip(('Light', 'Deep', 'REM'), r['sleep_stages'])]
    difficulty = ft.Checkbox(label='Breathing difficulty', value=r['breathing_difficulty'])
    irregular = ft.Checkbox(label='Irregular breathing', value=r['irregular_breathing'])
    external = ft.Dropdown(label='External radiation scenario', value=r['external_level'], options=[ft.DropdownOption(key=n, text=n.replace(' (demo)', '')) for n in ('Nominal (demo)', 'Elevated (demo)', 'External alert (demo)')])
    source = ft.Switch(label='Use manual measurements', value=bool(state.get('manual_enabled')))

    def save(e):
        try:
            values = {key: float(field.value) for key, field in fields.items()}
            for key, label, low, high in specs:
                if not math.isfinite(values[key]) or not low <= values[key] <= high:
                    raise ValueError(label + f': enter {low:g}–{high:g}.')
            if not values['awakenings'].is_integer():
                raise ValueError('Awakenings must be a whole number.')
            for key in ('hr', 'spo2', 'stress', 'awakenings'):
                values[key] = round(values[key])
            bp = [int(x.strip()) for x in (pressure.value or '').split('/')]
            if len(bp) != 2 or not 40 <= bp[1] < bp[0] <= 300:
                raise ValueError('Enter systolic/diastolic pressure, e.g. 110/70.')
            shares = [float(f.value) for f in stages]
            if not all((math.isfinite(v) and 0 <= v <= 100 for v in shares)) or abs(sum(shares) - 100) > 0.01:
                raise ValueError('Sleep stages must total 100%.')
            values.update(pressure=f'{bp[0]}/{bp[1]}', sleep_stages=shares, breathing_difficulty=bool(difficulty.value), irregular_breathing=bool(irregular.value), external_level=external.value, solar_event='Manual external alert' if external.value == 'External alert (demo)' else 'No event in manual scenario')
            state['manual_values'] = values
            state['manual_enabled'] = bool(source.value)
            persist_crew(state)
            change_mode(state['mode'])
            feedback.value = 'Saved for ' + CREW.get(state.get('crew_id'), 'selected crew member')
            feedback.color = GREEN
            page.update()
        except (ValueError, TypeError, OSError) as error:
            feedback.value = str(error) or 'Check the entered values.'
            feedback.color = RED
            page.update()

    def mode(name):
        state['manual_enabled'] = False
        source.value = False
        change_mode(name)
        feedback.value = 'Scenario applied to your monitoring profile.'
        feedback.color = GREEN
        selected.value = 'Current scenario: ' + name
        page.update()

    def pause(e):
        toggle_pause()
        status.value = 'Running' if state['running'] else 'Paused'
        page.update()
    crew_target = ft.Dropdown(label='Crew member', value='crew_02',
        options=[ft.DropdownOption(key=k, text=v) for k,v in CREW.items()
                 if k != state.get('own_crew_id', 'crew_01')])
    crew_feedback = txt('', 12, CYAN)

    def crew_scenario(name):
        try:
            set_crew_alert_scenario(state, crew_target.value, name)
            change_mode(state['mode'])
            crew_feedback.value = CREW[crew_target.value] + ': ' + name
            crew_feedback.color = GREEN if name == 'Clear alerts' else YELLOW
        except (ValueError, OSError) as error:
            crew_feedback.value = str(error)
            crew_feedback.color = RED
        page.update()

    crew_controls = box(ft.Column(spacing=12, controls=[
        txt('Crew alert controls', 18, WHITE, True),
        txt('Critical events appear in Crew and in the alert bell.', 12, GRAY),
        crew_target,
        ft.Row(wrap=True, controls=[ft.Button(content=n,
            on_click=lambda e, name=n: crew_scenario(name))
            for n in (*CREW_ALERT_SCENARIOS, 'Clear alerts')]), crew_feedback]))
    return ft.Column(spacing=16, horizontal_alignment=ft.CrossAxisAlignment.STRETCH, controls=[txt('Settings', 23, WHITE, True), box(ft.Column(spacing=10, controls=[txt('Astronaut profile', 18, WHITE, True), demo])), box(ft.Column(spacing=12, controls=[txt('Measurement controls', 18, WHITE, True), txt('Scenarios for your profile', 12, GRAY), selected, ft.Row(wrap=True, controls=[ft.Button(content=n, on_click=lambda e, x=n: mode(x)) for n in ('Normal', 'Calm day', 'Light activity', 'Short sleep', 'Busy day', 'Warning', 'Alert')]), ft.Button(content='Pause / resume monitoring', icon=ft.Icons.PAUSE, on_click=pause), status])), crew_controls, box(ft.Column(spacing=14, controls=[txt('Manual measurements · ' + CREW.get(state.get('crew_id'), 'Crew'), 18, WHITE, True), source, ft.ResponsiveRow(controls=list(fields.values())), pressure, ft.ResponsiveRow(controls=stages), ft.Row(wrap=True, controls=[difficulty, irregular]), external, ft.Button(content='Save measurements and source', icon=ft.Icons.SAVE, on_click=save), feedback]))])

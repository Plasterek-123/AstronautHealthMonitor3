"""Stable nutrition workspace: updates values without rebuilding the page."""
from datetime import date
import math
import flet as ft
from config import txt, box, WHITE, GRAY, CYAN, GREEN, YELLOW, RED, CARD, PANEL, BORDER, STATUS_COLOR
from logic import nutrient_targets, nutrition_totals, FOOD_CATALOG, NUTRIENT_UNITS
from minerals import MINERALS, assess_mineral, convert_amount

def build(ctx):
    state = ctx.state
    feedback = txt('', 12, GREEN)
    consumed = txt('', 25, WHITE, True)
    remaining = txt('', 18, CYAN, True)
    ratio = txt('', 12, GRAY)
    calories_bar = ft.ProgressBar(value=0, color=CYAN, bgcolor=CARD, height=7)
    macros = ft.ResponsiveRow(spacing=10, run_spacing=10)
    mineral_grid = ft.ResponsiveRow(spacing=10, run_spacing=10)
    history = ft.Column(spacing=8)
    vitamins = ft.Column(spacing=12)
    log_count = txt('', 12, GRAY)
    code = ft.TextField(label='Package code', hint_text='DEMO001 or DEMO002', col={'xs': 8, 'sm': 9})
    servings = ft.TextField(label='Servings', value='1', col={'xs': 4, 'sm': 3}, keyboard_type=ft.KeyboardType.NUMBER)

    def message(value, error=False):
        feedback.value = value
        feedback.color = RED if error else GREEN
        ctx.page.update()

    def commit(entry):
        state['nutrition_entries'].append(entry)
        try:
            ctx.persist_nutrition()
        except OSError:
            state['nutrition_entries'].pop()
            message('Could not save intake.', True)
            return
        refresh()
        message('Added ' + entry['name'] + '.')

    def add_food(e=None, quick=None):
        lookup = (quick or code.value or '').strip().upper()
        product = FOOD_CATALOG.get(lookup)
        try:
            count = float(servings.value)
            if not product:
                raise ValueError('Unknown code. Use DEMO001 or DEMO002.')
            if not math.isfinite(count) or not 0 < count <= 20:
                raise ValueError('Enter 0–20 servings, greater than zero.')
            commit(dict(date=date.today().isoformat(), code=lookup, name=product['name'], servings=count, **{k: product[k] * count for k in NUTRIENT_UNITS if k in product}))
        except (ValueError, TypeError) as error:
            message(str(error), True)
    mineral = ft.Dropdown(label='Mineral', value='calcium', options=[ft.DropdownOption(key=k, text=v['name']) for k, v in MINERALS.items()])
    amount = ft.TextField(label='Amount', keyboard_type=ft.KeyboardType.NUMBER)
    unit = ft.Dropdown(label='Unit', value='mg', options=[ft.DropdownOption(key=n) for n in ('g', 'mg', 'µg')])
    source = ft.Dropdown(label='Source', value='food', options=[ft.DropdownOption(key=n) for n in ('food', 'supplement')])

    def add_mineral(e):
        try:
            key = mineral.value
            r = MINERALS[key]
            value = convert_amount(amount.value, unit.value, r['unit'])
            if value <= 0:
                raise ValueError('Enter a positive amount.')
            commit(dict(date=date.today().isoformat(), name=r['name'] + ' (' + source.value + ')', source=source.value, single_mineral=key, **{key: value}))
        except (ValueError, TypeError) as error:
            message(str(error), True)
    profile = state['nutrition_profile']
    fields = {k: ft.TextField(label=label, value=str(profile[k]), col={'xs': 12, 'sm': 6}) for k, label in (('weight', 'Body mass (kg)'), ('height', 'Height (cm)'), ('age', 'Age (years)'), ('activity', 'Activity factor'))}
    sex = ft.Dropdown(label='Sex used by reference', value=profile['sex'], options=[ft.DropdownOption(key=x) for x in ('Male', 'Female')])
    target = ft.TextField(label='Daily calorie target (kcal)', value=str(state.get('nutrition_targets', {}).get('calories', nutrient_targets(profile)['calories'])))

    def save_profile(e):
        try:
            values = {k: float(f.value) for k, f in fields.items()}
            for key, low, high in (('weight', 20, 300), ('height', 100, 250), ('age', 19, 100), ('activity', 1, 3)):
                if not math.isfinite(values[key]) or not low <= values[key] <= high:
                    raise ValueError('Check ' + key + '.')
            kcal = float(target.value)
            if not math.isfinite(kcal) or not 500 <= kcal <= 10000:
                raise ValueError('Calorie target: 500–10000 kcal.')
            values['sex'] = sex.value
            old_profile, old_targets = (state['nutrition_profile'], state.get('nutrition_targets', {}))
            state['nutrition_profile'] = values
            state['nutrition_targets'] = {'calories': kcal}
            try:
                ctx.persist_nutrition()
            except OSError:
                state['nutrition_profile'] = old_profile
                state['nutrition_targets'] = old_targets
                raise
            refresh()
            ctx.refresh_camera()
            message('Profile and target saved.')
        except (ValueError, TypeError, OSError) as error:
            message(str(error), True)

    def estimate(e):
        try:
            values = {k: float(f.value) for k, f in fields.items()}
            values['sex'] = sex.value
            if not all((math.isfinite(v) for k, v in values.items() if k != 'sex')):
                raise ValueError
            target.value = str(nutrient_targets(values)['calories'])
            ctx.page.update()
        except (ValueError, TypeError):
            message('Enter valid profile values first.', True)
    sections = {'Overview': ft.Column(spacing=12, controls=[txt('Daily balance', 17, WHITE, True), macros, txt('Vitamins', 16, WHITE, True), vitamins, txt('Values describe logged intake. Missing food composition is not treated as a complete dietary record.', 12, GRAY)]), 'Food log': ft.Column(spacing=12, controls=[txt('Add a meal', 17, WHITE, True), box(ft.Column(spacing=10, controls=[ft.ResponsiveRow(controls=[code, servings]), ft.Button(content='Add food', icon=ft.Icons.ADD, on_click=add_food), ft.Row(wrap=True, controls=[ft.TextButton(content='Mission meal A', on_click=lambda e: add_food(quick='DEMO001')), ft.TextButton(content='Recovery snack', on_click=lambda e: add_food(quick='DEMO002'))])])), txt("Today's intake", 16, WHITE, True), log_count, history]), 'Minerals': ft.Column(spacing=12, controls=[txt('Mineral intake', 17, WHITE, True), txt('Age- and sex-based US adult references. UL and daily intake targets are separate. Missing composition stays incomplete.', 12, GRAY), ft.ExpansionTile(title=txt('Log a mineral amount', 14, WHITE, True), controls=[mineral, amount, unit, source, ft.Button(content='Add mineral intake', icon=ft.Icons.ADD, on_click=add_mineral)]), mineral_grid]), 'Profile': ft.Column(spacing=12, controls=[txt('Personal targets', 17, WHITE, True), ft.ResponsiveRow(controls=list(fields.values())), sex, target, ft.Row(wrap=True, controls=[ft.TextButton(content='Estimate calories', on_click=estimate), ft.Button(content='Save profile', icon=ft.Icons.SAVE, on_click=save_profile)]), txt('Mifflin–St Jeor × activity factor is an editable demo estimate. No accelerometer is connected.', 11, GRAY)])}
    active = state.get('nutrition_section', 'Overview')
    active = active if active in sections else 'Overview'
    host = ft.Container(content=sections[active])
    tabs = {}

    def select(name):
        state['nutrition_section'] = name
        host.content = sections[name]
        for key, tab in tabs.items():
            tab.bgcolor = CARD if key == name else PANEL
        ctx.page.update()
    for name in sections:
        tabs[name] = ft.Container(padding=ft.Padding.symmetric(horizontal=13, vertical=9), border_radius=9, bgcolor=CARD if name == active else PANEL, ink=True, on_click=lambda e, n=name: select(n), content=txt(name, 12, WHITE, True))

    def refresh():
        totals = nutrition_totals(state['nutrition_entries'])
        targets = nutrient_targets(state['nutrition_profile'])
        targets.update(state.get('nutrition_targets', {}))
        kcal = totals['calories']
        goal = targets['calories']
        left = goal - kcal
        consumed.value = f'{kcal:g} kcal'
        remaining.value = f'{abs(left):g} kcal ' + ('remaining' if left >= 0 else 'above target')
        ratio.value = f'{kcal / max(1, goal) * 100:.0f}% of {goal:g} kcal daily target'
        calories_bar.value = min(1, kcal / max(1, goal))
        macros.controls = []
        for key in ('protein', 'carbs', 'fat', 'fiber'):
            value, aim = (totals[key], targets[key])
            macros.controls.append(ft.Container(col={'xs': 6, 'sm': 6}, content=box(ft.Column(spacing=7, controls=[txt(key.title(), 12, GRAY), txt(f'{value:g} g', 21, WHITE, True), ft.ProgressBar(value=min(1, value / max(1, aim)), color=CYAN, bgcolor=PANEL), txt(f'of {aim:g} g', 11, GRAY)]), 12)))
        vitamins.controls = []
        for key in ('vitamin_c', 'vitamin_d'):
            value, aim = (totals[key], targets[key])
            vitamins.controls.append(ft.Column(spacing=5, controls=[ft.Row(controls=[ft.Container(expand=True, content=txt(key.replace('_', ' ').title(), 13, WHITE)), txt(f'{value:g} / {aim:g} {NUTRIENT_UNITS[key]}', 12, CYAN)]), ft.ProgressBar(value=min(1, value / max(1, aim)), color=CYAN, bgcolor=CARD)]))
        mineral_grid.controls = []
        for key in MINERALS:
            a = assess_mineral(key, state['nutrition_profile'], state['nutrition_entries'], date.today().isoformat() in state.get('nutrition_closed_days', []))
            ref = a['reference']
            v = a['intake']['total']
            aim = ref['target']
            color = STATUS_COLOR[a['status']]
            limit = 'UL not established' if ref['upper'] is None else f"{ref.get('limit_kind', 'UL')} {ref['upper']:g} {ref['unit']}" + (' · supplements only' if ref.get('scope') else '')
            mineral_grid.controls.append(ft.Container(col={'xs': 12, 'sm': 6, 'lg': 6}, content=box(ft.Column(spacing=4, controls=[ft.Row(controls=[ft.Container(width=32, height=32, bgcolor=CARD, border_radius=8, alignment=ft.Alignment.CENTER, content=txt(ref['symbol'], 13, CYAN, True)), txt(ref['name'], 13, WHITE, True)]), txt(f"{v:g} {ref['unit']}", 18, WHITE, True), txt(f"Daily {ref['kind']}: {aim:g} {ref['unit']}", 11, GRAY), ft.ProgressBar(value=min(1, v / aim), color=color, bgcolor=CARD), txt(a['label'], 11, color), txt(limit, 10, GRAY)]), 9)))
        today = [e for e in state['nutrition_entries'] if e.get('date') == date.today().isoformat()]
        log_count.value = f'{len(today)} entries'
        history.controls = []
        for entry in reversed(today):

            def remove(e, item=entry):
                old = list(state['nutrition_entries'])
                state['nutrition_entries'].remove(item)
                try:
                    ctx.persist_nutrition()
                except OSError:
                    state['nutrition_entries'] = old
                    message('Could not save intake log.', True)
                    return
                refresh()
                message('Entry removed.')
            detail = f"{entry.get('calories', 0):g} kcal" if not entry.get('single_mineral') else f"{entry[entry['single_mineral']]:g} {MINERALS[entry['single_mineral']]['unit']}"
            history.controls.append(box(ft.Row(controls=[ft.Container(expand=True, content=ft.Column(spacing=3, controls=[txt(entry.get('name', 'Intake'), 13, WHITE, True), txt(detail, 12, CYAN)])), ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, tooltip='Remove entry', on_click=remove)]), 10))
        if not today:
            history.controls = [txt('No food logged today. Add a meal above.', 13, GRAY)]
    review_label = txt('', 11, YELLOW)

    def review_day(e):
        day = date.today().isoformat()
        days = state.setdefault('nutrition_closed_days', [])
        if day in days:
            days.remove(day)
        else:
            days.append(day)
        try:
            ctx.persist_nutrition()
        except OSError:
            message('Could not save daily review.', True)
            return
        refresh()
        message('Daily review updated. Lower intake is a noncritical reminder, not a deficiency diagnosis.')
    review = ft.TextButton(content='Review end-of-day targets', on_click=review_day)
    sections['Overview'].controls.extend([review, review_label])
    original_refresh = refresh

    def refresh():
        original_refresh()
        review_label.value = 'Daily review on · low logged intake appears in Attention alerts.' if date.today().isoformat() in state.get('nutrition_closed_days', []) else 'Low-intake reminders start after end-of-day review. Missing composition stays unassessed.'
    refresh()
    return ft.Column(spacing=14, horizontal_alignment=ft.CrossAxisAlignment.STRETCH, controls=[box(ft.Column(spacing=10, controls=[txt('DAILY ENERGY', 11, CYAN, True), ft.Row(wrap=True, spacing=24, controls=[consumed, remaining]), calories_bar, ratio])), ft.Row(spacing=5, scroll=ft.ScrollMode.AUTO, controls=list(tabs.values())), feedback, host])

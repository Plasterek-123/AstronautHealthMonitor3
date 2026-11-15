import flet as ft
from config import txt,box,WHITE,GRAY,CYAN,RED,STATUS_COLOR
from logic import radiation_status
from radiation_calculator import RADIATION_WEIGHTS,TISSUE_WEIGHTS,UNITS,dose_values,add_tissue

def build(ctx):
    state=ctx.state;r=ctx.current;terms=state.setdefault('radiation_terms',{})
    ctx.daily_dose_control=txt(f"{r['absorbed_dose']*1e6:g} µGy",25,WHITE,True)
    dose=ft.TextField(label='Absorbed dose D',value=f"{r['absorbed_dose']*1e6:g}",dense=True,height=42,expand=3)
    unit=ft.Dropdown(value='µGy',options=[ft.DropdownOption(key=u) for u in UNITS],dense=True,height=42,expand=2)
    radiation=ft.Dropdown(label='Radiation type · wR',value=state.get('radiation_type','xray'),dense=True,height=48,
        options=[ft.DropdownOption(key=k,text=f'{name} · {weight:g}') for k,(name,weight) in RADIATION_WEIGHTS.items()])
    tissue=ft.Dropdown(label='Tissue / organ · wT',value=state.get('radiation_tissue','lungs'),dense=True,height=48,
        options=[ft.DropdownOption(key=k,text=f'{name} · {weight:g}') for k,(name,weight) in TISSUE_WEIGHTS.items()])
    basis=ft.Dropdown(value='Dose',dense=True,height=38,width=180,options=[ft.DropdownOption(key='Dose',text='Enter dose'),ft.DropdownOption(key='Energy',text='Energy / mass · D = E/m')])
    energy=ft.TextField(label='Absorbed energy (J)',value='0.000001',dense=True,height=42,expand=True)
    mass=ft.TextField(label='Mass (kg)',value='1',dense=True,height=42,expand=True)
    direct=ft.Row(spacing=8,controls=[dose,unit]);energy_row=ft.Row(visible=False,spacing=8,controls=[energy,mass])
    result=txt('',14,CYAN,True);total=txt('',13,WHITE,True);feedback=txt('',11,RED);feedback.visible=False
    def calculate(e=None):
        try:
            d,h,c=dose_values(dose.value,unit.value,radiation.value,tissue.value,
                energy.value if basis.value=='Energy' else None,mass.value if basis.value=='Energy' else None)
            state['radiation_type']=radiation.value;state['radiation_tissue']=tissue.value
            result.value=f'Hₜ = {h*1e6:g} µSv · wₜHₜ = {c*1e6:g} µSv'
            total.value=f'Σ wₜHₜ = {sum(terms.values())*1e6:g} µSv · {len(terms)} tissue(s)' if terms else f'D = {d:g} Gy'
            feedback.value='';feedback.visible=False;return c
        except (ValueError,TypeError,ZeroDivisionError):feedback.value='Check the dose, energy and mass values.';feedback.visible=True;return None
    def changed(e=None):
        direct.visible=basis.value=='Dose';energy_row.visible=not direct.visible;calculate();ctx.page.update()
    def append(e):
        value=calculate()
        if value is not None:
            try:add_tissue(terms,tissue.value,value);calculate()
            except ValueError as error:feedback.value=str(error);feedback.visible=True
        ctx.page.update()
    def clear(e):terms.clear();calculate();ctx.page.update()
    for control in (radiation,tissue,basis,unit):control.on_select=changed
    for control in (dose,energy,mass):control.on_change=changed
    calculate()
    return ft.Column(spacing=9,horizontal_alignment=ft.CrossAxisAlignment.STRETCH,controls=[
        box(ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN,controls=[
            ft.Column(spacing=2,controls=[txt('Daily absorbed dose',12,GRAY),ctx.daily_dose_control]),
            ft.Icon(ft.Icons.SHIELD_OUTLINED,color=STATUS_COLOR[radiation_status(r)],size=27)]),11),
        box(ft.Column(spacing=6,controls=[ft.Row(controls=[ft.Container(expand=True,content=txt('Calculator',16,WHITE,True)),basis]),direct,energy_row,radiation,tissue,
            txt('D = E/m · Hₜ = wR × D · E = Σ wT × Hₜ',11,GRAY),result,total,
            ft.Row(spacing=6,controls=[ft.TextButton(content='Add / update tissue',on_click=append),ft.TextButton(content='Clear sum',on_click=clear)]),feedback]),10)])

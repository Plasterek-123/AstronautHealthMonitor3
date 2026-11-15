"""Combined offline ICE contacts, procedure slots and interface assistant."""
import flet as ft
from config import BASE_DIR,txt,box,WHITE,GRAY,CYAN,YELLOW,RED,GREEN
from logic import read_json,write_json
def build_ice_screen(state,page):
    path=BASE_DIR/"ice_profile.json";profile=read_json(path,{})
    fields={k:ft.TextField(label=label,value=str(profile.get(k,"")),multiline=k=="notes",min_lines=2 if k=="notes" else 1)
            for k,label in (("contact","Medical / ICE contact"),("channel","Mission communication channel"),("notes","Approved procedures and important information"))}
    result=txt("Stored locally on this device.",12,GRAY)
    def save(e):
        try:write_json(path,{k:c.value or "" for k,c in fields.items()});result.value,result.color="ICE information saved.",GREEN
        except OSError:result.value,result.color="Could not save ICE information.",RED
        page.update()
    instructions=txt("Select a procedure to view its configured mission document.",13,GRAY)
    procedures=read_json(BASE_DIR/"data"/"mission_procedures.json",{})
    def choose(name):
        instructions.value=procedures.get(name,"No approved procedure is configured for this event. Use the mission's medical and emergency communication channel.");page.update()
    tip=txt("Select a topic for help with the interface.",13,GRAY)
    tips={"Monitoring":"Use the category rings or body areas. The left panel always shows the vital-sign overview.",
          "Alerts":"Alerts use the same categories as the rings above. Click an alert to select its category.",
          "Nutrition":"Edit your demonstration profile, then type a package code from the offline catalog to log food.",
          "Sleep":"Sleep stages and duration are simulated. No sleep classifier is connected."}
    def show_tip(name):tip.value=tips[name];page.update()
    return ft.Column(spacing=15,controls=[txt("ICE & Assistant",23,WHITE,True),
        box(ft.Column(spacing=11,controls=[txt("In case of emergency",18,RED,True),
            *fields.values(),ft.Button(content="Save ICE information",icon=ft.Icons.SAVE,on_click=save),result,
            ft.Row(wrap=True,controls=[ft.Button(content=n,on_click=lambda e,x=n:choose(x)) for n in ("Decompression","Cardiac emergency","Injury / bleeding")]),
            instructions,txt("No calls are made by this prototype.",12,YELLOW)])),
        box(ft.Column(spacing=10,controls=[txt("Health interface assistant",18,WHITE,True),
            ft.Row(wrap=True,controls=[ft.Button(content=k,on_click=lambda e,x=k:show_tip(x)) for k in tips]),tip]))])

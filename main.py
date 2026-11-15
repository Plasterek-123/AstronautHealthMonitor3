"""Health Assessment & Life Overview. Run: python main.py (Flet 1.1.2)."""
import asyncio
import time
from datetime import date
import flet as ft
from config import BG,PANEL,WHITE,GRAY,CYAN,DATA_DIR,txt
from logic import load_events,read_json,DEFAULT_PROFILE
from monitoring_view import build_monitoring_dashboard
from calendar_view import build_calendar_screen
from guidebook_view import build_guidebook_screen
from settings_view import build_settings_screen
from crew import initialize_crew
from brand import logo

def main(page:ft.Page):
    page.title="Health Assessment & Life Overview"
    page.theme_mode=ft.ThemeMode.DARK;page.bgcolor=BG;page.padding=0
    page.theme=ft.Theme(color_scheme_seed=CYAN,font_family="Segoe UI")
    page.window.width=1380;page.window.height=860
    page.window.min_width=360;page.window.min_height=500
    nutrition=read_json(DATA_DIR/"nutrition.json",{})
    profile={**DEFAULT_PROFILE,**nutrition.get("profile",{})}
    state={"tab":0,"category":None,"tick":0,"running":True,"mode":"Normal",
           "date":date.today(),"month":date.today().replace(day=1),"events":load_events(),
           "nutrition_profile":profile,"nutrition_entries":nutrition.get("entries",[]),
           "nutrition_targets":nutrition.get("targets",{})}
    initialize_crew(state,nutrition)
    def select_category(name):
        monitor.select(name)
        if state["tab"]!=0:open_tab(0)
        else:page.update()
    monitor=build_monitoring_dashboard(state,page,select_category)
    category_header=ft.Container(visible=state['tab']==0,padding=ft.Padding.symmetric(horizontal=14),
        content=ft.Column(spacing=0,controls=[monitor.category_bar,ft.Divider(height=4,color=PANEL)]))
    content=ft.Container(content=monitor.view,padding=ft.Padding.symmetric(horizontal=15,vertical=8),expand=True)
    other_scroll=ft.Column(expand=True,scroll=ft.ScrollMode.AUTO)
    def change_mode(mode):
        state["mode"]=mode;monitor.update();monitor.refresh_details();monitor.refresh_camera();page.update()
    def toggle_pause():
        state["running"]=not state["running"];monitor.update();page.update()
    def open_tab(index):
        state["tab"]=index;navigation.selected_index=index
        category_header.visible=index==0
        other_scroll.scroll=None if index==1 else ft.ScrollMode.AUTO
        if index==0:
            monitor.update();content.content=monitor.view
        else:
            builders={1:lambda:build_calendar_screen(state,page),2:lambda:build_guidebook_screen(state,page),
                      3:lambda:build_settings_screen(state,page,change_mode,toggle_pause)}
            other_scroll.controls=[builders[index]()];content.content=other_scroll
        fit();page.update()
    navigation=ft.NavigationBar(selected_index=0,bgcolor=PANEL,indicator_color="#233E58",
        on_change=lambda e:open_tab(e.control.selected_index),destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.MONITOR_HEART,label="Monitoring"),
            ft.NavigationBarDestination(icon=ft.Icons.CALENDAR_MONTH,label="Calendar"),
            ft.NavigationBarDestination(icon=ft.Icons.MENU_BOOK,label="Guidebook"),
            ft.NavigationBarDestination(icon=ft.Icons.SETTINGS,label="Settings"),
        ])
    page.navigation_bar=navigation
    title=txt("Health Assessment & Life Overview",23,WHITE,True)
    page.add(ft.Container(expand=True,gradient=ft.RadialGradient(
        center=ft.Alignment(0,-.05),radius=1.1,
        colors=["#11243C","#0E1A2E","#0A1322"],stops=[0,.52,1]),content=ft.SafeArea(expand=True,content=ft.Column(expand=True,spacing=0,controls=[
        ft.Container(padding=ft.Padding.only(left=20,right=20,top=12,bottom=5),content=ft.Column(spacing=2,controls=[
            ft.Row(controls=[logo(),ft.Container(expand=True,content=title),monitor.crew_button,monitor.bell]),
            txt("Health dashboard",11,GRAY)])),
        category_header,content,
    ]))))
    def fit(e=None):
        width=float(page.width or 1380)
        title.size=17 if width<600 else 23
        title.value="HALO" if width<600 else "Health Assessment & Life Overview"
        for destination,label in zip(navigation.destinations,('Monitor','Calendar','Guide','Settings') if width<600 else ('Monitoring','Calendar','Guidebook','Settings')):
            destination.label=label
        monitor.fit(width,float(page.height or 830))
        if e is not None:
            if state["tab"]==1:other_scroll.controls=[build_calendar_screen(state,page)]
            page.update()
    page.on_resize=fit;fit();page.update()
    async def sensor_loop():
        previous=time.perf_counter()
        reading_elapsed=0.
        while True:
            now=time.perf_counter();dt=min(.25,now-previous);previous=now
            transitioned=monitor.advance_transition(dt)
            bell_animated=monitor.animate_bell(dt)
            scan_animated=monitor.advance_scan(dt)
            updated_reading=False
            if state["running"]:
                reading_elapsed+=dt
                if reading_elapsed>=.35:
                    reading_elapsed%=.35
                    state["tick"]+=1
                    monitor.update()
                    updated_reading=True
                monitor.animate(dt)
            if scan_animated or bell_animated or updated_reading or (state['tab']==0 and (transitioned or (state['running'] and state.get('category') in ('Cardiology','Respiration','Stress','Radiation','Nutrition','Sleep')))):
                page.update()
            await asyncio.sleep(.025 if monitor.transition else .08)
    page.run_task(sensor_loop)

if __name__=="__main__":ft.run(main)

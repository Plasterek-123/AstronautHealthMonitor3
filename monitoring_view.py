"""Dashboard composition and per-session monitoring controller."""
import flet as ft
from config import *
from logic import readings,evaluate_alerts,ecg_svg,write_json
from overlays import body_svg,category_overlay
from categories import BUILDERS
from categories.sleep_chart import sleep_chart
from scan_art import scan_svg
from ui_icons import category_icon,custom_icon
from body_interaction import category_at
from minerals import mineral_alerts
from crew import CREW,current_readings,activate_crew,persist_crew,is_own_profile,critical_categories,crew_emergencies
from body_camera import FULL_BODY,frame_for,frame_svg,interpolate_frame

class MonitoringController:
    def __init__(self,state,page,on_select):
        self.state,self.page,self.on_select=state,page,on_select
        self.current=current_readings(state)
        self.statuses,self.alerts=evaluate_alerts(self.current)
        self.values={key:txt("",29 if key=="hr" else 19,WHITE,True) for key in ("hr","pressure","temp","spo2","radiation")}
        for value in self.values.values():value.no_wrap=True;value.max_lines=1
        self.badges={key:txt("",10,GREEN,True) for key in self.values}
        self.summary=txt("",12,GREEN,True)
        self.category_controls={}
        self.detail_values={}
        self.transition=None
        self.camera=FULL_BODY
        self.outgoing_source=None
        self.details=ft.Column(expand=True,scroll=ft.ScrollMode.AUTO,spacing=10,horizontal_alignment=ft.CrossAxisAlignment.STRETCH)
        self.alert_list=ft.Column(expand=True,scroll=ft.ScrollMode.AUTO,spacing=7)
        self.alert_filter=None;self.alert_signature=None
        self.alert_tab="all";self.critical_count=0;self.bell_phase=0.
        self.ecg=ft.Image(src=ecg_svg(0,72),height=85,fit=ft.BoxFit.CONTAIN,gapless_playback=True)
        self.live=txt("MONITORING",11,CYAN,True)
        self.overlay=ft.Image(src=category_overlay(None,self.current,state),fit=ft.BoxFit.FILL,gapless_playback=True)
        self.outgoing_overlay=ft.Image(src=category_overlay(None,self.current,state),fit=ft.BoxFit.FILL,opacity=0,gapless_playback=True)
        self.outline=ft.Image(src=body_svg(),fit=ft.BoxFit.FILL)
        self.scan=ft.Image(src=scan_svg(0,state['nutrition_profile'].get('sex','Male')),fit=ft.BoxFit.FILL,gapless_playback=True)
        self.model=ft.Stack(controls=[self.outgoing_overlay,self.overlay,self.outline,self.scan],width=280,height=500)
        self.sleep_graph=ft.Image(src=sleep_chart(self.current['sleep_stages'],self.current['sleep'],self.current['sleep_quality']),
            height=190,width=320,fit=ft.BoxFit.CONTAIN,visible=False,gapless_playback=True)
        self.body_hint=txt("Tap a body area or choose a category",11,GRAY)
        self.gesture=ft.GestureDetector(content=self.model,on_tap_up=self.body_tap,on_hover=self.body_hover)
        self.model_host=ft.Container(expand=True,alignment=ft.Alignment.TOP_CENTER,
            content=ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER,spacing=5,
                controls=[self.gesture,self.sleep_graph,self.body_hint]))
        category_widgets=[]
        for name,item in CATEGORIES.items():
            icon=category_icon(name,26,GREEN)
            ring=ft.Container(width=48,height=48,border_radius=99,border=ft.Border.all(2,GREEN),
                 content=icon,alignment=ft.Alignment.CENTER,bgcolor=PANEL,animate_scale=180)
            label=txt(name,12,GRAY,True)
            self.category_controls[name]=(ring,icon,label)
            category_widgets.append(ft.Container(width=112,height=82,ink=True,border_radius=12,
                on_click=lambda e,n=name:self.on_select(n),
                content=ft.Column(spacing=5,alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,controls=[ring,label])))
        self.category_bar=ft.Row(spacing=2,alignment=ft.MainAxisAlignment.START,scroll=ft.ScrollMode.AUTO,controls=category_widgets)
        self.left_panel=ft.Container(width=286,content=ft.Column(expand=True,scroll=ft.ScrollMode.AUTO,spacing=9,controls=[
            box(ft.Column(spacing=5,controls=[
                ft.Row(controls=[custom_icon("heart_rate",24,CYAN),txt("Heart rate",14,WHITE,True)]),
                self.values["hr"],self.badges["hr"],self.ecg,txt("ECG",10,GRAY)]),12),
            self.card("Blood pressure","pressure",ft.Icons.MONITOR_HEART),
            ft.Row(spacing=8,controls=[self.card("Temperature","temp",ft.Icons.THERMOSTAT,True),
                                      self.card("SpO₂","spo2",ft.Icons.AIR,True)]),
            self.card("Radiation • absorbed dose","radiation",ft.Icons.WARNING_AMBER),
            txt("",11,GRAY),
        ]))
        filters=ft.Row(spacing=3,scroll=ft.ScrollMode.AUTO,controls=[
            ft.IconButton(icon=ft.Icons.SELECT_ALL,tooltip="All categories",on_click=lambda e:self.filter_alerts(None)),
            *[ft.IconButton(icon=category_icon(n,21),tooltip=n,on_click=lambda e,name=n:self.filter_alerts(name)) for n,d in CATEGORIES.items()]])
        self.filter_text=txt("All categories",11,CYAN)
        self.bell_count=txt("0",11,WHITE,True)
        self.bell_icon=ft.Icon(ft.Icons.NOTIFICATIONS_OUTLINED,color=CYAN)
        self.all_alerts_label=txt("All alerts",12,WHITE,True)
        self.critical_alerts_label=txt("Critical",12,RED,True)
        self.alert_tabs={key:ft.Container(expand=True,padding=10,border_radius=9,ink=True,
            on_click=lambda e,k=key:self.select_alert_tab(k),content=label)
            for key,label in (("all",self.all_alerts_label),("critical",self.critical_alerts_label))}
        tabs=ft.Row(spacing=8,controls=list(self.alert_tabs.values()))
        self.bell=ft.Container(tooltip="Alerts",ink=True,border_radius=12,padding=8,
            on_click=self.open_alerts,content=ft.Row(spacing=5,controls=[
                self.bell_icon,self.bell_count]))
        self.alert_content=ft.Container(width=500,height=480,content=ft.Column(expand=True,controls=[
            self.summary,tabs,filters,self.filter_text,self.alert_list]))
        self.alert_dialog=ft.AlertDialog(title=txt("Alerts by category",20,WHITE,True),
            content=self.alert_content,actions=[ft.TextButton(content="Close",on_click=self.close_alerts)],bgcolor=PANEL)
        self.right_panel=ft.Container(width=430,padding=ft.Padding.only(left=5),content=self.details)
        self.row=ft.Row(spacing=15,vertical_alignment=ft.CrossAxisAlignment.START,
                        controls=[self.left_panel,self.model_host,self.right_panel])
        self.team_events=[];self.emergency_member=None;self.emergency_values={}
        self.crew_label=txt("Crew",12,WHITE,True)
        self.crew_button=ft.Container(tooltip="Crew emergency alerts",ink=True,padding=9,border_radius=10,
            on_click=lambda e:self.open_crew_emergencies(),content=ft.Row(spacing=6,controls=[
                ft.Icon(ft.Icons.GROUP_OUTLINED,color=CYAN,size=21),self.crew_label]))
        self.crew_emergency_list=ft.Column(spacing=12,scroll=ft.ScrollMode.AUTO,expand=True)
        self.crew_emergency_content=ft.Container(width=520,height=460,content=self.crew_emergency_list)
        self.crew_emergency_dialog=ft.AlertDialog(title=txt("Crew emergencies",20,WHITE,True),
            content=self.crew_emergency_content,bgcolor=PANEL,
            actions=[ft.TextButton(content="Back to alerts",on_click=lambda e:self.show_crew_emergency(None)),
                     ft.TextButton(content="Close",on_click=lambda e:self.page.pop_dialog())])
        self.view=ft.Column(expand=True,spacing=6,controls=[
            ft.Row(wrap=True,alignment=ft.MainAxisAlignment.SPACE_BETWEEN,controls=[txt("My health overview",18,WHITE,True),self.live]),self.row])
        self.refresh_details();self.update()

    def open_crew_emergencies(self,member=None,from_alerts=False):
        if from_alerts:self.page.pop_dialog()
        self.emergency_member=member
        self.render_crew_emergencies()
        self.page.show_dialog(self.crew_emergency_dialog)

    def show_crew_emergency(self,member):
        self.emergency_member=member;self.render_crew_emergencies();self.page.update()

    def render_crew_emergencies(self):
        self.emergency_values={}
        selected=next((e for e in self.team_events if e['id']==self.emergency_member),None)
        if self.emergency_member and not selected:
            self.emergency_member=None
        if selected:
            rows=[txt(selected['name'],21,WHITE,True),txt("CRITICAL · assistance view",12,RED,True),
                txt("Only active critical alerts and the measurements related to them are shared.",12,GRAY)]
            for category in dict.fromkeys(a[0] for a in selected['alerts']):
                messages=[message for cat,_,message in selected['alerts'] if cat==category]
                keys={'Cardiology':(('hr','Heart rate','BPM'),('pressure','Blood pressure','mmHg')),
                    'Respiration':(('spo2','SpO2','%'),('breath','Respiratory rate','/min')),
                    'Temperature':(('temp','Body temperature','°C'),),
                    'Radiation':(('absorbed_dose','Absorbed dose','Gy'),('external_level','External detectors',''))}.get(category,())
                measures=[]
                for key,label,unit in keys:
                    value=txt(f"{selected['values'][key]} {unit}".strip(),20,WHITE,True)
                    self.emergency_values[key]=(value,unit)
                    measures.append(ft.Column(spacing=4,controls=[txt(label,11,GRAY),value]))
                rows.append(box(ft.Column(spacing=10,controls=[ft.Row(controls=[category_icon(category,23,RED),txt(category,16,RED,True)]),
                    *[txt(message,13,WHITE) for message in messages],*measures])))
            rows.append(txt("Follow the configured mission emergency procedures. Routine health history and food logs are not shared.",12,GRAY))
        else:
            rows=[txt("Crew critical alerts",18,WHITE,True),txt("Your monitoring stays on your own profile.",12,GRAY)]
            for event in self.team_events:
                rows.append(ft.Container(bgcolor="#301D2C",border=ft.Border.all(1,RED),border_radius=12,padding=14,ink=True,
                    on_click=lambda e,key=event['id']:self.show_crew_emergency(key),content=ft.Row(controls=[
                        ft.Icon(ft.Icons.WARNING_AMBER,color=RED),ft.Container(expand=True,content=ft.Column(spacing=5,controls=[
                            txt(event['name'],16,WHITE,True),txt(f"{len(event['alerts'])} critical alerts · open assistance view",12,RED)])),
                        ft.Icon(ft.Icons.CHEVRON_RIGHT,color=GRAY)])))
            if not self.team_events:
                rows.extend([ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE,color=GREEN,size=36),txt("No active crew emergencies",16,GREEN,True),
                    txt("Other crew members' routine measurements and profiles are private.",13,GRAY)])
        self.crew_emergency_list.controls=rows

    def live_metric(self,key,label,value,unit=""):
        from categories.common import metric
        card=metric(label,value,unit)
        self.detail_values[key]=(card.content.controls[1],unit)
        return card

    def card(self,label,key,icon,expand=False):
        return ft.Container(expand=True if expand else None,bgcolor=PANEL,gradient=panel_gradient(),padding=11,border_radius=12,
            border=ft.Border.all(1,BORDER),content=ft.Column(spacing=4,controls=[
                ft.Row(spacing=5,controls=[custom_icon({"temp":"temperature","radiation":"radiation"}.get(key,""),19,CYAN,icon),txt(label,11,GRAY)]),
                self.values[key],self.badges[key]]))

    def body_category(self,e):
        position=e.local_position
        x,y,w,h=self.camera
        return category_at(x+position.x*w/self.model.width,y+position.y*h/self.model.height,self.state["nutrition_profile"].get("sex","Male"))

    def body_tap(self,e):
        name=self.body_category(e)
        if name:self.on_select(name)

    def body_hover(self,e):
        name=self.body_category(e)
        value=(name+" — tap to explore") if name else "Tap a body area or choose a category"
        if value!=self.body_hint.value:self.body_hint.value=value;self.page.update()

    def fit(self,width,height):
        # A real viewport resize settles the current transition before relayout.
        self.transition=None
        self.overlay.opacity=1;self.outgoing_overlay.opacity=0;self.right_panel.opacity=1
        self.camera=frame_for(self.state.get("category"))
        self.viewport=(width,height)
        mobile=width<850
        available=max(220,height-285)
        self.crew_emergency_content.width=max(240,min(540,width-72))
        self.crew_emergency_content.height=max(220,min(560,height-220))
        self.alert_content.width=max(240,min(520,width-72))
        self.alert_content.height=max(220,min(560,height-220))
        for control in self.category_bar.controls:control.width=88 if mobile else 106
        self.view.scroll=ft.ScrollMode.AUTO if mobile else None
        self.row.height=None if mobile else available
        self.row.wrap=mobile
        self.row.controls=([self.model_host,self.right_panel,self.left_panel] if mobile and self.state.get('category') else [self.model_host,self.left_panel,self.right_panel] if mobile else
                           [self.left_panel,self.model_host,self.right_panel])
        self.left_panel.width=width-45 if mobile else (250 if width<1250 else 270)
        self.right_panel.width=width-45 if mobile else max(340,min(540,width*.36))
        if not mobile and self.state.get('category')=='Nutrition':
            self.right_panel.width=max(350,min(560,width*.38))
        self.left_panel.height=self.right_panel.height=None if mobile else available
        self.left_panel.content.expand=not mobile
        self.left_panel.content.scroll=None if mobile else ft.ScrollMode.AUTO
        self.details.expand=not mobile
        self.details.scroll=None if mobile else ft.ScrollMode.AUTO
        self.model_host.expand=None if mobile else True
        self.model_host.width=width-45 if mobile else None
        center=(width-50) if mobile else max(130,width-self.left_panel.width-self.right_panel.width-65)
        h=min((340 if self.state.get('category')=='Nutrition' else 370) if mobile else available-30,center*self.camera[3]/self.camera[2])
        self.sleep_graph.width=min(360,center)
        self.sleep_graph.height=min(200,center*220/360)
        if self.state.get('category')=='Sleep':h=min(h,max(95,available-self.sleep_graph.height-40))
        h*={'Stress':.94,'Sleep':.88,'Temperature':.98}.get(self.state.get('category'),1.)
        w=h*self.camera[2]/self.camera[3]
        self.model.width,self.model.height=w,h
        self.gesture.width,self.gesture.height=w,h
        for image in (self.outline,self.overlay,self.outgoing_overlay,self.scan):image.width,image.height=w,h
        self.ecg.width=self.left_panel.width-30
        self.refresh_camera()

    def open_alerts(self,e=None):
        self.alert_tab="critical" if self.critical_count else "all"
        self.alert_filter=None
        self.render_alerts();self.page.show_dialog(self.alert_dialog)

    def close_alerts(self,e=None):
        self.page.pop_dialog()

    def alert_select(self,name):
        self.close_alerts();self.on_select(name)

    def geometry(self):
        return (self.right_panel.width,self.model.width,self.model.height)

    def apply_geometry(self,values):
        panel,w,h=values
        w=min(w,h*self.camera[2]/self.camera[3]);h=w*self.camera[3]/self.camera[2]
        self.right_panel.width=panel
        self.model.width,self.model.height=w,h
        self.gesture.width,self.gesture.height=w,h
        for image in (self.outline,self.overlay,self.outgoing_overlay,self.scan):image.width,image.height=w,h

    def select(self,name):
        if not is_own_profile(self.state) and name not in critical_categories(self.state,self.current):name=None
        if name==self.state.get('category'):return
        start=self.geometry()
        start_camera=self.camera
        previous=category_overlay(self.state.get('category'),self.current,self.state)
        self.state["category"]=name
        self.body_hint.value="Tap a body area or choose a category"
        self.refresh_details();self.refresh_overlay();self.update()
        if hasattr(self,"viewport"):self.fit(*self.viewport)
        target=self.geometry()
        target_camera=self.camera
        self.camera=start_camera
        self.apply_geometry(start)
        self.outgoing_source=previous
        self.refresh_camera()
        self.outgoing_overlay.opacity=1;self.overlay.opacity=0
        self.right_panel.opacity=.12
        self.transition=dict(elapsed=0.,duration=.85 if name in ('Sleep','Cardiology') else .75,start=start,target=target,
            start_camera=start_camera,target_camera=target_camera)

    def advance_transition(self,dt):
        """One cancellable transition, independent of simulated sensor pause."""
        motion=self.transition
        if not motion:return False
        motion['elapsed']+=max(0,dt)
        t=min(1.,motion['elapsed']/motion['duration'])
        eased=t*t*(3.-2.*t)
        self.camera=interpolate_frame(motion['start_camera'],motion['target_camera'],eased)
        self.apply_geometry(tuple(a+(b-a)*eased for a,b in zip(motion['start'],motion['target'])))
        self.overlay.opacity=eased;self.outgoing_overlay.opacity=1.-eased
        self.right_panel.opacity=.12+.88*eased
        self.refresh_camera()
        if t>=1:
            self.transition=None
            self.outgoing_source=None
            self.outgoing_overlay.src=category_overlay(None,self.current,self.state)
        return True

    def refresh_details(self):
        self.detail_values={}
        name=self.state.get("category")
        self.sleep_graph.visible=name=="Sleep"
        if not is_own_profile(self.state):
            self.details.controls=self.shared_profile()
            return
        if not name:
            self.details.controls=[ft.Icon(ft.Icons.TOUCH_APP,color=CYAN,size=30),txt("Choose a category",19,WHITE,True),
                txt("Select a ring above or an area on the body to explore its readings.",13,GRAY)]
            return
        self.details.controls=[ft.Row(controls=[category_icon(name,26,CYAN),
            ft.Container(expand=True,content=txt(name,20,WHITE,True)),
            ft.IconButton(icon=ft.Icons.CLOSE,tooltip="Clear category",on_click=lambda e:self.on_select(None))]),
            txt(CATEGORIES[name]["description"],12,GRAY),
            BUILDERS[name](self)]
        if name=="Radiation":self.details.controls=[self.details.controls[0],self.details.controls[-1]]

    def shared_profile(self):
        critical=[a for a in self.alerts if a[1]=='danger']
        cards=[box(ft.Column(spacing=9,controls=[
            ft.Icon(ft.Icons.PERSON_OUTLINE,size=38,color=CYAN),
            txt(CREW.get(self.state.get('crew_id'),'Crew member'),21,WHITE,True),
            txt('Critical support view' if critical else 'No shared critical alerts',15,RED if critical else GREEN,True),
            txt('Routine measurements, nutrition logs and personal settings are private. Only information related to active critical alerts is shared here.',12,GRAY)]))]
        for category,_,message in critical:
            metrics=[]
            keys={'Cardiology':(('hr','Heart rate','BPM'),('pressure','Blood pressure','mmHg')),
                'Respiration':(('spo2','SpO2','%'),('breath','Respiratory rate','/min')),
                'Temperature':(('temp','Body temperature','°C'),),
                'Radiation':(('absorbed_dose','Absorbed dose','Gy'),('external_level','External detectors',''))}.get(category,())
            for key,label,unit in keys:metrics.append(self.live_metric(key,label,self.current[key],unit))
            cards.append(box(ft.Column(spacing=9,controls=[ft.Row(controls=[category_icon(category,24,RED),txt(category+' · Critical',16,RED,True)]),txt(message,13,WHITE),*metrics])))
        if critical:cards.append(txt('Use Guidebook → ICE to review the configured emergency procedures.',13,CYAN,True))
        return cards

    def refresh_category(self):
        self.refresh_details();self.page.update()

    def refresh_camera(self):
        self.scan.visible=self.state.get('category') is None
        self.scan.src=frame_svg(scan_svg(self.state.get('scan_seconds',0.),self.state['nutrition_profile'].get('sex','Male')),self.camera)
        self.outline.opacity=1
        if self.state.get('category')=='Radiation':self.body_hint.value='Radiation exposure'
        self.outline.src=frame_svg(body_svg(self.state["nutrition_profile"].get("sex","Male")),self.camera)
        self.refresh_overlay()
        if self.outgoing_source:
            self.outgoing_overlay.src=frame_svg(self.outgoing_source,self.camera)

    def refresh_overlay(self):
        self.overlay.src=frame_svg(category_overlay(self.state.get("category"),self.current,self.state),self.camera)

    def advance_scan(self,dt):
        if self.state.get('tab',0)!=0 or self.state.get('category') is not None:return False
        self.state['scan_seconds']=self.state.get('scan_seconds',0.)+dt
        self.scan.src=frame_svg(scan_svg(self.state['scan_seconds'],self.state['nutrition_profile'].get('sex','Male')),self.camera)
        return True

    def animate(self,dt):
        """Integrate phases from elapsed time, so rate changes never jump the phase."""
        self.state['breath_phase']=(self.state.get('breath_phase',0.)+dt*self.current['breath']/60.)%1.
        self.state['heart_phase']=(self.state.get('heart_phase',0.)+dt*self.current['hr']/60.)%1.
        self.state['swallow_phase']=(self.state.get('swallow_phase',0.)+dt/3.8)%1.
        self.state['radiation_seconds']=self.state.get('radiation_seconds',0.)+dt
        self.state['sleep_seconds']=self.state.get('sleep_seconds',0.)+dt
        self.state['radiation_phase']=(self.state.get('radiation_phase',0.)+dt/1.6)%1.
        self.state['static_frame']=self.state.get('static_frame',0)+dt*12
        if self.state.get('category') in ('Respiration','Cardiology','Stress','Radiation','Nutrition','Sleep'):
            self.refresh_overlay()
    def persist_nutrition(self):
        persist_crew(self.state)
        if self.state.get('crew_id','crew_01')=='crew_01':
            write_json(DATA_DIR/"nutrition.json",{"profile":self.state["nutrition_profile"],
                "entries":self.state["nutrition_entries"],"targets":self.state.get("nutrition_targets",{})})
        self.update()

    def filter_alerts(self,name):
        self.alert_filter=name;self.render_alerts();self.page.update()

    def select_alert_tab(self,key):
        self.alert_tab=key;self.render_alerts();self.page.update()

    def animate_bell(self,dt):
        # Slow, continuous pulse; continues on all screens and during sensor pause.
        if not self.critical_count:
            self.bell.scale=1.;self.bell.opacity=1.;self.bell.bgcolor=None
            self.bell.border=None;self.bell_icon.color=CYAN
            return False
        import math
        self.bell_phase=(self.bell_phase+dt/1.4)%1.
        pulse=.5-.5*math.cos(self.bell_phase*math.tau)
        self.bell.scale=1.+.14*pulse
        self.bell.opacity=.76+.24*pulse
        self.bell.bgcolor="#481C2B";self.bell.border=ft.Border.all(1,RED)
        self.bell_icon.color=RED
        return True

    def render_alerts(self):
        self.filter_text.value=self.alert_filter or "All categories"
        self.all_alerts_label.value=f"All alerts ({len(self.alerts)+sum(len(e['alerts']) for e in self.team_events)})"
        self.critical_alerts_label.value=f"Critical ({self.critical_count})"
        for key,tab in self.alert_tabs.items():
            tab.bgcolor=CARD if key==self.alert_tab else PANEL
            tab.border=ft.Border.all(1,RED if key=="critical" and key==self.alert_tab else BORDER)
        self.alert_list.controls=[]
        if self.team_events and not self.alert_filter:
            self.alert_list.controls.append(txt("CREW · CRITICAL",12,RED,True))
            for event in self.team_events:
                self.alert_list.controls.append(ft.Container(padding=12,border_radius=10,bgcolor="#301D2C",border=ft.Border.all(1,RED),ink=True,
                    on_click=lambda e,key=event['id']:self.open_crew_emergencies(key,True),content=ft.Row(controls=[
                        ft.Icon(ft.Icons.WARNING_AMBER,color=RED),ft.Container(expand=True,content=txt(event['name']+f" · {len(event['alerts'])} critical",13,WHITE,True)),
                        ft.Icon(ft.Icons.CHEVRON_RIGHT,color=RED)])))
        levels=("danger",) if self.alert_tab=="critical" else ("danger","warning")
        for level in levels:
            visible=[a for a in self.alerts if a[1]==level and (not self.alert_filter or a[0]==self.alert_filter)]
            if not visible:continue
            color=STATUS_COLOR[level]
            self.alert_list.controls.append(txt("CRITICAL — review immediately" if level=="danger" else "REQUIRES ATTENTION",12,color,True))
            # Severity is the outer group: no warning can precede a critical alert.
            for name in CATEGORIES:
                items=[message for cat,_,message in visible if cat==name]
                if not items:continue
                self.alert_list.controls.append(ft.Container(bgcolor="#301D2C" if level=="danger" else CARD,
                    border=ft.Border.all(1,color),border_radius=9,padding=11,ink=True,
                    on_click=lambda e,n=name:self.alert_select(n),content=ft.Column(spacing=6,controls=[
                        ft.Row(spacing=6,controls=[category_icon(name,20,color),
                            ft.Container(expand=True,content=txt(name,13,WHITE,True)),
                            txt(str(len(items)),12,color,True)]),
                        *[txt(message,12,WHITE) for message in items],
                    ])))
        if not self.alert_list.controls:
            self.alert_list.controls=[txt("No active critical alerts" if self.alert_tab=="critical" else "No active alerts",15,GREEN,True),
                txt("In the selected category." if self.alert_filter else "All monitored categories checked. Unassessed data may still be present.",12,GRAY)]

    def update(self):
        self.current=current_readings(self.state)
        self.statuses,self.alerts=evaluate_alerts(self.current);r=self.current
        extra=mineral_alerts(self.state['nutrition_profile'],self.state['nutrition_entries'],__import__("datetime").date.today().isoformat() in self.state.get("nutrition_closed_days",[]))
        self.alerts.extend(extra)
        self.alerts.sort(key=lambda a:0 if a[1]=="danger" else 1)
        if extra:self.statuses['Nutrition']='danger' if any(a[1]=='danger' for a in extra) else 'warning'
        own=is_own_profile(self.state)
        shared=critical_categories(self.state,r) if not own else set()
        if not own:
            self.alerts=[a for a in self.alerts if a[1]=='danger']
            self.statuses={name:('danger' if name in shared else 'neutral') for name in CATEGORIES}
        panels=self.left_panel.content.controls
        self.left_panel.visible=own or bool(shared)
        panels[0].visible=panels[1].visible=own or 'Cardiology' in shared
        panels[2].visible=own or bool({'Temperature','Respiration'} & shared)
        panels[2].controls[0].visible=own or 'Temperature' in shared
        panels[2].controls[1].visible=own or 'Respiration' in shared
        panels[3].visible=own or 'Radiation' in shared
        self.team_events=crew_emergencies(self.state)
        team_count=sum(len(event['alerts']) for event in self.team_events)
        self.crew_label.value=f"Crew · {team_count}" if team_count else "Crew"
        self.crew_label.color=RED if team_count else WHITE
        self.crew_button.bgcolor="#301D2C" if team_count else None
        self.crew_button.border=ft.Border.all(1,RED) if team_count else None
        selected=next((e for e in self.team_events if e['id']==self.emergency_member),None)
        if selected:
            for key,(control,unit) in self.emergency_values.items():control.value=f"{selected['values'][key]} {unit}".strip()
        for key,value in {"hr":f'{r["hr"]} BPM',"pressure":f'{r["pressure"]} mmHg',
                          "temp":f'{r["temp"]:.1f} °C',"spo2":f'{r["spo2"]}%',
                          "radiation":f'{r["absorbed_dose"]:.6f} Gy'}.items():self.values[key].value=value
        keys={"hr":"Cardiology","pressure":None,"temp":"Temperature","spo2":"Respiration","radiation":"Radiation"}
        for key,category in keys.items():
            status=self.statuses[category] if category else "neutral"
            self.badges[key].value=STATUS_TEXT[status];self.badges[key].color=STATUS_COLOR[status]
        for key,(control,unit) in self.detail_values.items():
            control.value=f"{r[key]} {unit}".strip()
        self.ecg.src=ecg_svg(self.state["tick"],r["hr"])
        if self.state.get('category')=='Cardiology' and getattr(self,'detail_ecg',None):
            self.detail_ecg.src=ecg_svg(self.state['tick'],r['hr'],width=600,height=150)
        if self.state.get('category')=='Radiation' and getattr(self,'daily_dose_control',None):
            self.daily_dose_control.value=f"{r['absorbed_dose']*1e6:g} µGy"
        if self.state.get('category')=='Sleep':
            self.sleep_graph.src=sleep_chart(r['sleep_stages'],r['sleep'],r['sleep_quality'])
        self.live.value=("MANUAL INPUT" if self.state.get("manual_enabled") else "MONITORING" if self.state["running"] else "PAUSED") if own else "PRIVACY VIEW"
        for name,(ring,icon,label) in self.category_controls.items():
            active=self.state.get("category")==name;color=GREEN if name=="Nutrition" and self.statuses[name] in ("neutral","ok") else STATUS_COLOR[self.statuses[name]]
            ring.border=ft.Border.all(3 if active else 2,color)
            icon.color=color
            ring.scale=1.08 if active else 1.;label.color=WHITE if active else GRAY
        danger=sum(level=="danger" for _,level,_ in self.alerts);warning=sum(level=="warning" for _,level,_ in self.alerts)
        self.summary.value=f"{danger+team_count} critical · {warning} requiring attention"
        self.critical_count=danger+team_count
        self.summary.color=RED if danger+team_count else YELLOW if warning else GREEN
        self.bell.tooltip=f"{danger} critical alerts — click to review" if danger else "Alerts"
        if not self.critical_count:self.animate_bell(0)
        self.bell_count.value=str(len(self.alerts)+team_count);self.bell_count.color=self.summary.color
        signature=(tuple(self.alerts),tuple(self.statuses.items()),tuple((e["id"],tuple(e["alerts"])) for e in self.team_events))
        if signature!=self.alert_signature:
            self.alert_signature=signature;self.render_alerts();self.render_crew_emergencies()
            if not own:self.refresh_details()
        if self.state.get("category") in ("Stress","Sleep","Temperature","Respiration","Cardiology","Radiation"):
            self.refresh_overlay()

def build_monitoring_dashboard(state,page,on_select):
    return MonitoringController(state,page,on_select)

def update_monitoring_data(controller):
    controller.update()


"""Viewport-sized month and agenda; event types choose colors automatically."""
import calendar,re
from datetime import date
import flet as ft
from config import box,txt,WHITE,GRAY,CYAN,CARD,BORDER,RED,GREEN,YELLOW,VIOLET
from logic import save_events

COLORS={'Medical':CYAN,'Sleep':VIOLET,'Exercise':GREEN,'Nutrition':YELLOW,'Safety':RED,'Other':GRAY}
def event_type(event):
    chosen=event.get('type')
    if chosen in COLORS:return chosen
    title=event.get('title','').lower()
    for name,words in [('Safety',('emergency','radiation','alarm','safety')),('Sleep',('sleep','recovery','rest')),
        ('Exercise',('exercise','workout','training')),('Nutrition',('food','meal','nutrition')),('Medical',('check','blood','health','medical','pressure'))]:
        if any(word in title for word in words):return name
    return 'Other'

def build_calendar_screen(state,page):
    host=ft.Container(expand=True)
    def refresh():host.content=render();page.update()
    def render():
        month,selected=state['month'],state['date'];mobile=float(page.width or 1380)<850
        available=max(320,float(page.height or 860)-310)
        month_height=(available-46)*(.67 if mobile else 1)
        weeks=calendar.Calendar(firstweekday=0).monthdayscalendar(month.year,month.month)
        cell=max(23,(month_height-120)/len(weeks)-4)
        def shift(amount):
            index=month.year*12+month.month-1+amount
            state['month']=date(index//12,index%12+1,1);state['date']=state['month'];refresh()
        def pick(day):state['date']=date(month.year,month.month,day);refresh()
        def today(e):state['date']=date.today();state['month']=date.today().replace(day=1);refresh()
        def new_event(e):
            title=ft.TextField(label='Event title',autofocus=True)
            time=ft.TextField(label='Time',value='09:00')
            kind=ft.Dropdown(label='Event color / category',value='Auto',options=[ft.DropdownOption(key=n) for n in ('Auto',*COLORS)])
            error=txt('',12,RED)
            def add(e):
                entry=dict(date=selected.isoformat(),time=(time.value or '').strip(),title=(title.value or '').strip())
                if not entry['title']:error.value='Enter an event title.';page.update();return
                if not re.fullmatch(r'(?:[01]\d|2[0-3]):[0-5]\d',entry['time']):error.value='Use HH:MM format.';page.update();return
                if kind.value!='Auto':entry['type']=kind.value
                state['events'].append(entry)
                try:save_events(state['events'])
                except OSError:state['events'].pop();error.value='Could not save event.';page.update();return
                page.pop_dialog();refresh()
            page.show_dialog(ft.AlertDialog(title=txt('New event · '+selected.isoformat(),18,WHITE,True),
                content=ft.Container(width=340,content=ft.Column(tight=True,spacing=12,controls=[title,time,kind,error])),
                actions=[ft.TextButton(content='Cancel',on_click=lambda e:page.pop_dialog()),ft.Button(content='Save event',on_click=add)]))
        grid=[ft.Row(spacing=4,controls=[ft.Container(expand=True,alignment=ft.Alignment.CENTER,content=txt(day,10,GRAY,True)) for day in ('Mon','Tue','Wed','Thu','Fri','Sat','Sun')])]
        for week in weeks:
            cells=[]
            for day in week:
                if not day:cells.append(ft.Container(expand=True,height=cell));continue
                dt=date(month.year,month.month,day);chosen=dt==selected
                events=[e for e in state['events'] if e['date']==dt.isoformat()]
                bars=[ft.Container(width=9,height=3,bgcolor=COLORS[k],border_radius=2) for k in dict.fromkeys(event_type(e) for e in events)]
                cells.append(ft.Container(expand=True,height=cell,padding=3,border_radius=8,ink=True,
                    bgcolor='#265166' if chosen else CARD,border=ft.Border.all(2 if chosen else 1,CYAN if chosen else BORDER),
                    on_click=lambda e,d=day:pick(d),content=ft.Column(spacing=2,alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[txt(str(day),12,WHITE,chosen),ft.Row(spacing=2,alignment=ft.MainAxisAlignment.CENTER,controls=bars)])))
            grid.append(ft.Row(spacing=4,controls=cells))
        agenda=[]
        for event in sorted((e for e in state['events'] if e['date']==selected.isoformat()),key=lambda e:e['time']):
            color=COLORS[event_type(event)]
            def remove(e,item=event):
                old=list(state['events']);state['events'].remove(item)
                try:save_events(state['events'])
                except OSError:state['events']=old;return
                refresh()
            agenda.append(ft.Container(bgcolor=CARD,padding=8,border_radius=9,content=ft.Row(spacing=9,controls=[
                ft.Container(width=4,height=34,bgcolor=color,border_radius=2),txt(event['time'],12,color,True),
                ft.Container(expand=True,content=ft.Column(spacing=3,controls=[txt(event['title'],12,WHITE,True),txt(event_type(event),10,color)])),
                ft.IconButton(icon=ft.Icons.DELETE_OUTLINE,icon_size=17,tooltip='Delete event',on_click=remove)])))
        month_panel=box(ft.Column(spacing=6,controls=[ft.Row(controls=[
            ft.IconButton(icon=ft.Icons.CHEVRON_LEFT,on_click=lambda e:shift(-1)),
            ft.Container(expand=True,content=txt(f'{calendar.month_name[month.month]} {month.year}',16,WHITE,True)),
            ft.TextButton(content='Today',on_click=today),ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT,on_click=lambda e:shift(1))]),*grid]),10)
        agenda_panel=box(ft.Column(expand=True,spacing=8,controls=[
            ft.Row(controls=[ft.Container(expand=True,content=txt(selected.strftime('%d %b · Agenda'),15,WHITE,True)),ft.IconButton(icon=ft.Icons.ADD,tooltip='Add event',on_click=new_event)]),
            ft.Column(expand=True,scroll=ft.ScrollMode.AUTO,spacing=7,controls=agenda or [txt('No events scheduled.',12,GRAY)])]),10)
        layout=ft.Column(expand=True,spacing=8,controls=[ft.Container(height=month_height,content=month_panel),ft.Container(expand=True,content=agenda_panel)]) if mobile else ft.Row(expand=True,spacing=12,vertical_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[ft.Container(expand=7,content=month_panel),ft.Container(expand=4,content=agenda_panel)])
        return ft.Column(height=available,spacing=7,controls=[ft.Row(wrap=True,spacing=14,controls=[txt('Mission calendar',20,WHITE,True),
            *[txt('━ '+name,10,color) for name,color in COLORS.items() if name!='Other']]),layout])
    host.content=render();return host

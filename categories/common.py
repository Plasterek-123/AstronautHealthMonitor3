import math
import flet as ft
from config import txt, CARD, WHITE, GRAY, CYAN, GREEN, YELLOW, RED

def metric(label,value,unit=""):
    return ft.Container(bgcolor=CARD,padding=11,border_radius=10,content=ft.Column(spacing=3,controls=[
        txt(label,12,GRAY),txt(f"{value} {unit}".strip(),20,WHITE,True)]))

def note(text): return txt(text,11,GRAY)

def trend_svg(values,color=CYAN):
    points=' '.join(f'{10+i*280/max(1,len(values)-1):.1f},{105-v*.9:.1f}' for i,v in enumerate(values))
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 125"><path d="M10 15V105H290" stroke="#516C7C" fill="none"/><text x="12" y="12" font-size="10" fill="#A3B8C8">100</text><text x="12" y="120" font-size="10" fill="#A3B8C8">0</text><polyline points="{points}" stroke="{color}" fill="none" stroke-width="2"/></svg>'

def pie_svg(values):
    colors=[CYAN,"#C1B1FF",GREEN]; start=-math.pi/2; paths=[]
    for value,color in zip(values,colors):
        end=start+value/100*2*math.pi
        x1,y1=80+65*math.cos(start),80+65*math.sin(start)
        x2,y2=80+65*math.cos(end),80+65*math.sin(end)
        paths.append(f'<path d="M80 80L{x1} {y1}A65 65 0 {int(value>50)} 1 {x2} {y2}Z" fill="{color}"/>')
        start=end
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 160">'+''.join(paths)+'</svg>'

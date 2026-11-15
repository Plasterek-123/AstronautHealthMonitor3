"""Incoming illustrative photons around the original category warning icon."""
import math
import re
from functools import lru_cache
from config import ASSET_DIR,STATUS_COLOR
from logic import radiation_status

@lru_cache(maxsize=1)
def warning_icon():
    source=(ASSET_DIR/'icons/radiation.svg').read_text(encoding='utf-8')
    # Strip document declarations; preserve all original artwork and its viewBox.
    source=source[source.index('<svg'):]
    source=re.sub(r'\b(?:width|height)="[^"]*"','',source,count=2)
    return source.replace('<svg','<svg x="385" y="455" width="170" height="170"',1)

def photon_count(reading):
    ratio=max(0,reading['absorbed_dose']/max(1e-12,reading.get('dose_limit_gy',.0005)))
    external=reading.get('external_level','Nominal (demo)')
    intensity=max(min(1,ratio/2),1 if external=='External alert (demo)' else .5 if external=='Elevated (demo)' else 0)
    return round(10+64*intensity),intensity

def radiation_overlay(reading,seconds):
    count,intensity=photon_count(reading)
    color=STATUS_COLOR[radiation_status(reading)]
    pieces=[]
    for i in range(count):
        phase=(seconds*(.13+(i%7)*.012)+i*.61803398875)%1
        x=-300+phase*1550
        y=-180+(i*137%1370)+phase*470
        length=22+85*intensity+45*(.5+.5*math.sin(seconds*1.7+i))
        pieces.append(f'<path d="M{x-length:.2f} {y-length*.38:.2f}L{x:.2f} {y:.2f}" stroke="{color}" stroke-width="{1.5+intensity:.2f}" stroke-linecap="round" opacity="{.22+.42*math.sin(math.pi*phase):.3f}"/>')
    # Incoming streaks cross the full body canvas; the supplied icon sits on the chest.
    icon=warning_icon()
    icon_color=color
    icon=re.sub(r'fill:#[0-9a-fA-F]{3,8}', 'fill:'+icon_color,icon)
    icon=re.sub(r'fill="#[0-9a-fA-F]{3,8}"', 'fill="'+icon_color+'"',icon)
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 941 1672">'+''.join(pieces)+f'<g color="{color}">'+icon+'</g></svg>'

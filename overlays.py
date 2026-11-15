"""Load aligned SVG artwork; dynamic head and heat-map overlays stay in body space."""
import math
import re
from sleep_art import sleep_overlay
from radiation_art import radiation_overlay
from functools import lru_cache
from original_art import original_organs,beating_original_heart
from config import BODY_FILE,OVERLAYS,CYAN,GREEN,YELLOW,RED

def svg(content):
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 941 1672">'+content+'</svg>'

@lru_cache(maxsize=2)
def body_svg(sex="Male"):
    try:return (BODY_FILE.parent/"assets/body_female.svg" if sex=="Female" else BODY_FILE.parent/"assets/body_original_male.svg").read_text(encoding="utf-8").replace('fill="#000000"','fill="#66C5D7"')
    except OSError:return svg('<text x="100" y="500" fill="white" font-size="30">Body SVG is missing</text>')

@lru_cache(maxsize=8)
def artwork(category):
    try:return OVERLAYS[category].read_text(encoding="utf-8")
    except OSError:return svg('')

def inner_svg(source):
    return re.sub(r'</svg>\s*$','',re.sub(r'^\s*<svg\b[^>]*>','',source))

@lru_cache(maxsize=2)
def outer_body_path(sex="Male"):
    """Use the original body's external contour to clip the thermal illustration."""
    source=(BODY_FILE.parent/"assets/body_female.svg" if sex=="Female" else BODY_FILE.parent/"assets/body_original_male.svg").read_text(encoding="utf-8")
    path=re.search(r'<path\b[^>]*\bd="([^"]+)"',source).group(1)
    return re.split('[Zz]',path,maxsplit=1)[0]+' Z'

def temperature_color(value,low=30.,high=40.):
    """Continuous fixed-scale palette. Colors encode temperature, not clinical risk."""
    stops=[(0.,(33,57,185)),(.25,(0,190,241)),(.5,(59,220,155)),
           (.7,(251,216,63)),(.85,(255,122,44)),(1.,(227,52,74))]
    fraction=max(0.,min(1.,(value-low)/(high-low)))
    for (left,a),(right,b) in zip(stops,stops[1:]):
        if fraction<=right:
            t=(fraction-left)/(right-left)
            rgb=[round(x+(y-x)*t) for x,y in zip(a,b)]
            return '#'+''.join(f'{x:02X}' for x in rgb)
    return '#E3344A'

def heatmap_overlay(r,state):
    body=r['temp'];limb=r['limb_temp'];selected=state.get('limb','Left arm')
    regions={
        'Left arm':('M606 327Q667 322 694 430L735 588L830 799L787 840L688 626L642 500Z',710,620),
        'Right arm':('M335 327Q274 322 247 430L206 588L111 799L154 840L253 626L299 500Z',232,620),
        'Left leg':('M475 858L602 858L598 1090L580 1320L590 1580L515 1585L504 1330L485 1110Z',550,1250),
        'Right leg':('M466 858L339 858L343 1090L361 1320L351 1580L426 1585L437 1330L456 1110Z',390,1250),
    }
    path,x,y=regions[selected]
    core=temperature_color(body);peripheral=temperature_color(max(30,body-2.5));tip=temperature_color(max(30,body-4.5))
    limb_color=temperature_color(limb)
    defs=f'''<defs>
      <clipPath id="thermalBody"><path d="{outer_body_path(state.get("nutrition_profile",{}).get("sex","Male"))}"/></clipPath>
      <radialGradient id="thermalCore" cx="50%" cy="31%" r="75%">
        <stop offset="0" stop-color="{core}"/><stop offset=".3" stop-color="{core}"/>
        <stop offset=".6" stop-color="{peripheral}"/><stop offset="1" stop-color="{tip}"/>
      </radialGradient>
      <linearGradient id="limbField" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop stop-color="{temperature_color(limb+1)}"/><stop offset=".5" stop-color="{limb_color}"/>
        <stop offset="1" stop-color="{temperature_color(limb-1)}"/>
      </linearGradient>
    </defs>'''
    return svg(defs+f'''<g clip-path="url(#thermalBody)">
      <rect width="941" height="1672" fill="url(#thermalCore)" opacity=".88"/>
      <path d="{path}" fill="url(#limbField)"/>
    </g>
    <circle cx="{x}" cy="{y}" r="33" fill="none" stroke="white" stroke-width="3"/>
    <path d="M{x-44} {y}H{x+44}M{x} {y-44}V{y+44}" stroke="white" stroke-width="2" opacity=".75"/>
    <rect x="373" y="475" width="194" height="58" rx="13" fill="#0A1421" opacity=".82"/>
    <text x="470" y="515" text-anchor="middle" font-size="36" font-family="sans-serif" fill="white">{body:.1f} °C</text>
    <rect x="{x-90}" y="{y+52}" width="180" height="55" rx="12" fill="#0A1421" opacity=".85"/>
    <text x="{x}" y="{y+90}" text-anchor="middle" font-size="32" font-family="sans-serif" fill="white">{limb:.1f} °C</text>''')

def thermal_legend_svg():
    stops=''.join(f'<stop offset="{i}%" stop-color="{temperature_color(30+i*.1)}"/>' for i in range(0,101,10))
    labels=''.join(f'<text x="{15+(value-30)*27}" y="55" text-anchor="middle" font-size="11" fill="#EDF8FF">{value}°</text>' for value in (30,32,34,36,38,40))
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 65"><defs><linearGradient id="legend">'+stops+'</linearGradient></defs><rect x="15" y="12" width="270" height="22" rx="7" fill="url(#legend)"/>'+labels+'</svg>'

def category_overlay(category,r,state):
    if not category:return svg('')
    if category=="Respiration":
        phase=state.get('breath_phase',0.)
        inflation=.5-.5*math.cos(phase*math.tau)
        sx,sy=1.+.055*inflation,1.+.035*inflation
        drawing=inner_svg(original_organs(category,state.get("nutrition_profile",{}).get("sex","Male")) or artwork(category))
        # Only the chest artwork expands. The head and outline remain stationary.
        return svg(f'''<defs>
          <clipPath id="lungChest"><rect x="325" y="280" width="300" height="405"/></clipPath>
          <clipPath id="airwayHead"><rect x="0" y="0" width="941" height="280"/></clipPath>
        </defs><g clip-path="url(#airwayHead)">{drawing}</g>
        <g clip-path="url(#lungChest)"><g transform="translate(470 370) scale({sx:.4f} {sy:.4f}) translate(-470 -370)">{drawing}</g></g>''')
    if category=="Cardiology":
        return beating_original_heart(state.get('nutrition_profile',{}).get('sex','Male'),state.get('heart_phase',0.))
    if category=="Nutrition":
        drawing=inner_svg(original_organs(category,state.get('nutrition_profile',{}).get('sex','Male')) or artwork(category))
        phase=state.get('swallow_phase',0.)
        # A schematic bolus travels inside the original esophagus, then into the stomach.
        progress=min(1,phase/.82)
        x=470+4*math.sin(progress*math.tau);y=197+287*progress
        if phase>.82:
            turn=(phase-.82)/.18;x=470+35*turn;y=484+28*math.sin(turn*math.pi/2)
        opacity=min(1,phase*15,(1-phase)*15)
        bolus=f'<ellipse cx="{x:.2f}" cy="{y:.2f}" rx="5" ry="10" fill="#FFD06B" stroke="#FFD06B" stroke-width="2" opacity="{max(0,opacity):.3f}"/>'
        return svg(drawing+bolus)
    if category=="Temperature":
        return heatmap_overlay(r,state)
    if category=="Stress":
        # Higher stress means greater visual disorder.
        strength=(max(0,min(100,r['stress']))/100)**1.5
        frame=int(state.get('static_frame',0))
        import random
        rng=random.Random(frame)
        count=round(80+1700*strength)
        grains=''.join(f'<rect x="{rng.randrange(50,890)}" y="{rng.randrange(20,1650)}" width="{rng.randrange(3,max(5,round(8+22*strength)))}" height="{rng.randrange(2,max(4,round(4+6*strength)))}" fill="{rng.choice(("#EFFFFF","#41DDE5","#092532"))}"/>' for _ in range(count))
        spacing=round(5+23*(1-strength))
        lines=''.join(f'<path d="M0 {y}H941" stroke="#C9FAFF" stroke-width="{.5+strength:.2f}"/>' for y in range(frame%spacing,1672,spacing))
        streaks=''.join(f'<rect x="{rng.randrange(180,600)}" y="{rng.randrange(50,1550)}" width="{rng.randrange(40,230)}" height="{rng.randrange(2,8)}" fill="#EFFFFF"/>' for _ in range(round(20*strength)))
        return svg(f'<defs><clipPath id="staticBody"><path d="{outer_body_path(state.get("nutrition_profile",{}).get("sex","Male"))}"/></clipPath></defs>'
            f'<g clip-path="url(#staticBody)" opacity="{.94*strength:.3f}">'
            f'<rect width="941" height="1672" fill="#41DDE5" opacity="{.12*strength:.3f}"/>{grains}{lines}{streaks}</g>')
    if category=="Radiation":
        return radiation_overlay(r,state.get('radiation_seconds',0.))
    if category=="Sleep":
        return sleep_overlay(state.get('sleep_seconds',0.),r['sleep_quality']=='Good')
    return artwork(category)

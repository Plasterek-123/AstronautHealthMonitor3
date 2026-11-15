"""Sleep phase composition; no invented overnight timeline."""
import math

def sleep_chart(values,hours,quality):
    colors=('#41DDE5','#C1B1FF','#51E4AE');radius=73;circ=2*math.pi*radius;offset=0;arcs=[];labels=[]
    for name,value,color in zip(('Light','Deep','REM'),values,colors):
        length=max(0,circ*value/100-4)
        arcs.append(f'<circle cx="105" cy="110" r="{radius}" fill="none" stroke="{color}" stroke-width="17" stroke-linecap="round" stroke-dasharray="{length:.3f} {circ:.3f}" stroke-dashoffset="{-offset:.3f}" transform="rotate(-90 105 110)"/>')
        offset+=circ*value/100
        y=50+len(labels)*62;minutes=round(hours*60*value/100)
        labels.append(f'<circle cx="222" cy="{y}" r="4" fill="{color}"/><text x="235" y="{y+4}" fill="#EDF8FF" font-size="13">{name}</text><text x="235" y="{y+23}" fill="{color}" font-size="16" font-weight="bold">{value:g}% · {minutes//60}h {minutes%60:02}m</text>')
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 220" font-family="sans-serif"><circle cx="105" cy="110" r="73" fill="none" stroke="#193147" stroke-width="17"/>'+''.join(arcs)+f'<text x="105" y="105" text-anchor="middle" fill="#EDF8FF" font-size="27" font-weight="bold">{hours:g}h</text><text x="105" y="128" text-anchor="middle" fill="#A3B8C8" font-size="12">{quality} sleep</text>'+''.join(labels)+'</svg>'

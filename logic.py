"""Offline demo data and presentation rules; replace sources with sensor adapters."""
import json
import math
from datetime import date, timedelta
from config import CATEGORIES, DATA_FILE, BASE_DIR
from minerals import MINERALS,reference_for

def read_json(path, default):
    try:
        result=json.loads(path.read_text(encoding="utf-8"))
        return result if isinstance(result,type(default)) else default
    except (OSError, ValueError):
        return default

def write_json(path, value):
    path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_suffix(path.suffix+".tmp")
    temporary.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding="utf-8")
    temporary.replace(path)

def load_events():
    if DATA_FILE.exists():
        return [e for e in read_json(DATA_FILE,[]) if isinstance(e,dict) and all(k in e for k in ("date","time","title"))]
    today=date.today()
    return [{"date":today.isoformat(),"time":"08:00","title":"Health check"},
            {"date":(today+timedelta(days=1)).isoformat(),"time":"09:00","title":"Sleep and recovery review"}]

def save_events(events):
    write_json(DATA_FILE,events)

def stress_score(hr, breath):
    # Explicitly a UI demo formula, NOT a validated physiological model.
    return round(max(0,min(100,(hr-55)*0.75+(breath-10)*2.5)))

def stress_label(score):
    return "Low" if score<30 else "Normal" if score<60 else "Medium" if score<80 else "High"

def readings(mode, tick):
    jitter=round(3*math.sin(tick*.27)+2*math.sin(tick*.17))
    r=dict(hr=72+jitter,pressure="110/70",spo2=98,temp=36.6,breath=15,
           tidal_volume=.0005,irregular_breathing=False,breathing_difficulty=False,
           limb_temp=34.5,sleep=7.5,awakenings=1,sleep_stages=[55,23,22],
           absorbed_dose=.00012,dose_limit_gy=.0005,dose_period="24 hours (demo)",water=1.7,external_level="Nominal (demo)",solar_event="No event in demo scenario")
    if mode=="Calm day":
        r.update(hr=62+jitter, breath=12, sleep=8.2, awakenings=0,
                 sleep_stages=[50,27,23])
    elif mode=="Light activity":
        r.update(hr=96+jitter, breath=19, temp=37.1, pressure="118/76")
    elif mode=="Short sleep":
        r.update(sleep=6.2, awakenings=3, sleep_stages=[62,16,22])
    elif mode=="Busy day":
        r.update(hr=99+jitter, breath=21, pressure="122/78")
    elif mode=="Warning":
        r.update(hr=107+jitter,spo2=93,temp=37.9,breath=21,pressure="128/82",
                 tidal_volume=.00042,limb_temp=35.3,sleep=5.7,awakenings=4,sleep_stages=[64,14,22],
                 irregular_breathing=True,external_level="Elevated (demo)")
    elif mode=="Alert":
        r.update(hr=155+jitter,spo2=88,temp=39.6,breath=29,pressure="145/90",
                 tidal_volume=.00035,limb_temp=36.4,sleep=5.3,awakenings=6,sleep_stages=[70,10,20],
                 irregular_breathing=True,breathing_difficulty=True,absorbed_dose=.00065,
                 external_level="External alert (demo)",solar_event="Simulated CME notification")
    r["stress"]=stress_score(r["hr"],r["breath"])
    r["sleep_quality"]="Good" if r["sleep"]>=7 and r["awakenings"]<=2 and r["sleep_stages"][1]>=20 else "Poor"
    return r

def radiation_status(r):
    """One shared demo state for the category, central SVG and detail panel."""
    if r['external_level']=='External alert (demo)':return 'danger'
    if r['external_level']=='Elevated (demo)' or r['absorbed_dose']>r.get('dose_limit_gy',.0005):return 'warning'
    return 'ok'

def evaluate_alerts(r):
    status={c:"ok" for c in CATEGORIES}; status["Nutrition"]="neutral"
    alerts=[]
    def add(cat,level,msg):
        if {"ok":0,"neutral":0,"warning":1,"danger":2}[level]>{"ok":0,"neutral":0,"warning":1,"danger":2}[status[cat]]:
            status[cat]=level
        alerts.append((cat,level,msg))
    if r["hr"]>=140: add("Cardiology","danger","Heart rate exceeds the demo alert threshold.")
    elif r["hr"]>100: add("Cardiology","warning","Heart rate is outside the demo resting range.")
    if r["spo2"]<=90: add("Respiration","danger","Low simulated oxygen saturation.")
    elif r["spo2"]<95: add("Respiration","warning","Oxygen saturation is below the demo range.")
    if r["breathing_difficulty"]: add("Respiration","danger","Breathing difficulty reported in this scenario.")
    if r["temp"]>=39.5: add("Temperature","danger","High simulated body temperature.")
    elif r["temp"]>=37.8: add("Temperature","warning","Elevated simulated body temperature.")
    if r["stress"]>=60: add("Stress","warning","Elevated illustrative stress score.")
    if r["sleep_quality"]=="Poor": add("Sleep","warning","Review the simulated sleep summary.")
    if r['external_level']=='Elevated (demo)':add('Radiation','warning','External detector level is elevated in the demo scenario.')
    if r["external_level"]=="External alert (demo)": add("Radiation","danger","Simulated external detector / CME event. Check mission procedures.")
    if r['absorbed_dose']>r.get('dose_limit_gy',.0005) and r['external_level']!='External alert (demo)':
        add('Radiation','warning','Absorbed dose exceeds the configured demo review level for the selected period.')
    return status,sorted(alerts,key=lambda a:0 if a[1]=="danger" else 1)

def nutrient_targets(profile):
    weight,age,height=profile["weight"],profile["age"],profile["height"]
    # Mifflin-St Jeor used as an editable demonstration estimate only.
    resting=10*weight+6.25*height-5*age+(5 if profile["sex"]=="Male" else -161)
    calories=round(resting*profile["activity"])
    return {"calories":calories,"protein":round(weight*1.2),"carbs":round(calories*.5/4),
            "fat":round(calories*.3/9),"fiber":30,"sodium":2000,"calcium":1000,
            "iron":14,"vitamin_c":80,"vitamin_d":15,
            **{key:reference_for(key,profile)["target"] for key in MINERALS}}

DEFAULT_PROFILE=dict(weight=75.,age=30,height=178.,sex="Male",activity=1.55)
NUTRIENT_UNITS={"calories":"kcal","protein":"g","carbs":"g","fat":"g","fiber":"g",
                "sodium":"mg","calcium":"mg","iron":"mg","vitamin_c":"mg","vitamin_d":"µg"}
NUTRIENT_UNITS.update({key:row["unit"] for key,row in MINERALS.items()})
FOOD_CATALOG={
    "DEMO001":dict(name="Mission meal A",calories=460,protein=26,carbs=55,fat=15,fiber=7,sodium=650,calcium=160,iron=4,vitamin_c=25,vitamin_d=3),
    "DEMO002":dict(name="Recovery snack",calories=210,protein=14,carbs=25,fat=6,fiber=4,sodium=120,calcium=220,iron=2,vitamin_c=10,vitamin_d=2),
}

def nutrition_totals(entries,day=None):
    day=day or date.today().isoformat()
    return {key:sum(float(e.get(key,0)) for e in entries if e.get("date")==day) for key in NUTRIENT_UNITS}

def ecg_svg(tick,hr,width=350,height=95):
    def g(x,c,s): return math.exp(-.5*((x-c)/s)**2)
    beat=60/max(1,hr);points=[]
    # Six seconds across the strip; the same BPM drives beat spacing and heart animation.
    for x in range(width+1):
        phase=((x/width*6+tick*.35)%beat)/beat
        v=4*g(phase,.17,.04)-6*g(phase,.385,.015)+39*g(phase,.415,.012)-13*g(phase,.45,.016)+9*g(phase,.69,.07)
        points.append(f"{x},{height*.61-v:.1f}")
    grid=''.join(f'<path d="M{x} 0V{height}" stroke="#214655" stroke-width=".5"/>' for x in range(0,width,20))
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}"><rect width="{width}" height="{height}" fill="#0C2432"/>{grid}<polyline points="{" ".join(points)}" fill="none" stroke="#51E4AE" stroke-width="2"/></svg>'

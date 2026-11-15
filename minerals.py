"""US adult dietary reference intake examples, checked 2026-11-14.

Not a mission prescription. Canonical units are mg except Se/I/Cr/Mo in micrograms.
UL = tolerable upper intake level; sodium uses CDRR, not a toxicity UL.
"""
from datetime import date
ODS='https://ods.od.nih.gov/factsheets/'
MINERALS={
 'calcium':dict(name='Calcium',symbol='Ca',unit='mg',male=1000,female=1000,upper=2500,kind='RDA',source=ODS+'Calcium-HealthProfessional/'),
 'phosphorus':dict(name='Phosphorus',symbol='P',unit='mg',male=700,female=700,upper=4000,kind='RDA',source=ODS+'Phosphorus-HealthProfessional/'),
 'magnesium':dict(name='Magnesium',symbol='Mg',unit='mg',male=420,female=320,upper=350,kind='RDA',scope='supplement',source=ODS+'Magnesium-HealthProfessional/'),
 'sodium':dict(name='Sodium',symbol='Na',unit='mg',male=1500,female=1500,upper=2300,kind='AI',limit_kind='CDRR',source='https://www.nationalacademies.org/read/25353/chapter/2'),
 'chloride':dict(name='Chloride',symbol='Cl',unit='mg',male=2300,female=2300,upper=3600,kind='AI',source='https://www.nationalacademies.org/read/10925/chapter/8'),
 'potassium':dict(name='Potassium',symbol='K',unit='mg',male=3400,female=2600,upper=None,kind='AI',source=ODS+'Potassium-HealthProfessional/'),
 'iron':dict(name='Iron',symbol='Fe',unit='mg',male=8,female=18,upper=45,kind='RDA',source=ODS+'Iron-HealthProfessional/'),
 'copper':dict(name='Copper',symbol='Cu',unit='mg',male=.9,female=.9,upper=10,kind='RDA',source=ODS+'Copper-HealthProfessional/'),
 'manganese':dict(name='Manganese',symbol='Mn',unit='mg',male=2.3,female=1.8,upper=11,kind='AI',source=ODS+'Manganese-HealthProfessional/'),
 'fluoride':dict(name='Fluoride',symbol='F',unit='mg',male=4,female=3,upper=10,kind='AI',source=ODS+'Fluoride-HealthProfessional/'),
 'zinc':dict(name='Zinc',symbol='Zn',unit='mg',male=11,female=8,upper=40,kind='RDA',source=ODS+'Zinc-HealthProfessional/'),
 'selenium':dict(name='Selenium',symbol='Se',unit='µg',male=55,female=55,upper=400,kind='RDA',source=ODS+'Selenium-HealthProfessional/'),
 'iodine':dict(name='Iodine',symbol='I',unit='µg',male=150,female=150,upper=1100,kind='RDA',source=ODS+'Iodine-HealthProfessional/'),
 'chromium':dict(name='Chromium',symbol='Cr',unit='µg',male=35,female=25,upper=None,kind='AI',source=ODS+'Chromium-HealthProfessional/'),
 'molybdenum':dict(name='Molybdenum',symbol='Mo',unit='µg',male=45,female=45,upper=2000,kind='RDA',source=ODS+'Molybdenum-HealthProfessional/'),
}

def reference_for(key,profile):
    row=dict(MINERALS[key]);age=float(profile.get('age',30));sex=profile.get('sex','Male')
    row['target']=row['male' if sex=='Male' else 'female']
    row['supported']=19<=age<=100
    if key=='calcium':
        row['target']=1200 if age>=71 or (sex=='Female' and age>=51) else 1000
        row['upper']=2000 if age>=51 else 2500
    elif key=='magnesium' and age<=30:row['target']=400 if sex=='Male' else 310
    elif key=='iron' and age>=51:row['target']=8
    elif key=='phosphorus' and age>=71:row['upper']=3000
    elif key=='chromium' and age>=51:row['target']=30 if sex=='Male' else 20
    elif key=='chloride':row['target']=1800 if age>=71 else 2000 if age>=51 else 2300
    return row

def convert_amount(value,source_unit,target_unit):
    aliases={'ug':'µg','mcg':'µg','μg':'µg'}
    a,b=aliases.get(source_unit,source_unit),aliases.get(target_unit,target_unit)
    factors={'g':1000.,'mg':1.,'µg':.001}
    if a not in factors or b not in factors:raise ValueError('Unsupported mass unit')
    number=float(value)
    if number<0 or not __import__('math').isfinite(number):raise ValueError('Invalid amount')
    return number*factors[a]/factors[b]

def intake_for(entries,key,day=None,source=None):
    today=day or date.today().isoformat();total=0.;complete=True;count=0
    for entry in entries:
        if entry.get('date')!=today:continue
        entry_source=entry.get('source','food')
        if source and source!=entry_source:continue
        if entry.get('single_mineral') and entry['single_mineral']!=key:continue
        count+=1
        value=entry.get(key)
        if value is None:complete=False
        else:
            try:
                number=float(value)
                if number<0 or not __import__('math').isfinite(number):raise ValueError
                total+=number
            except (ValueError,TypeError):complete=False
    return dict(total=total,complete=complete,count=count)

def assess_mineral(key,profile,entries,day_complete=False):
    reference=reference_for(key,profile)
    intake=intake_for(entries,key)
    checked=intake_for(entries,key,source='supplement') if reference.get('scope')=='supplement' else intake
    upper=reference['upper']
    status='neutral';label='No entries' if intake['count']==0 else 'Logged intake'
    if not reference['supported']:label='Adult reference unavailable'
    elif upper is not None and checked['total']>upper:
        status='warning' if reference.get('limit_kind')=='CDRR' else 'danger'
        label='Above CDRR reference' if status=='warning' else 'Above reference UL'
        if reference.get('scope')=='supplement':label='Supplement UL exceeded'
    elif not intake['complete']:label='Incomplete food data'
    elif day_complete and intake['count'] and intake['total']<reference['target']:
        status='warning';label='Below daily target · logged intake'
    elif intake['count'] and intake['total']>=reference['target']:
        status='ok';label='Target reached' if upper else 'Target reached · UL not set'
    return dict(reference=reference,intake=intake,checked=checked,status=status,label=label)

def mineral_alerts(profile,entries,day_complete=False):
    result=[]
    for key in MINERALS:
        assessment=assess_mineral(key,profile,entries,day_complete)
        if assessment['status'] in ('danger','warning'):
            ref=assessment['reference'];value=assessment['checked']['total']
            result.append(('Nutrition',assessment['status'],f'{ref["name"]}: {value:g} {ref["unit"]} — {assessment["label"]}.'))
    return result

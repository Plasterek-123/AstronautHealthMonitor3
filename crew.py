"""Local demo crew records; nutrition and manual inputs are isolated per member."""
from copy import deepcopy
from config import DATA_DIR
from logic import read_json,write_json,DEFAULT_PROFILE,readings,stress_score

CREW={'crew_01':'Crew member 01','crew_02':'Crew member 02','crew_03':'Crew member 03'}

def initialize_crew(state,legacy):
    saved=read_json(DATA_DIR/'crew.json',{})
    records=saved.get('records',{})
    for key in CREW:
        default={'nutrition_profile':deepcopy(DEFAULT_PROFILE),'nutrition_entries':[],
                 'nutrition_targets':{},'nutrition_closed_days':[],'manual_enabled':False,'manual_values':{}}
        if key=='crew_01':default.update(nutrition_profile={**DEFAULT_PROFILE,**legacy.get('profile',{})},
            nutrition_entries=legacy.get('entries',[]),nutrition_targets=legacy.get('targets',{}))
        records[key]={**default,**records.get(key,{})}
    state['own_crew_id']='crew_01'
    state['crew_records']=records
    key=state['own_crew_id']  # Emergency review never changes the signed-in profile.
    state['crew_id']=key
    state.update(deepcopy(records[key]))

def sync_crew(state):
    if 'crew_records' not in state:return
    keys=('nutrition_profile','nutrition_entries','nutrition_targets','nutrition_closed_days','manual_enabled','manual_values')
    state['crew_records'][state['crew_id']]={k:deepcopy(state.get(k,{})) for k in keys}

def persist_crew(state):
    sync_crew(state)
    write_json(DATA_DIR/'crew.json',{'selected':state.get('crew_id','crew_01'),'records':state.get('crew_records',{})})

def activate_crew(state,key):
    if key not in CREW:return
    sync_crew(state);state['crew_id']=key
    state.update(deepcopy(state['crew_records'][key]));persist_crew(state)

def current_readings(state):
    result=readings(state['mode'],state['tick'])
    if state.get('manual_enabled'):
        values=state.get('manual_values',{})
        result.update(values)
        if 'stress' not in values:result['stress']=stress_score(result['hr'],result['breath'])
        result['sleep_quality']='Good' if result['sleep']>=7 and result['awakenings']<=2 and result['sleep_stages'][1]>=20 else 'Poor'
    return result


def is_own_profile(state):
    return state.get('crew_id','crew_01')==state.get('own_crew_id','crew_01')

def critical_categories(state,values):
    from logic import evaluate_alerts
    from minerals import mineral_alerts
    _,alerts=evaluate_alerts(values)
    alerts+=mineral_alerts(state['nutrition_profile'],state['nutrition_entries'])
    return {cat for cat,level,_ in alerts if level=='danger'}


def crew_emergencies(state):
    """Return only critical events from other members; routine records stay out of the view."""
    from logic import evaluate_alerts
    from minerals import mineral_alerts
    events=[]
    for key in CREW:
        if key==state.get('own_crew_id','crew_01'):continue
        record=state.get('crew_records',{}).get(key,{})
        if not record:continue
        snapshot={**state,**record,'crew_id':key,'mode':record.get('mode','Normal')}
        values=current_readings(snapshot)
        _,alerts=evaluate_alerts(values)
        alerts+=mineral_alerts(snapshot['nutrition_profile'],snapshot['nutrition_entries'])
        critical=[a for a in alerts if a[1]=='danger']
        if critical:events.append(dict(id=key,name=CREW[key],alerts=critical,values=values))
    return events


CREW_ALERT_SCENARIOS = {
    'Heart rate alert': {'hr': 155},
    'Low oxygen': {'spo2': 88},
    'High temperature': {'temp': 39.6},
    'Radiation alert': {'absorbed_dose': .00065, 'external_level': 'External alert (demo)',
                        'solar_event': 'External detector alert'},
    'Multiple alerts': None,
}

def set_crew_alert_scenario(state, key, scenario):
    """Change a separate crew record without exposing routine measurements."""
    if key not in CREW or key == state.get('own_crew_id', 'crew_01'):
        raise ValueError('Select another crew member.')
    if scenario != 'Clear alerts' and scenario not in CREW_ALERT_SCENARIOS:
        raise ValueError('Unknown crew scenario.')
    record = state['crew_records'][key]
    if scenario == 'Clear alerts':
        record.update(mode='Normal', manual_enabled=False, manual_values={})
    else:
        values = readings('Alert' if scenario == 'Multiple alerts' else 'Normal', state['tick'])
        values.update(CREW_ALERT_SCENARIOS[scenario] or {})
        values['stress'] = stress_score(values['hr'], values['breath'])
        record.update(mode='Normal', manual_enabled=True, manual_values=values)
    persist_crew(state)

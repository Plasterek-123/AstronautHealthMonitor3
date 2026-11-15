"""Preserve supplied SVG paths; animate the original heart groups at render time."""
from pathlib import Path
from functools import lru_cache
import math,copy,xml.etree.ElementTree as ET

ASSETS=Path(__file__).parent/'assets'
NS='http://www.w3.org/2000/svg'
ET.register_namespace('',NS)

@lru_cache(maxsize=6)
def organ_template(category,sex):
    path=ASSETS/f'{category.lower()}_original_{sex.lower()}.svg'
    if not path.exists():return None
    root=ET.parse(path).getroot()
    # The original contour is drawn by the shared model layer. Keep every organ path.
    for child in list(root):
        if child.tag==f'{{{NS}}}path' and not child.get('id'):root.remove(child)
    if category=='Cardiology':
        for group in list(root.iter()):
            for i,child in enumerate(list(group)):
                if child.tag==f'{{{NS}}}g' and child.get('transform','').startswith('matrix(0.43,'):
                    wrapper=ET.Element(f'{{{NS}}}g',{'transform':'__HEART_MOTION__'})
                    group.remove(child);wrapper.append(child);group.insert(i,wrapper)
    return ET.tostring(root,encoding='unicode')

def original_organs(category,sex):
    source=organ_template(category,sex)
    return source.replace('__HEART_MOTION__','translate(0 0)') if source else None

def beating_original_heart(sex,phase):
    source=organ_template('Cardiology',sex)
    if not source:return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 941 1672"/>'
    pulse=math.exp(-((phase-.13)/.085)**2)+.28*math.exp(-((phase-.34)/.11)**2)
    scale=1+.11*pulse
    # Heart groups share this local pivot before their original parent translation.
    motion=f'translate(476 454) scale({scale:.5f}) translate(-476 -454)'
    return source.replace('__HEART_MOTION__',motion)

"""Independent motion for the supplied cloud, moon and star SVG groups."""
import math
import xml.etree.ElementTree as ET
from functools import lru_cache
from config import ASSET_DIR

@lru_cache(maxsize=1)
def sleep_groups():
    root=ET.parse(ASSET_DIR/'sleep_clouds_original.svg').getroot()
    ET.register_namespace('','http://www.w3.org/2000/svg')
    return tuple(ET.tostring(group,encoding='unicode') for group in root)

def sleep_overlay(seconds,good=True):
    groups=[]
    for i,source in enumerate(sleep_groups()):
        cloud=i<4
        phase=i*1.83
        dx=(15 if cloud else 8)*math.sin(seconds*(.60+i*.035)+phase)
        dy=(20 if cloud else 11)*math.sin(seconds*(.78+i*.045)+phase*.71)
        twinkle=.65+.35*math.sin(seconds*(1.1+i*.039)+phase) if not cloud else 1.
        opacity=twinkle if good or cloud else .23*twinkle
        groups.append(f'<g transform="translate({dx:.3f} {dy:.3f})" opacity="{opacity:.3f}">{source}</g>')
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 941 1672" style="fill-rule:evenodd;clip-rule:evenodd;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;">'+''.join(groups)+'</svg>'

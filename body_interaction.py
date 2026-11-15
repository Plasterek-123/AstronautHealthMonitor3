"""Polygon hit testing in the original 941 x 1672 body canvas."""
import re
from functools import lru_cache
from config import BODY_FILE

REGIONS={
    'Cardiology':[(438,370),(532,365),(544,450),(526,520),(444,520)],
    'Respiration':[(331,330),(480,330),(480,550),(343,550),(319,420)],
    'Nutrition':[(346,550),(590,550),(608,750),(558,905),(380,905),(333,750)],
    'Sleep':[(380,26),(559,26),(570,135),(376,135)],
    'Stress':[(376,135),(570,135),(552,250),(605,324),(335,324),(393,251)],
    'Radiation':[(614,315),(690,339),(721,535),(746,624),(875,872),(784,948),(703,776),(635,577)],
    'Temperature':[(320,315),(248,336),(218,535),(193,624),(62,872),(158,948),(234,776),(307,577)],
}
LEG_REGIONS=[[(337,893),(463,930),(458,1220),(435,1550),(437,1638),(308,1638),(335,1300)],
             [(480,930),(606,893),(607,1300),(635,1638),(506,1638),(507,1550),(483,1220)]]

def point_in_polygon(x,y,points):
    inside=False
    for (ax,ay),(bx,by) in zip(points,points[1:]+points[:1]):
        cross=(x-ax)*(by-ay)-(y-ay)*(bx-ax)
        if abs(cross)<1e-6 and min(ax,bx)<=x<=max(ax,bx) and min(ay,by)<=y<=max(ay,by):return True
        if (ay>y)!=(by>y) and x<(bx-ax)*(y-ay)/(by-ay)+ax:inside=not inside
    return inside

@lru_cache(maxsize=2)
def silhouette_polygon(sex="Male"):
    source=(BODY_FILE.parent/'assets/body_female.svg' if sex=='Female' else BODY_FILE.parent/'assets/body_original_male.svg').read_text(encoding='utf-8')
    path=re.search(r'<path\b[^>]*\bd="([^"]+)"',source).group(1)
    first=re.split('[Zz]',path,maxsplit=1)[0]
    return [(float(x),float(y)) for x,y in re.findall(r'[ML]([0-9.]+),([0-9.]+)',first)]

def category_at(x,y,sex="Male"):
    # Ignore empty canvas, including space between the legs and beside the hands.
    if not point_in_polygon(x,y,silhouette_polygon(sex)):return None
    for category,polygon in REGIONS.items():
        if point_in_polygon(x,y,polygon):return category
    if any(point_in_polygon(x,y,p) for p in LEG_REGIONS):return 'Temperature'
    # Remaining body pixels still select a nearby anatomical region.
    if y<135:return 'Sleep'
    if y<325:return 'Stress'
    if y>900:return 'Temperature'
    if y>550:return 'Nutrition'
    return 'Cardiology' if x>480 else 'Respiration'

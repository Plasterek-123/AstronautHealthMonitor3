"""Original user-provided SVG icons, tinted only at render time for contrast."""
from functools import lru_cache
import flet as ft
from config import ASSET_DIR,CATEGORIES,CYAN

@lru_cache(maxsize=12)
def icon_source(name):
    path=ASSET_DIR/'icons'/(name+'.svg')
    try:return path.read_text(encoding='utf-8')
    except OSError:return None

def custom_icon(name,size=24,color=CYAN,fallback=ft.Icons.CIRCLE):
    source=icon_source(name)
    return ft.Image(src=source,width=size,height=size,fit=ft.BoxFit.CONTAIN,
                    color=color,color_blend_mode=ft.BlendMode.SRC_IN) if source else ft.Icon(fallback,size=size,color=color)

def category_icon(category,size=24,color=CYAN):
    return custom_icon(CATEGORIES[category]['module'],size,color,CATEGORIES[category]['icon'])

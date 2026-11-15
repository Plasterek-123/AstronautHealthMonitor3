"""Shared appearance, category metadata and body coordinates (941 x 1672)."""
from pathlib import Path
import flet as ft

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_FILE = BASE_DIR / "calendar_events.json"  # preserve existing calendars
BODY_FILE = BASE_DIR / "sylwetka_czlowieka_kontur.svg"
ASSET_DIR = BASE_DIR / "assets"
BG, PANEL, CARD, BORDER = "#0B1423", "#111F32", "#18283D", "#2B405C"
WHITE, GRAY, CYAN = "#EDF8FF", "#A9B8CA", "#68C7DD"
GREEN, YELLOW, RED, VIOLET = "#62CEA3", "#E4BE67", "#ED7180", "#B7ACDF"
STATUS_COLOR = {"ok": GREEN, "warning": YELLOW, "danger": RED, "neutral": GRAY}
STATUS_TEXT = {"ok": "Within range", "warning": "Attention", "danger": "Alert", "neutral": "Not assessed"}
CATEGORIES = {
    "Cardiology": {"icon": ft.Icons.FAVORITE, "description": "Heart rate, ECG and blood pressure", "module": "cardiology"},
    "Respiration": {"icon": ft.Icons.AIR, "description": "Breathing depth, rhythm and symptoms", "module": "respiration"},
    "Temperature": {"icon": ft.Icons.THERMOSTAT, "description": "Body and limb temperature map", "module": "temperature"},
    "Stress": {"icon": ft.Icons.PSYCHOLOGY, "description": "Stress score and trends", "module": "stress"},
    "Sleep": {"icon": ft.Icons.BEDTIME, "description": "Sleep duration, awakenings and stages", "module": "sleep"},
    "Radiation": {"icon": ft.Icons.WARNING_AMBER, "description": "Daily exposure and dose calculator", "module": "radiation"},
    "Nutrition": {"icon": ft.Icons.RESTAURANT, "description": "Personal targets and food intake", "module": "nutrition"},
}
# Every overlay uses the same canvas as the silhouette. Replace files in assets/.
OVERLAYS = {name: ASSET_DIR / (entry["module"] + ".svg") for name,entry in CATEGORIES.items()}

def txt(value, size=13, color=WHITE, bold=False):
    return ft.Text(value, size=size, color=color, weight=ft.FontWeight.BOLD if bold else None)

def panel_gradient():
    return ft.LinearGradient(begin=ft.Alignment.TOP_LEFT,end=ft.Alignment.BOTTOM_RIGHT,
        colors=["#243145","#18263B","#111D30"],stops=[0,.4,1])

def box(content, pad=14):
    return ft.Container(content=content, padding=pad, bgcolor=PANEL,gradient=panel_gradient(),
                        border_radius=14, border=ft.Border.all(1,BORDER))

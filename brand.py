"""Original HALO artwork, with its native proportions preserved."""
import flet as ft
from config import ASSET_DIR

def logo():
    return ft.Image(src=(ASSET_DIR/'halo_original_logo.svg').read_bytes(),
                    width=100, height=72, fit=ft.BoxFit.CONTAIN)

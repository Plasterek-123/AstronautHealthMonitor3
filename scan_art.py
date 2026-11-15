"""A decorative scanner sweeps the original body without covering readings."""
import math
from overlays import outer_body_path,svg

def scan_svg(seconds,sex='Male'):
    y=35+1590*(.5-.5*math.cos(seconds*math.tau/8))
    return svg(f'''<defs>
      <clipPath id="overviewScanBody"><path d="{outer_body_path(sex)}"/></clipPath>
      <linearGradient id="overviewScanGlow" x1="0" y1="0" x2="0" y2="1">
        <stop stop-color="#80DCC8" stop-opacity="0"/>
        <stop offset=".52" stop-color="#80DCC8" stop-opacity=".22"/>
        <stop offset="1" stop-color="#80DCC8" stop-opacity="0"/>
      </linearGradient>
    </defs><g clip-path="url(#overviewScanBody)">
      <rect x="0" y="{y-55:.2f}" width="941" height="110" fill="url(#overviewScanGlow)"/>
      <path d="M0 {y:.2f}H941" fill="none" stroke="#8BE2D0" stroke-width="5" opacity=".8"/>
      <path d="M0 {y:.2f}H941" fill="none" stroke="#E3FFF7" stroke-width="1.8" opacity=".9"/>
    </g>''')

"""Category camera frames in the original silhouette coordinate system."""
import re

FULL_BODY=(0.,0.,941.,1672.)
FRAMES={
    'Respiration':(180.,0.,580.,900.),
    'Sleep':(115.,-45.,710.,400.),
    'Nutrition':(180.,0.,580.,900.),
}

def frame_for(category):
    return FRAMES.get(category,FULL_BODY)

def frame_svg(source,frame):
    box=' '.join(f'{v:.3f}' for v in frame)
    def root(match):
        header=re.sub(r'viewBox="[^"]*"',f'viewBox="{box}"',match.group(0),count=1)
        header=re.sub(r'\bwidth="[^"]*"',f'width="{frame[2]:.3f}"',header,count=1)
        return re.sub(r'\bheight="[^"]*"',f'height="{frame[3]:.3f}"',header,count=1)
    return re.sub(r'<svg\b[^>]*>',root,source,count=1)

def interpolate_frame(start,target,t):
    """Interpolate center and zoom; retain natural SVG proportions."""
    sx,sy,sw,sh=start;tx,ty,tw,th=target
    width=sw*(tw/sw)**t;height=sh*(th/sh)**t
    cx=(sx+sw/2)*(1-t)+(tx+tw/2)*t
    cy=(sy+sh/2)*(1-t)+(ty+th/2)*t
    return (cx-width/2,cy-height/2,width,height)

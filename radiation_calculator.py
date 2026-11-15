"""Coefficients transcribed from the supplied reference table."""
import math
RADIATION_WEIGHTS={'xray':('X-rays / beta / gamma',1.),'thermal':('Thermal neutrons',4.5),'alpha':('Alpha particles',20.)}
TISSUE_WEIGHTS={'gonads':('Gonads',.25),'breast':('Breast',.15),'marrow':('Red bone marrow',.12),'lungs':('Lungs',.12),'bone':('Bone surface',.03),'skin':('Skin',.01),'whole':('Whole body',1.)}
UNITS={'µGy':1e-6,'mGy':1e-3,'Gy':1.}
def dose_values(dose,unit,radiation,tissue,energy=None,mass=None):
    if energy is not None and (not math.isfinite(float(mass)) or float(mass)<=0):raise ValueError('Mass must be positive.')
    d=float(dose)*UNITS[unit] if energy is None else float(energy)/float(mass)
    if not math.isfinite(d) or d<0:raise ValueError('Enter finite, nonnegative values.')
    h=d*RADIATION_WEIGHTS[radiation][1]
    return d,h,h*TISSUE_WEIGHTS[tissue][1]
def add_tissue(terms,key,value):
    if terms and (('whole' in terms and key!='whole') or (key=='whole' and any(k!='whole' for k in terms))):raise ValueError('Clear the sum before combining whole body with individual tissues.')
    terms[key]=value

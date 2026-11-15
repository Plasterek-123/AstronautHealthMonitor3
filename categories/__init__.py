"""Independent category views. Each module exposes build(context)."""
from . import cardiology, respiration, temperature, stress, sleep, radiation, nutrition
BUILDERS={"Cardiology":cardiology.build,"Respiration":respiration.build,
          "Temperature":temperature.build,"Stress":stress.build,"Sleep":sleep.build,
          "Radiation":radiation.build,"Nutrition":nutrition.build}

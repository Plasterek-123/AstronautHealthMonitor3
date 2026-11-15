# Astronaut Health Monitor

Offline Flet 1.1.2 prototype. Run `python main.py` using the existing project environment.
All generated physiology, radiation events, stress trends and sleep stages are **demo data**.

## Project modules

| File | Responsibility |
| --- | --- |
| main.py | App state, navigation and simulation loop |
| config.py | Colors, categories, overlay filenames and body hit areas |
| logic.py | Data sources, demo rules, persistence and nutrition calculations |
| monitoring_view.py | Fixed vital-sign panel, body interaction and grouped alerts |
| calendar_view.py | Offline calendar |
| guidebook_view.py | English glossary |
| ice_view.py | Combined emergency information and assistant |
| settings_view.py | Normal / Warning / Alert scenarios and pause |
| overlays.py | Dynamic temperature, stress and sleep visuals |
| categories/ | One independent view per category |
| assets/ | Category artwork on a common 941 × 1672 canvas |

Categories: **Cardiology, Respiration, Temperature, Stress, Sleep, Radiation, Nutrition**.
Nutrition replaces Hydration. Navigation matches the supplied project: Monitoring, Calendar,
Guidebook, ICE & Assistant, Settings. Category rings remain visible above every screen.

The left panel is ordered: Heart rate + ECG → Blood pressure → Temperature and SpO₂ side by
side → Radiation. Side panels scroll independently while the whole body remains visible.

## Category ownership

Each module in `categories/` exports `build(context)`. It owns its view and form callbacks.
The context provides current readings, app state, persistence, page updates and overlay refresh.
Demo sources live in `logic.readings`; replace these with sensor adapters independently.

## Body assets

`sylwetka_czlowieka_kontur.svg` is the base outline. `config.OVERLAYS` maps category names to
English filenames. Keep viewBox `0 0 941 1672` to align custom SVGs automatically.
`assets/respiration.svg` embeds the supplied transparent PNG without altering the drawing;
it is a raster image wrapped in SVG, not vectorized artwork. It can be replaced with a true SVG.
`assets/nutrition.svg` similarly embeds the supplied digestive-system PNG.
Cardiology and radiation use editable schematic SVGs. Temperature heat values,
stress head noise and sleep cloud / moon visuals are generated in `overlays.py`.
Body points are navigation shortcuts rather than physical sensor locations.

## Data and integration boundaries

- `calendar_events.json`: existing calendar entries are preserved. User-authored event titles
  are not automatically translated.
- `ice_profile.json`: local ICE contact and notes. Existing entries are preserved.
- `data/nutrition.json`: profile, nutrient target overrides and daily dated food entries.
- `data/mission_procedures.json`: optional approved mission procedures keyed by
  `Decompression`, `Cardiac emergency`, `Injury / bleeding`. No unapproved medical procedure is
  presented as mission guidance.
- Nutrition lookup accepts `DEMO001` / `DEMO002` and manual scanner input. No camera scanner
  or real food database is connected. Food values are fictional. Replace `FOOD_CATALOG` with
  an actual validated data source.
- Calorie needs are an editable equation-based example. Activity is an entered factor;
  accelerometer integration is pending. Nutrient defaults are illustrative and customizable.
- Stress uses an explicitly unvalidated presentation formula from heart and respiratory rates.
  Hour/week charts are generated examples, not recorded history.
- Sleep duration and stage percentages are simulated. There is no validated sleep classifier.
- Radiation separates absorbed Gy, equivalent Sv and one tissue's effective-dose contribution.
  Weighting inputs are demo values. No universal dose-risk threshold is inferred. CME and
  external detector messages come from the selected demo scenario, not a live feed.

Category views show a reading snapshot and provide a refresh button; the left vital signs,
category statuses, alerts and dynamic body overlays update continuously.

## Body animations and thermal view

- Respiration expands only the lung / diaphragm region of the supplied artwork. The head
  and body outline stay fixed. Cycle duration follows the current simulated breaths/min.
- Cardiology uses a two-part pulse synchronized with the simulated BPM. Phase is integrated
  from elapsed time, so changing the rate does not jump the animation.
- Settings → Pause / resume freezes both animations; leaving Monitoring avoids frame rendering.
- Temperature fills the body's external contour with a continuous, fixed 30–40 °C palette.
  The selected limb has its own gradient, target marker and reading. Left/right use the
  astronaut's perspective. The legend does not automatically rescale between scenarios.
- Only average body temperature and selected-limb temperature are supplied. Other colors
  are an illustrative interpolated field, not actual thermography or clinical risk levels.


## Responsive layout and alerts

The body uses silhouette-clipped polygon hit testing without marker dots. The bell remains in the global header on every screen and opens alerts grouped by the same seven categories. Nutrition gets a wider detail workspace; other categories use the full available detail height. Below 850 px the layout stacks vertically and category rings scroll horizontally. The whole body remains visible within its own area. Heart/lung animations respect the simulation pause. Stress static is stronger at lower stress by the chosen visual mapping.

## Minerals

Nutrition displays 15 mineral intake cards, age/sex references, missing composition, upper references and daily logs. Add food via a demo code or log a single mineral with unit and food/supplement source. Mineral alerts feed the same global bell. Sources, age adjustments and corrections are documented in docs/MINERAL_REFERENCES.md. These are US adult DRI examples, not individualized mission prescriptions.

Phone-sized layouts are supported. Running the desktop Python process does not expose it to a phone: use a Flet web run or a packaged mobile build for an actual device. No server or public deployment is configured automatically.


## Category motion

Category changes crossfade the previous and new body overlay over 650 ms. Nutrition smoothly shrinks the body and expands its workspace; returning restores the larger silhouette. Detail panels fade between categories. Rapid clicks retarget the current geometry, and resizing settles to the new viewport. These transitions continue while the sensor simulation is paused. Stress static has nonlinear changes in grain density, grain size, line spacing and contrast: lower stress gives stronger static, and score 100 gives a clear silhouette.


## Category camera frames

Respiration and Nutrition crop below the navel and enlarge the upper body. Sleep zooms onto the head; Cardiology focuses the heart and chest. Stress, Temperature and Radiation show the full silhouette. Category cameras interpolate center and zoom with easing, crossfade aligned organ layers, and return smoothly when cleared. Hit testing converts visible positions back into original anatomical coordinates. Camera frames are editable in body_camera.py. Transition timings are 750–850 ms. No automated or visual animation tests were run for this camera change, per request.


## Critical alerts

Alert severity uses existing demo `danger` events; no new medical thresholds are introduced. The menu has All alerts and Critical tabs, with counts and category filters. Critical groups precede every warning group. Opening the bell defaults to Critical while any critical event is active. A slow red pulse (1.4 s cycle) continues on every tab and while sensor readings are paused, and clears when the critical events clear. Opening the menu does not resolve or acknowledge an ongoing event.


## Crew, data source and privacy

Select crew member in the Monitoring bar. Crew member 01 is the local signed-in demo identity. The other two are demo crew profiles: routine values, food logs and settings are hidden, and only active critical alerts with related measurements are shared. This is UI-level privacy in a local prototype; real identity, consent and server-side authorization are required before using real crew data. Crew member 01 retains the legacy nutrition import; crew.json stores per-person nutrition and manual test inputs. Manual values are enabled and saved from Settings, with source labels; no sensor integration is implied.

Nutrition now has stable Overview, Food log, Minerals and Profile sections. Logging intake updates values without rebuilding the detail screen or resetting the selected section. Cardiology and stress BPM fields update with live readings. The synthetic ECG uses a six-second time base and beat spacing from BPM. Low stress now means less chaotic static. Sleep uses a donut showing phase proportions and durations; radiation grows and changes color with the external demo scenario, not a new dose threshold.


## Crew emergency access

The signed-in identity stays on Crew member 01. The header Crew button opens a separate critical-alert drawer/dialog; it does not switch monitoring profiles, rewrite selection state or rebuild personal screens. Only members with active critical events are selectable. Their assistance view includes the alert and related vital signs; routine measurements, nutrition logs and personal settings are unavailable there. The global bell includes crew critical events, and returns to the relevant emergency view when clicked. Resolved critical events disappear from that view. UI privacy remains a prototype behavior, not server-side authorization.


## Visual layout and daily review

Cardiology returns to a full-body schematic with red arteries, blue veins and a pulsing heart. The sketch is illustrative, not a clinical vascular atlas. Nutrition detail width is capped at 560 px on desktop, with more space for the model and compact mineral cards. Category rings are centered. The Female profile uses a stylized female outline on the same organ canvas and the existing sex/age-specific mineral targets; change sex under Nutrition → Profile and save. The outline is an illustration, not an anatomical measurement.

Low mineral intake is a noncritical Attention reminder after explicitly reviewing the completed daily log. Only complete known values are assessed; absent or incomplete food composition is not a deficiency. Upper-reference highlights and magnesium supplement-only handling are preserved. Reference definitions: https://ods.od.nih.gov/HealthInformation/nutrientrecommendations.aspx .

Radiation adds an outline and a same-period editable demo review level. 500 µGy is an arbitrary UI demo setting, not a NASA safety limit. The loadable NASA example is the historical Curiosity RAD Mars surface GCR absorbed-dose rate of about 210 µGy/day (Aug 2012–Jun 2013), from https://science.nasa.gov/photojournal/radiation-measurements-on-mars/ . It is environmental instrument data, not current crew exposure. Gy, dose equivalent in Sv and effective dose are not interchangeable. No live detector feed is connected.

The calendar fits the normal desktop viewport, with a bounded agenda and event creation in a dialog. Types automatically choose colors from titles unless explicitly assigned; older events are preserved. At phone widths the month and agenda stack, with the month kept visible and the agenda independently scrollable.


## Original SVG animation

The supplied original male/female cardiovascular SVGs and female respiratory/digestive SVGs are stored unchanged in assets/*_original_*.svg. Rendering preserves their paths and colors, extracts the outline separately, and applies a synchronized transform only to the original heart parts. The prior simplified vascular drawing is no longer used. Cardiology adds a larger synthetic ECG strip in its detail view. Nutrition shows a schematic moving bolus along the esophagus; it is illustrative, not a digestive measurement. Radiation now has a broad surrounding field; it turns red for an external critical event or when the configured demo review level is exceeded. Settings offers fictional Alex/Maya male/female demo profiles without changing the signed-in identity or deleting food logs.


## Guidebook and supplied sleep artwork

The supplied Markdown Guidebook replaces the old glossary view; ICE is a chapter inside it, with no separate bottom navigation entry. The remaining destinations are Monitoring, Calendar, Guidebook and Settings. Supplied clouds, moon and stars retain their original paths and colors, with independent slow floating and twinkling animations. The Sleep camera includes the full decoration. PEARTO is the Nutrition category icon. Radiation uses a bounded circular zone centered on the warning symbol, with no body-shaped glow or full-body field.


## Animation and Guidebook controls

Sleep has stronger independent floating and twinkling, with the stage chart under the head artwork. Nutrition uses a green icon/ring for its normal or unassessed demo state; actual warnings still retain their alert color. Radiation now displays the original category SVG alone with incoming particle streaks; their count rises with the demo exposure and external alert scenario, and their lengths vary over time. These are illustrative photons, not a physical simulation. Guidebook chapters collapse automatically after selection. Its compact CDSS chat searches local article titles, tags and contents and opens matching documents; it does not generate diagnoses or treatment advice.


## Subtle mission palette and radiation status

The full content area has a restrained navy gradient with opaque, toned panel surfaces for text contrast. The shared accent palette is less saturated. Radiation restores the complete original body silhouette with the supplied warning SVG on the chest and incoming streaks across the canvas. Photon density and length vary with demo intensity. Normal is green, elevated external readings or a demo review-level exceedance are amber, and the external critical scenario is red. The category ring, body symbol, photons and detail panel use the same classification. These are demonstration states, not clinical exposure thresholds.


## Overview scanner and reference styling

Category buttons return to left alignment. The reference-inspired finish uses a restrained radial navy background and a soft slate highlight on card surfaces and the category bar. In the Monitoring overview, an eight-second scan line moves down and back up the original body, clipped to its contour. It is a decorative interface animation, independent of sensor pause, and hides when a category is selected or another tab is open.


## HALO presentation finish

Application name: Health Assessment & Life Overview (HALO). The supplied orbit-logo-z-aureola.svg is used unchanged in the header. Category views omit implementation and demonstration footnotes; the underlying sources remain the local simulator or manual inputs selected in Settings. No live sensor or medical certification has been added. Radiation contains the daily absorbed dose and a compact calculator for D=E/m, HT=wR*D and the sum of selected tissue contributions. The wR/wT coefficients reproduce the user-supplied table, including thermal neutrons 4.5 and gonads 0.25; this historical table is not presented as a current NASA standard. Whole-body contributions cannot be mixed with organ contributions.

Guidebook chapter options remain open. Two new Markdown workflows include local NASA photographs, source links and original step diagrams: periodic blood-pressure assessment and initial external-bleeding control. They are compiled from NASA requirements and ground first-aid guidance, with AHA measurement details; they are not issued NASA flight checklists. Images are loaded locally by guide_media.py. Existing calendar appointments are retained alongside the new schedule.


## GUI logo and completed Guidebook chapters

The header uses a generated cyan/teal HALO logo with a centered halo, kept at fixed aspect ratio. Original supplied SVG artwork remains in assets/halo_logo.svg. Every Guidebook chapter has content, including concise pharmacy, medical-conference, exposure-record and units cards. The supplied 00_ice_cpr.md replaces the older CPR card, with an offline NASA Expedition 65 training photograph and source credit. Arrest recognition no longer depends on waiting for zero BPM or falling oxygen saturation. Vehicle-specific restraint details and advanced drug directions are delegated to approved training and the medical lead.

# guidebook_view.py
from pathlib import Path
from guide_media import article_controls
import flet as ft
from guide_assistant import build_guide_assistant
from config import box, txt, WHITE, GRAY, CYAN, GREEN, YELLOW, RED, PANEL, CARD, BORDER

GUIDEBOOK_DIR = Path(__file__).resolve().parent / "guidebook_data"

CHAPTERS = {
    "ALL": {
        "title": "All Chapters",
        "icon": ft.Icons.APPS,
        "color": CYAN,
    },
    "ICE": {
        "title": "ICE",
        "icon": ft.Icons.WARNING_AMBER,
        "color": RED,
    },
    "EXAMS": {
        "title": "Medical Exams",
        "icon": ft.Icons.BIOTECH,
        "color": GREEN,
    },
    "SPACE_MED": {
        "title": "Space Physiology",
        "icon": ft.Icons.PUBLIC,
        "color": CYAN,
    },
    "PHARMA": {
        "title": "Onboard Pharmacy",
        "icon": ft.Icons.MEDICATION,
        "color": YELLOW,
    },
    "RAD_ENV": {
        "title": "Radiation & Habitat",
        "icon": ft.Icons.SHIELD_MOON,
        "color": RED,
    },
    "GLOSSARY": {
        "title": "Glossary & Norms",
        "icon": ft.Icons.MENU_BOOK,
        "color": WHITE,
    },
}


def ensure_sample_markdown_files():
    """Creates the guidebook_data directory and ensures all starter .md files (including ICE) exist."""
    GUIDEBOOK_DIR.mkdir(parents=True, exist_ok=True)

    starter_files = {
        "00_ice_decompression.md": (
            "---\n"
            "title: Critical Decompression / Cabin Air Loss\n"
            "chapter: ICE\n"
            "summary: Emergency protocol for rapid cabin depressurization and suit seal verification.\n"
            "read_time: 1 min\n"
            "tags: ICE, Decompression, Air Loss, Oxygen, Vacuum\n"
            "---\n\n"
            "# Critical Decompression Protocol\n\n"
            "## Immediate Actions\n"
            "1. **DON OXYGEN MASK:** Pull emergency mask from the nearest bulkhead unit within 5 seconds.\n"
            "2. **VERIFY SUIT SEAL:** Check helmet locks and glove pressure integrity.\n"
            "3. **SOUND ALARM:** Broadcast **CODE RED** to mission control and adjacent modules.\n"
            "4. **EVACUATE AREA:** Seal hatch to the compromised sector if structural failure is confirmed.\n"
        ),
        "00_ice_cpr.md": (
            "---\n"
            "title: Cardiac Arrest / CPR Protocol\n"
            "chapter: ICE\n"
            "summary: Emergency response, chest compressions, and AED deployment in microgravity.\n"
            "read_time: 1 min\n"
            "tags: ICE, CPR, Cardiac Arrest, AED, Epinephrine\n"
            "---\n\n"
            "# Cardiac Arrest / CPR Protocol\n\n"
            "## Emergency Response\n"
            "1. **VERIFY UNRESPONSIVENESS:** Check carotid pulse and telemetry readout in **Monitoring** tab.\n"
            "2. **START CPR:** Begin chest compressions (100-120 bpm, 30 compressions / 2 breaths).\n"
            "3. **AED DEPLOYMENT:** Retrieve automated external defibrillator from Sector A locker.\n"
            "4. **EPINEPHRINE:** Prepare 1mg IV injection according to medical payload guidelines.\n"
        ),
        "00_ice_anaphylaxis.md": (
            "---\n"
            "title: Anaphylactic Shock / Severe Allergy\n"
            "chapter: ICE\n"
            "summary: Immediate epinephrine auto-injector administration and airway management.\n"
            "read_time: 1 min\n"
            "tags: ICE, Anaphylaxis, Allergy, EpiPen, Airway\n"
            "---\n\n"
            "# Anaphylactic Shock Protocol\n\n"
            "## Immediate Actions\n"
            "1. **ADMINISTER EPINEPHRINE:** Use auto-injector (EpiPen 0.3mg) into the lateral thigh muscle.\n"
            "2. **AIRWAY MANAGEMENT:** Ensure clear airway, administer high-flow oxygen.\n"
            "3. **MONITOR VITALS:** Watch SpO2 and blood pressure closely in telemetry monitor.\n"
        ),
        "00_ice_trauma.md": (
            "---\n"
            "title: Severe Trauma / Hemorrhage Control\n"
            "chapter: ICE\n"
            "summary: Tourniquet application and hemostatic gauze packing for severe bleeding.\n"
            "read_time: 1 min\n"
            "tags: ICE, Trauma, Bleeding, Hemorrhage, Tourniquet\n"
            "---\n\n"
            "# Severe Trauma & Hemorrhage Protocol\n\n"
            "## Action Plan\n"
            "1. **LOCATE BLEEDING:** Identify primary hemorrhage site.\n"
            "2. **TOURNIQUET APPLICATION:** Apply windlass tourniquet proximal to the wound (high and tight on limb).\n"
            "3. **HEMOSTATIC GAUZE:** Pack deep wounds with Celox/QuikClot gauze and apply direct pressure for 3 minutes.\n"
        ),
        "01_ecg_exam.md": (
            "---\n"
            "title: 3-Lead ECG Procedure in Microgravity\n"
            "chapter: EXAMS\n"
            "summary: Step-by-step electrode placement and motion artifact reduction.\n"
            "read_time: 3 min\n"
            "tags: ECG, Cardiology, Electrodes\n"
            "---\n\n"
            "# 3-Lead ECG Procedure in Microgravity\n\n"
            "## Required Equipment\n"
            "* Telemetry unit **BioMonitor-X**\n"
            "* 3 disposable gel electrodes\n"
            "* 70% isopropyl alcohol swabs\n\n"
            "## Step-by-Step Instructions\n"
            "1. **Skin Prep:** Clean the chest sites with an alcohol swab and let dry for 30 seconds.\n"
            "2. **Electrode Placement:**\n"
            "   * **Red (RA):** Right infraclavicular fossa.\n"
            "   * **Yellow (LA):** Left infraclavicular fossa.\n"
            "   * **Green (LL):** Left lower costal margin.\n"
            "3. **Stabilization:** Have the astronaut hold a handrail and relax shoulder muscles.\n"
        ),
        "02_spo2_calibration.md": (
            "---\n"
            "title: SpO2 Measurement & Sensor Calibration\n"
            "chapter: EXAMS\n"
            "summary: How to properly measure blood oxygen saturation and avoid cold-hand errors.\n"
            "read_time: 2 min\n"
            "tags: SpO2, Respiration, Hypoxia\n"
            "---\n\n"
            "# SpO2 Measurement & Sensor Calibration\n\n"
            "## Reference Ranges\n"
            "* **95% - 100%:** Normal\n"
            "* **91% - 94%:** Warning (check cabin gas mix and repeat measurement)\n"
            "* **Below 90%:** Critical Alert (initiate oxygen protocol in ICE chapter)\n\n"
            "## Procedure\n"
            "1. Warm up the hand before placing the optical clip.\n"
            "2. Place the sensor on the index or middle finger.\n"
            "3. Shield the sensor from direct cabin lighting.\n"
        ),
        "03_space_adaptation.md": (
            "---\n"
            "title: Space Adaptation Syndrome (SAS)\n"
            "chapter: SPACE_MED\n"
            "summary: Managing vestibular disorientation, fluid shifts, and motion sickness.\n"
            "read_time: 4 min\n"
            "tags: Vestibular, Fluid Shift, Microgravity\n"
            "---\n\n"
            "# Space Adaptation Syndrome (SAS)\n\n"
            "## Overview\n"
            "Caused by sensory conflict between the visual system and the vestibular apparatus in weightlessness.\n\n"
            "## Countermeasures\n"
            "1. Avoid rapid head movements during the first 72 hours of flight.\n"
            "2. Maintain visual orientation cues inside the module.\n"
            "3. Keep hydration above **2.0 L/day**.\n"
        ),
        "04_radiation_shelter.md": (
            "---\n"
            "title: Solar Particle Event (SPE) Shelter Protocol\n"
            "chapter: RAD_ENV\n"
            "summary: Dosimeter verification and emergency shielding actions during solar storms.\n"
            "read_time: 3 min\n"
            "tags: Radiation, Dosimeter, Shielding\n"
            "---\n\n"
            "# Solar Particle Event (SPE) Shelter Protocol\n\n"
            "## Action Checklist\n"
            "1. Verify real-time dosimeter rate in the **Monitoring** tab.\n"
            "2. Relocate crew to the central shielded zone (surrounded by water storage bags).\n"
            "3. Avoid viewport areas and thin hull sections until the alert clears.\n"
        ),
        "05_medical_glossary.md": (
            "---\n"
            "title: System Medical Glossary\n"
            "chapter: GLOSSARY\n"
            "summary: Core definitions of telemetry metrics and diagnostic abbreviations.\n"
            "read_time: 2 min\n"
            "tags: BPM, SpO2, ECG, Actigraphy, Dosimeter\n"
            "---\n\n"
            "# System Medical Glossary\n\n"
            "* **BPM (Beats Per Minute):** Heart rate frequency. Normal resting range: **60-100 BPM**.\n"
            "* **SpO2:** Estimated arterial blood oxygen saturation.\n"
            "* **ECG:** Electrocardiogram recording cardiac electrical activity (P-QRS-T waves).\n"
            "* **Actigraphy:** Non-invasive monitoring of rest and activity cycles.\n"
            "* **Dosimeter:** Device measuring ionizing radiation exposure rate (µSv/h).\n"
        ),
    }

    for filename, file_content in starter_files.items():
        file_path = GUIDEBOOK_DIR / filename
        if not file_path.exists():
            file_path.write_text(file_content, encoding="utf-8")


def parse_markdown_file(md_path: Path):
    """Parses a Markdown file with optional YAML-like frontmatter metadata."""
    raw_text = md_path.read_text(encoding="utf-8")
    meta = {
        "id": md_path.stem,
        "title": md_path.stem.replace("_", " ").title(),
        "chapter": "EXAMS",
        "summary": "Local procedure document.",
        "read_time": "2 min",
        "tags": [],
    }
    body = raw_text

    if raw_text.startswith("---"):
        parts = raw_text.split("---", 2)
        if len(parts) == 3:
            header_lines = parts[1].strip().splitlines()
            body = parts[2].strip()
            for line in header_lines:
                if ":" in line:
                    k, v = line.split(":", 1)
                    key = k.strip().lower()
                    val = v.strip()
                    if key == "tags":
                        meta["tags"] = [t.strip() for t in val.split(",") if t.strip()]
                    elif key in meta:
                        meta[key] = val

    if meta["chapter"] not in CHAPTERS or meta["chapter"] == "ALL":
        meta["chapter"] = "EXAMS"

    meta["content"] = body
    meta["filename"] = md_path.name
    return meta


def load_articles_from_disk():
    """Loads all .md articles from guidebook_data/ directory."""
    ensure_sample_markdown_files()
    articles = []
    for md_path in sorted(GUIDEBOOK_DIR.glob("*.md")):
        try:
            articles.append(parse_markdown_file(md_path))
        except OSError:
            pass
    return articles


def build_guidebook_screen(state=None, page=None):
    articles = load_articles_from_disk()

    def calc_box_height():
        win_h = (page.window.height if page and page.window.height else 900)
        # Leaves safe space for window title bar, app header, chapter bar, and bottom NavigationBar
        return max(360, int(win_h - 365))

    box_height = calc_box_height()

    gb_state = {
        "chapters_open": True,
        "chapter": "ALL",
        "search": "",
        "search_open": False,
        "selected_article": articles[0] if articles else None,
    }

    chapters_row = ft.Row(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)
    top_bar_switcher = ft.AnimatedSwitcher(
        content=ft.Container(),
        duration=200,
        reverse_duration=150,
        transition=ft.AnimatedSwitcherTransition.FADE,
    )

    articles_list_col = ft.Column(
        spacing=10,
        scroll=ft.ScrollMode.AUTO,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        expand=True,
    )
    article_reader_container = ft.Container(expand=8)
    results_counter = txt("", 12, GRAY)

    search_field = ft.TextField(
        hint_text="Search procedures, tags, or symptoms (e.g. decompression, CPR, ECG, SpO2)...",
        prefix_icon=ft.Icons.SEARCH,
        bgcolor=CARD,
        border_color=CYAN,
        focused_border_color=CYAN,
        border_radius=12,
        height=42,
        content_padding=ft.Padding.symmetric(horizontal=12, vertical=6),
        expand=True,
    )

    def get_filtered_articles():
        query = gb_state["search"]
        chapter = gb_state["chapter"]
        filtered = []
        for art in articles:
            if chapter != "ALL" and art["chapter"] != chapter:
                continue
            if query:
                searchable = " ".join([
                    art["title"],
                    art["summary"],
                    art["content"],
                    " ".join(art.get("tags", [])),
                ]).lower()
                if query not in searchable:
                    continue
            filtered.append(art)
        return filtered

    def refresh_ui():
        nonlocal box_height
        box_height = calc_box_height()
        left_articles_box.height = box_height
        render_top_bar()
        render_articles_list()
        render_reader()
        if page is not None:
            page.update()

    def select_chapter(chapter_key):
        gb_state["chapter"] = chapter_key
        filtered = get_filtered_articles()
        if filtered and gb_state["selected_article"] not in filtered:
            gb_state["selected_article"] = filtered[0]
        elif not filtered:
            gb_state["selected_article"] = None
        refresh_ui()

    def select_article(article):
        gb_state["selected_article"] = article
        refresh_ui()

    def on_search_change(e):
        gb_state["search"] = (e.control.value or "").strip().lower()
        filtered = get_filtered_articles()
        gb_state["selected_article"] = filtered[0] if filtered else None
        render_articles_list()
        render_reader()
        if page is not None:
            page.update()

    search_field.on_change = on_search_change

    def open_search(e):
        gb_state["search_open"] = True
        refresh_ui()

    def close_search(e):
        gb_state["search_open"] = False
        gb_state["search"] = ""
        search_field.value = ""
        filtered = get_filtered_articles()
        if filtered and gb_state["selected_article"] not in filtered:
            gb_state["selected_article"] = filtered[0]
        refresh_ui()

    def reload_disk_files(e):
        nonlocal articles
        articles = load_articles_from_disk()
        filtered = get_filtered_articles()
        gb_state["selected_article"] = filtered[0] if filtered else None
        refresh_ui()

    def toggle_chapters(e):
        gb_state["chapters_open"] = not gb_state["chapters_open"]
        refresh_ui()

    def render_top_bar():
        chapters_row.controls.clear()
        for key, ch in CHAPTERS.items():
            active = (gb_state["chapter"] == key)
            accent = ch["color"]
            count = sum(1 for a in articles if key == "ALL" or a["chapter"] == key)
            chapters_row.controls.append(
                ft.Container(
                    bgcolor="#3A1414" if (active and key == "ICE") else ("#234757" if active else CARD),
                    border=ft.Border.all(2 if active else 1, accent if active else BORDER),
                    border_radius=12,
                    padding=ft.Padding.symmetric(horizontal=13, vertical=7),
                    ink=True,
                    on_click=lambda e, k=key: select_chapter(k),
                    content=ft.Row(spacing=8, controls=[
                        ft.Icon(ch["icon"], size=17, color=accent),
                        txt(ch["title"], 13, WHITE if active else GRAY, active),
                        ft.Container(
                            bgcolor=PANEL,
                            border_radius=8,
                            padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                            content=txt(str(count), 11, accent, True),
                        ),
                    ]),
                )
            )

        search_toggle_btn = ft.Container(
            bgcolor="#234757" if gb_state["search"] else CARD,
            border=ft.Border.all(1, CYAN if gb_state["search"] else BORDER),
            border_radius=12,
            padding=ft.Padding.symmetric(horizontal=12, vertical=8),
            ink=True,
            tooltip="Open search",
            on_click=open_search,
            content=ft.Row(spacing=6, controls=[
                ft.Icon(ft.Icons.SEARCH, size=19, color=CYAN),
            ]),
        )

        close_search_btn = ft.Container(
            bgcolor=CARD,
            border=ft.Border.all(1, RED),
            border_radius=12,
            padding=ft.Padding.symmetric(horizontal=12, vertical=8),
            ink=True,
            tooltip="Close search",
            on_click=close_search,
            content=ft.Row(spacing=6, controls=[
                ft.Icon(ft.Icons.CLOSE, size=18, color=RED),
                txt("Cancel", 12, WHITE, True),
            ]),
        )

        if gb_state["search_open"]:
            top_bar_switcher.content = ft.Row(
                key="search_bar_mode",
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[search_field, close_search_btn],
            )
        else:
            top_bar_switcher.content = ft.Row(
                key="chapters_bar_mode",
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[search_toggle_btn,chapters_row],
            )

    def render_articles_list():
        articles_list_col.controls.clear()
        filtered = get_filtered_articles()
        results_counter.value = f"{len(filtered)} articles"

        if not filtered:
            articles_list_col.controls.append(
                ft.Container(
                    padding=16,
                    bgcolor=CARD,
                    border_radius=12,
                    content=txt("No matching Markdown articles found.", 13, YELLOW),
                )
            )
            return

        for art in filtered:
            is_selected = (
                gb_state["selected_article"] is not None
                and gb_state["selected_article"]["id"] == art["id"]
            )
            is_ice = (art["chapter"] == "ICE")
            ch_info = CHAPTERS.get(art["chapter"], CHAPTERS["ALL"])
            accent = ch_info["color"]

            articles_list_col.controls.append(
                ft.Container(
                    bgcolor="#3A1414" if (is_selected and is_ice) else ("#214659" if is_selected else CARD),
                    border=ft.Border.all(
                        2 if is_selected else 1,
                        (RED if is_ice else CYAN) if is_selected else BORDER,
                    ),
                    border_radius=12,
                    padding=12,
                    ink=True,
                    on_click=lambda e, a=art: select_article(a),
                    content=ft.Column(spacing=6, controls=[
                        ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                            ft.Row(spacing=6, controls=[
                                ft.Icon(ch_info["icon"], size=15, color=accent),
                                txt(ch_info["title"], 11, accent, True),
                            ]),
                            txt(f'⏱ {art.get("read_time", "2 min")}', 11, GRAY),
                        ]),
                        txt(art["title"], 15, WHITE, True),
                        txt(art["summary"], 12, GRAY),
                    ]),
                )
            )

    def render_reader():
        art = gb_state["selected_article"]
        if not art:
            article_reader_container.content = ft.Container(
                height=box_height,
                bgcolor=PANEL,
                border=ft.Border.all(1, BORDER),
                border_radius=16,
                padding=20,
                content=txt("Select an article from the list to view its content.", 15, GRAY),
            )
            return

        is_ice = (art["chapter"] == "ICE")
        ch_info = CHAPTERS.get(art["chapter"], CHAPTERS["ALL"])
        tag_color = RED if is_ice else CYAN

        tags_row = ft.Row(
            wrap=True,
            spacing=6,
            controls=[
                ft.Container(
                    bgcolor=CARD,
                    border=ft.Border.all(1, BORDER),
                    border_radius=6,
                    padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                    content=txt(f"#{tag}", 11, tag_color),
                )
                for tag in art.get("tags", [])
            ],
        )

        article_reader_container.content = ft.Container(
            height=box_height,
            bgcolor=PANEL,
            border=ft.Border.all(2 if is_ice else 1, RED if is_ice else BORDER),
            border_radius=16,
            padding=18,
            content=ft.Column(
                spacing=10,
                expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                controls=[
                    ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                        ft.Row(spacing=8, controls=[
                            ft.Icon(ch_info["icon"], color=ch_info["color"], size=20),
                            txt(ch_info["title"].upper(), 12, ch_info["color"], True),
                        ]),
                        txt(f'Source: guidebook_data/{art.get("filename", "")}', 11, GRAY),
                    ]),
                    tags_row,
                    ft.Divider(color=BORDER, height=8),
                    ft.Column(
                        expand=True,
                        scroll=ft.ScrollMode.AUTO,
                        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                        controls=article_controls(art["content"],GUIDEBOOK_DIR),
                    ),
                ],
            ),
        )

    reload_button = ft.Container(
        bgcolor=CARD,
        border=ft.Border.all(1, BORDER),
        border_radius=12,
        padding=ft.Padding.symmetric(horizontal=12, vertical=7),
        ink=True,
        on_click=reload_disk_files,
        content=ft.Row(spacing=6, controls=[
            ft.Icon(ft.Icons.REFRESH, size=17, color=CYAN),
            txt("Reload .md", 12, WHITE, True),
        ]),
    )

    left_articles_box = ft.Container(
        expand=4,
        height=box_height,
        bgcolor=PANEL,
        border=ft.Border.all(1, BORDER),
        border_radius=16,
        padding=14,
        content=ft.Column(
            spacing=10,
            expand=True,
            controls=[
                ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                    txt("Articles", 17, WHITE, True),
                    results_counter,
                ]),
                ft.Divider(color=BORDER, height=4),
                articles_list_col,
            ],
        ),
    )

    render_top_bar()
    render_articles_list()
    render_reader()

    return ft.Column(
        spacing=10,
        controls=[
            ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                ft.Row(spacing=10, controls=[
                    txt("Guidebook", 21, WHITE, True),
                    txt("• Knowledge Base & ICE", 12, GRAY),
                ]),
                reload_button,
            ]),
            top_bar_switcher,
            build_guide_assistant(lambda:articles,select_article,page),
            ft.Row(
                spacing=14,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    left_articles_box,
                    article_reader_container,
                ],
            ),
        ],
    )
from __future__ import annotations

from pathlib import Path
import re
import shutil
import sys

ROOT = Path.cwd()
APP = ROOT / "app.py"
TEMPLATE = ROOT / "templates" / "index.html"
CSS = ROOT / "static" / "style.css"


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


def backup(path: Path) -> None:
    backup_path = path.with_name(path.name + ".before_hero_ui_fix")
    if not backup_path.exists():
        shutil.copy2(path, backup_path)
        print(f"Backup created: {backup_path.relative_to(ROOT)}")


def patch_template() -> None:
    text = TEMPLATE.read_text(encoding="utf-8")
    if 'id="hero-search-toggle"' in text:
        print("Template already has the collapsible Search by Hero control; skipped.")
        return

    old = '''  <section class="hero-explore-section" id="explore-heroes">
    <div class="hero-explore-heading"><div><p class="kicker">THE STARS OF TELUGU CINEMA</p><h2>Explore by <em>hero.</em></h2><p>Choose an actor to see the films led by them in our collection.</p></div><span class="hero-explore-mark">నటుడు<br><b>✳</b></span></div>
    <div class="hero-chip-list" role="group" aria-label="Filter films by lead actor">
      <button type="button" class="hero-chip is-active" data-hero-filter="all">All heroes</button>
      {% for hero in heroes %}<button type="button" class="hero-chip" data-hero-filter="{{ hero|lower }}">{{ hero }}</button>{% endfor %}
    </div>
    <p class="hero-filter-note" id="hero-filter-note" aria-live="polite">Showing films from every hero. Select a name to narrow the collection.</p>
  </section>'''

    new = '''  <section class="hero-explore-section" id="explore-heroes">
    <div class="hero-explore-heading"><div><p class="kicker">THE STARS OF TELUGU CINEMA</p><h2>Find films by <em>hero.</em></h2><p>Open the hero search to browse the actors in this collection.</p></div><span class="hero-explore-mark">నటుడు<br><b>✳</b></span></div>
    <button type="button" class="hero-search-toggle" id="hero-search-toggle" aria-expanded="false" aria-controls="hero-chip-list">
      <span>Search by Hero</span><span class="hero-search-toggle-icon" aria-hidden="true">＋</span>
    </button>
    <div class="hero-chip-list" id="hero-chip-list" role="group" aria-label="Filter films by lead actor" hidden>
      <button type="button" class="hero-chip is-active" data-hero-filter="all">All heroes</button>
      {% for hero in heroes %}<button type="button" class="hero-chip" data-hero-filter="{{ hero|lower }}">{{ hero }}</button>{% endfor %}
    </div>
    <p class="hero-filter-note" id="hero-filter-note" aria-live="polite">Select “Search by Hero” to open the actor list.</p>
  </section>'''

    if old not in text:
        fail("Could not find the expected hero section in templates/index.html. No files were changed after backup.")

    text = text.replace(old, new, 1)
    js_anchor = "  const heroNote = document.querySelector('#hero-filter-note');\n"
    js_add = '''  const heroNote = document.querySelector('#hero-filter-note');
  const heroSearchToggle = document.querySelector('#hero-search-toggle');
  const heroChipList = document.querySelector('#hero-chip-list');
  heroSearchToggle?.addEventListener('click', () => {
    const isOpen = heroSearchToggle.getAttribute('aria-expanded') === 'true';
    heroSearchToggle.setAttribute('aria-expanded', String(!isOpen));
    if (heroChipList) heroChipList.hidden = isOpen;
    const icon = heroSearchToggle.querySelector('.hero-search-toggle-icon');
    if (icon) icon.textContent = isOpen ? '＋' : '−';
    if (!isOpen) heroChipList?.querySelector('.hero-chip')?.focus({ preventScroll: true });
  });
'''
    if js_anchor not in text:
        fail("Could not find the hero JavaScript insertion point in templates/index.html.")
    text = text.replace(js_anchor, js_add, 1)
    backup(TEMPLATE)
    TEMPLATE.write_text(text, encoding="utf-8")
    print("Updated: templates/index.html")


def patch_css() -> None:
    text = CSS.read_text(encoding="utf-8")
    marker = "/* Search-by-hero disclosure: keep actor names collapsed until requested. */"
    if marker in text:
        print("Hero disclosure styles already exist; skipped.")
        return
    addition = '''

/* Search-by-hero disclosure: keep actor names collapsed until requested. */
.hero-search-toggle {
  margin-top: 24px;
  min-width: 190px;
  display: inline-flex;
  align-items: center;
  justify-content: space-between;
  gap: 28px;
  padding: 13px 17px;
  color: #fff8ed;
  background: var(--ink);
  border: 1px solid var(--ink);
  border-radius: 3px;
  font: 700 11px 'DM Sans', sans-serif;
  letter-spacing: .25px;
  cursor: pointer;
  transition: transform .18s ease, background .18s ease;
}
.hero-search-toggle:hover { background: #245454; transform: translateY(-1px); }
.hero-search-toggle:focus-visible { outline: 3px solid var(--tomato); outline-offset: 3px; }
.hero-search-toggle-icon { color: var(--sun); font-size: 18px; line-height: 1; }
#hero-chip-list[hidden] { display: none !important; }
#hero-chip-list:not([hidden]) { margin-top: 19px; }
'''
    backup(CSS)
    CSS.write_text(text + addition, encoding="utf-8")
    print("Updated: static/style.css")


def patch_app() -> None:
    text = APP.read_text(encoding="utf-8")
    if "def select_stage_movie(" in text:
        print("Stage-poster fallback already exists; skipped.")
        return

    anchor = "    by_slug = {slugify(title): recommender.get_movie(title) for title in recommender.index}\n"
    helper = '''    by_slug = {slugify(title): recommender.get_movie(title) for title in recommender.index}

    def select_stage_movie(hero_name, preferred_titles):
        """Pick a featured actor film whose poster is present in the local project."""
        movies = recommender.movies
        hero_values = movies["hero"].fillna("").astype(str).str.casefold()
        actor_rows = movies[hero_values.str.contains(re.escape(hero_name.casefold()), na=False)].copy()
        preferred_rows = actor_rows if not actor_rows.empty else movies

        def title_key(value):
            return re.sub(r"[^a-z0-9]+", "", str(value).casefold())

        def has_local_poster(row):
            raw = str(row.get("poster_url", "")).strip()
            if not raw or raw.casefold() in {"nan", "none"} or raw.startswith(("http://", "https://")):
                return False
            relative = raw.lstrip("/")
            if relative.startswith("static/"):
                poster_path = BASE_DIR / relative
            elif relative.startswith("posters/"):
                poster_path = BASE_DIR / "static" / relative
            else:
                poster_path = BASE_DIR / relative
            return poster_path.is_file()

        wanted = {title_key(title): title for title in preferred_titles}
        for _, row in preferred_rows.iterrows():
            if title_key(row["title"]) in wanted and has_local_poster(row):
                return recommender.movie_info(row)
        for _, row in preferred_rows.iterrows():
            if has_local_poster(row):
                return recommender.movie_info(row)
        return None
'''
    if anchor not in text:
        fail("Could not find the app.py stage selection insertion point.")
    text = text.replace(anchor, helper, 1)

    old_stage = '''            stage_movies={
                "ram_charan": recommender.get_movie("Rangasthalam"),
                "pawan_kalyan": recommender.get_movie("Jalsa"),
                "prabhas": recommender.get_movie("Baahubali 2 The Conclusion"),
            },'''
    new_stage = '''            stage_movies={
                "ram_charan": select_stage_movie("Ram Charan", ["Rangasthalam", "Magadheera", "RRR", "Dhruva", "Game Changer"]),
                "pawan_kalyan": select_stage_movie("Pawan Kalyan", ["Jalsa", "Tholi Prema", "Kushi", "Gabbar Singh"]),
                "prabhas": select_stage_movie("Prabhas", ["Baahubali 2: The Conclusion", "Bahubali 2: The Conclusion", "Baahubali: The Epic", "Salaar", "Mirchi", "Darling", "Saaho", "Kalki 2898-AD"]),
            },'''
    if old_stage not in text:
        fail("Could not find the expected stage_movies block in app.py. No stage change was applied.")
    text = text.replace(old_stage, new_stage, 1)
    backup(APP)
    APP.write_text(text, encoding="utf-8")
    print("Updated: app.py (featured posters now fall back to a matching actor film with an existing local poster)")


def main() -> None:
    required = [APP, TEMPLATE, CSS]
    missing = [str(p.relative_to(ROOT)) for p in required if not p.is_file()]
    if missing:
        fail("Run this script from your Mana-Movie project root. Missing: " + ", ".join(missing))

    print("Applying a UI-only patch. Movie CSV files and poster images will not be changed.")
    patch_template()
    patch_css()
    patch_app()
    print("\nDone. Backups with .before_hero_ui_fix suffix were saved beside the original files.")
    print("Restart Flask and test the homepage. No catalogue or poster data was modified.")


if __name__ == "__main__":
    main()

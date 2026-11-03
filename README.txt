MANA CINEMA — GABBAR SINGH HOMEPAGE POSTER FIX

This patch changes only the featured Pawan Kalyan poster on the homepage.
It makes the hero showcase select the local Gabbar Singh poster from:
static/posters/421-gabbar-singh.jpg

HOW TO APPLY
1. Stop Flask in the terminal with Ctrl+C.
2. In your project folder, make a backup copy of app.py (for example app.py.before_gabbar_fix).
3. Extract this ZIP into the project root (the folder containing app.py).
4. Allow app.py to be replaced. Do not replace your data or static folders.
5. Run: python app.py
6. Refresh Chrome with Ctrl+F5.

The patch assumes the 500-posters collection has already been extracted.

# patch_index.py
import re, shutil, os, sys

src = "index.html"
bak = "index.html.bak"
dst = "index_fixed.html"

if not os.path.exists(src):
    print("Couldn't find index.html in this folder. Put patch_index.py next to index.html and rerun.")
    sys.exit(1)

# backup
shutil.copyfile(src, bak)
print("Backup saved as", bak)

with open(src, "r", encoding="utf-8") as f:
    s = f.read()

# 1) Replace common insecure URL prefixes with https (safe)
s = s.replace("http://img.pokemondb.net", "https://img.pokemondb.net")
s = s.replace("http://play.pokemonshowdown.com", "https://play.pokemonshowdown.com")
s = s.replace("http://raw.githubusercontent.com", "https://raw.githubusercontent.com")
s = s.replace("http://pokeapi.co", "https://pokeapi.co")
s = s.replace("http://img.pokemon.com", "https://img.pokemon.com")

# 2) Wrap inline <script> blocks (those without src) in DOMContentLoaded.
#    If script already contains "DOMContentLoaded" or is empty, skip wrapping.
pattern = re.compile(r'(<script\b(?![^>]*\bsrc\b)[^>]*>)([\s\S]*?)(</script>)', re.IGNORECASE)
def wrap(m):
    open_tag, content, close_tag = m.group(1), m.group(2), m.group(3)
    # skip if already contains listener or is just whitespace
    if not content.strip() or "DOMContentLoaded" in content or "document.addEventListener" in content:
        return m.group(0)
    # wrap
    wrapped = open_tag + "\n// Wrapped by patch_index.py to wait for DOMContentLoaded\n" \
              "document.addEventListener('DOMContentLoaded', function(){\n" + content + "\n});\n" + close_tag
    return wrapped

new_s, count = pattern.subn(wrap, s)

with open(dst, "w", encoding="utf-8") as f:
    f.write(new_s)

print(f"Patched file written to {dst} (wrapped {count} inline script(s)).")
print("If everything looks good, replace your repo's index.html with index_fixed.html and redeploy.")

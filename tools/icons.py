"""Generate the AK monogram app icons in the site's lime-and-charcoal theme.

Usage: python3 tools/icons.py <site_dir>

Writes:
  icons/icon-192.png, icons/icon-512.png        full-bleed app icons
  icons/icon-maskable-512.png                   safe-zone version for Android adaptive icons
  icons/apple-touch-icon.png (180)              iPhone / iPad home screen
  icons/favicon-32.png, favicon.ico (16/32/48)  browser tabs
  icons/favicon.svg                             vector favicon (letters as paths, no font needed)
  tools/app-store/play-icon-512.png             Google Play listing icon
  tools/app-store/feature-graphic-1024x500.png  Google Play feature graphic
"""
import sys
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

SITE = Path(sys.argv[1])
FONT = Path(__file__).parent / "fonts" / "SpaceGrotesk.ttf"
CHAR = (25, 26, 35)       # #191A23
LIME = (185, 255, 102)    # #B9FF66
WHITE = (243, 243, 243)   # #F3F3F3
TEXT = "AK"


def font(size, weight="Bold"):
    f = ImageFont.truetype(str(FONT), size)
    f.set_variation_by_name(weight)
    return f


def monogram(size, scale=1.0, radius=0):
    """Charcoal square, lime 'AK', lime underline. scale<1 shrinks the mark (for maskable safe zone)."""
    ss = 4  # supersample for smooth edges
    S = size * ss
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if radius:
        d.rounded_rectangle([0, 0, S - 1, S - 1], radius=radius * ss, fill=CHAR + (255,))
    else:
        d.rectangle([0, 0, S, S], fill=CHAR + (255,))
    # letters: target width ~60% of the icon (times scale)
    target_w = S * 0.60 * scale
    fs = int(S * 0.5 * scale)
    f = font(fs)
    w = d.textlength(TEXT, font=f)
    fs = int(fs * target_w / w)
    f = font(fs)
    bbox = d.textbbox((0, 0), TEXT, font=f, anchor="ls")
    tw, th = bbox[2] - bbox[0], -bbox[1]
    bar_h = max(2, int(S * 0.034 * scale))
    gap = int(S * 0.06 * scale)
    block_h = th + gap + bar_h
    top = (S - block_h) / 2
    x = (S - tw) / 2 - bbox[0]
    baseline = top + th
    d.text((x, baseline), TEXT, font=f, fill=LIME + (255,), anchor="ls")
    bar_w = tw * 0.62
    bx = (S - bar_w) / 2
    by = baseline + gap
    d.rounded_rectangle([bx, by, bx + bar_w, by + bar_h], radius=bar_h / 2, fill=LIME + (255,))
    return img.resize((size, size), Image.LANCZOS)


def svg_favicon():
    tt = TTFont(str(FONT))
    # pick Bold instance from the variable font
    if "fvar" in tt:
        from fontTools.varLib import instancer
        wght = [a for a in tt["fvar"].axes if a.axisTag == "wght"][0]
        tt = instancer.instantiateVariableFont(tt, {"wght": min(700, wght.maxValue)})
    gs = tt.getGlyphSet()
    cmap = tt.getBestCmap()
    upm = tt["head"].unitsPerEm
    paths, x = [], 0
    for ch in TEXT:
        g = cmap[ord(ch)]
        pen = SVGPathPen(gs)
        gs[g].draw(pen)
        paths.append((x, pen.getCommands()))
        x += gs[g].width
    total_w = x
    cap = tt["OS/2"].sCapHeight or int(upm * 0.7)
    # fit letters to 60% of a 64-unit box
    s = 64 * 0.60 / total_w
    tw, th = total_w * s, cap * s
    bar_h, gap = 2.2, 3.8
    top = (64 - (th + gap + bar_h)) / 2
    ox = (64 - tw) / 2
    base = top + th
    g_el = "".join(
        f'<path transform="translate({ox + px * s:.2f} {base:.2f}) scale({s:.5f} {-s:.5f})" d="{cmd}"/>'
        for px, cmd in paths)
    bw = tw * 0.62
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
            f'<rect width="64" height="64" rx="14" fill="#191A23"/>'
            f'<g fill="#B9FF66">{g_el}</g>'
            f'<rect x="{(64 - bw) / 2:.2f}" y="{base + gap:.2f}" width="{bw:.2f}" height="{bar_h}" rx="{bar_h / 2}" fill="#B9FF66"/>'
            f'</svg>')


def feature_graphic():
    W, H = 1024, 500
    ss = 2
    img = Image.new("RGB", (W * ss, H * ss), CHAR)
    d = ImageDraw.Draw(img)
    icon = monogram(300 * ss, radius=66)
    img.paste(icon, (90 * ss, 100 * ss), icon)
    x = 450 * ss
    d.text((x, 170 * ss), "Custos", font=font(64 * ss), fill=WHITE, anchor="ls")
    d.text((x, 228 * ss), "by Adv. Ashwani Kumar", font=font(40 * ss, "Medium"), fill=LIME, anchor="ls")
    for i, line in enumerate(["Plain-language guides, case tracker", "and commentary on Indian tech law"]):
        d.text((x, (300 + i * 44) * ss), line, font=font(30 * ss, "Regular"), fill=WHITE, anchor="ls")
    return img.resize((W, H), Image.LANCZOS)


icons = SITE / "icons"
icons.mkdir(exist_ok=True)
store = Path(__file__).parent / "app-store"
store.mkdir(exist_ok=True)

monogram(512).convert("RGB").save(icons / "icon-512.png", optimize=True)
monogram(192).convert("RGB").save(icons / "icon-192.png", optimize=True)
monogram(512, scale=0.72).convert("RGB").save(icons / "icon-maskable-512.png", optimize=True)
monogram(180).convert("RGB").save(icons / "apple-touch-icon.png", optimize=True)
monogram(32, radius=7).save(icons / "favicon-32.png", optimize=True)
fav = monogram(256, radius=56)
fav.save(SITE / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
(icons / "favicon.svg").write_text(svg_favicon(), encoding="utf-8")
monogram(512).save(store / "play-icon-512.png", optimize=True)
feature_graphic().save(store / "feature-graphic-1024x500.png", optimize=True)
print("icons written")

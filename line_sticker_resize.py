#!/usr/bin/env python3
"""
Batch convert images to LINE sticker size 370x320 PNG with transparent background.
- Keeps aspect ratio (no stretching). Pads with transparency to exactly 370x320.
- Optional: make solid background transparent with soft edges (auto-detect from corners or specify a hex color).
Usage:
  python line_sticker_resize.py /path/to/input --output out_dir --make-transparent --tolerance 18
  python line_sticker_resize.py /path/to/input --bg-color #FFFFFF --make-transparent
"""
import argparse
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image

TARGET_W, TARGET_H = 370, 320
VALID_EXTS = {'.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif'}

def parse_hex_color(s: str) -> Tuple[int, int, int]:
    s = s.strip()
    if s.startswith('#'):
        s = s[1:]
    if len(s) == 3:
        s = ''.join(ch*2 for ch in s)
    if len(s) != 6:
        raise ValueError("Hex color must be 3 or 6 hex digits, e.g. #fff or #ffffff")
    r = int(s[0:2], 16)
    g = int(s[2:4], 16)
    b = int(s[4:6], 16)
    return (r, g, b)

def color_distance_sq(a: Tuple[int,int,int], b: Tuple[int,int,int]) -> int:
    return (a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2

def detect_bg_color(im: Image.Image) -> Tuple[int,int,int]:
    """Pick a representative background color from the 4 corners (RGB)."""
    px = im.convert('RGBA')
    w, h = px.size
    corners = [(0,0), (w-1,0), (0,h-1), (w-1,h-1)]
    colors = []
    for x,y in corners:
        r,g,b,a = px.getpixel((x,y))
        colors.append((r,g,b))
    # Use the most frequent; if tie, average
    from collections import Counter
    cnt = Counter(colors).most_common()
    if not cnt:
        return (255,255,255)
    max_freq = cnt[0][1]
    candidates = [c for c,f in cnt if f == max_freq]
    if len(candidates) == 1:
        return candidates[0]
    # average candidates
    r = sum(c[0] for c in candidates)//len(candidates)
    g = sum(c[1] for c in candidates)//len(candidates)
    b = sum(c[2] for c in candidates)//len(candidates)
    return (r,g,b)

def make_bg_transparent(im: Image.Image, bg: Tuple[int,int,int], tolerance: int) -> Image.Image:
    """Replace pixels close to bg color with graduated alpha, creating soft edges."""
    im = im.convert('RGBA')
    w, h = im.size
    px = im.load()
    tol_sq = tolerance * tolerance * 3  # simple sphere in RGB space
    
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            
            # Calculate distance from background color
            dist_sq = color_distance_sq((r, g, b), bg)
            
            if dist_sq <= tol_sq:
                # Create soft transition: closer to bg = more transparent
                # Use square root for more natural falloff
                distance_ratio = (dist_sq / tol_sq) ** 0.5
                # Smooth transition from 0 (fully transparent) to original alpha
                new_alpha = int(a * distance_ratio)
                px[x, y] = (r, g, b, new_alpha)
    
    return im

def resize_and_pad(im: Image.Image, target_w: int, target_h: int) -> Image.Image:
    im = im.convert('RGBA')
    w, h = im.size
    if w == 0 or h == 0:
        raise ValueError("Image has invalid dimensions")
    scale = min(target_w / w, target_h / h)
    new_w = max(1, int(round(w * scale)))
    new_h = max(1, int(round(h * scale)))
    resized = im.resize((new_w, new_h), Image.LANCZOS)
    canvas = Image.new('RGBA', (target_w, target_h), (0,0,0,0))
    x = (target_w - new_w) // 2
    y = (target_h - new_h) // 2
    canvas.paste(resized, (x, y), resized)
    return canvas

def process_image(src_path: Path, dst_path: Path, make_transparent: bool, bg_color: Optional[Tuple[int,int,int]], tolerance: int):
    with Image.open(src_path) as im:
        # Optional background transparency
        if make_transparent:
            bg = bg_color if bg_color is not None else detect_bg_color(im)
            im = make_bg_transparent(im, bg, tolerance)
        # Resize + pad to exactly 370x320
        out_im = resize_and_pad(im, TARGET_W, TARGET_H)
        # Save as PNG
        out_im.save(dst_path.with_suffix('.png'), format='PNG')

def main():
    ap = argparse.ArgumentParser(description="Batch convert images to 370x320 PNG with transparency.")
    ap.add_argument("input", help="Input folder or a single image file")
    ap.add_argument("--output", "-o", help="Output folder (will be created if missing)", default="output_370x320")
    ap.add_argument("--make-transparent", action="store_true", help="Attempt to remove a solid background with soft edges")
    ap.add_argument("--bg-color", type=str, default=None, help="Background color to remove (hex, e.g. #FFFFFF). If omitted, auto-detect from corners.")
    ap.add_argument("--tolerance", type=int, default=18, help="Color tolerance for soft background removal (0-64 is common).")
    args = ap.parse_args()

    in_path = Path(args.input)
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    bg_tuple: Optional[Tuple[int,int,int]] = None
    if args.bg_color:
        bg_tuple = parse_hex_color(args.bg_color)

    files = []
    if in_path.is_file():
        files = [in_path]
    elif in_path.is_dir():
        for p in in_path.rglob("*"):
            if p.suffix.lower() in VALID_EXTS and p.is_file():
                files.append(p)
    else:
        raise SystemExit("Input path does not exist.")

    if not files:
        raise SystemExit("No images found in the input path.")

    count = 0
    for f in files:
        rel = f.name if in_path.is_file() else f.relative_to(in_path).as_posix()
        dst = out_dir / Path(rel).name
        try:
            process_image(f, dst, args.make_transparent, bg_tuple, args.tolerance)
            count += 1
            print(f"✅ Converted: {f} -> {dst.with_suffix('.png')}")
        except Exception as e:
            print(f"⚠️ Skipped {f}: {e}")

    print(f"\nDone. {count} image(s) converted to {out_dir.resolve()}")

if __name__ == "__main__":
    main()

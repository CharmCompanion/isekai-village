import math
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

def generate_element_texture(element_name, output_dir="Content/SpellCraft/Textures", size=2048):
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"T_MagicCircle_{element_name}.png")
    
    cx, cy = size / 2.0, size / 2.0
    
    # Radii
    r_outer_border = size * 0.425  # Outer limit
    r1 = size * 0.395              # Outer primary ring
    r2 = size * 0.330              # Inner perimeter ring (Outer ZIG-ZAG band between r1 & r2)
    r3 = size * 0.235              # Inscribed middle circle
    r4 = size * 0.135              # Center Core Region
    
    r_img = Image.new("L", (size, size), 0)
    r_draw = ImageDraw.Draw(r_img)
    
    b_img = Image.new("L", (size, size), 0)
    b_draw = ImageDraw.Draw(b_img)
    
    def draw_poly_loop(d, pts, width=22):
        for i in range(len(pts)):
            d.line([pts[i], pts[(i + 1) % len(pts)]], fill=255, width=width)
            
    def draw_star_chords(d, pts, skip_step=2, width=20):
        n = len(pts)
        idx = 0
        for _ in range(n):
            next_idx = (idx + skip_step) % n
            d.line([pts[idx], pts[next_idx]], fill=255, width=width)
            idx = next_idx

    def get_poly_pts(radius, n_count, offset_deg=0.0):
        pts = []
        for i in range(n_count):
            angle = math.radians(offset_deg + (i * 360.0 / n_count) - 90.0)
            pts.append((cx + math.cos(angle) * radius, cy + math.sin(angle) * radius))
        return pts

    # --- 1. Volumetric God-Rays (Channel B) ---
    num_rays = 48
    for i in range(num_rays):
        angle = math.radians(i * (360.0 / num_rays))
        ray_len = (size * 0.040) if (i % 2 == 0) else (size * 0.075)
        if i % 4 == 0:
            ray_len = size * 0.115
            
        p1 = (cx + math.cos(angle) * (r_outer_border + 2), cy + math.sin(angle) * (r_outer_border + 2))
        p2 = (cx + math.cos(angle) * (r_outer_border + ray_len), cy + math.sin(angle) * (r_outer_border + ray_len))
        b_draw.line([p1, p2], fill=255, width=14 if i % 2 == 0 else 8)

    # --- 2. Doubled Thickness Neon Vector Lines (Channel R) ---
    # Concentric Outer Borders (26px thick)
    r_draw.ellipse([cx - r_outer_border, cy - r_outer_border, cx + r_outer_border, cy + r_outer_border], outline=255, width=26)
    r_draw.ellipse([cx - r1, cy - r1, cx + r1, cy + r1], outline=255, width=26)
    r_draw.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], outline=255, width=26)

    # ZIG-ZAG CHORD BAND AROUND OUTER PERIMETER (Between r1 and r2)
    num_zig_zags = 24
    zig_pts = []
    for z in range(num_zig_zags):
        za = math.radians(z * (360.0 / num_zig_zags) - 90.0)
        zr = r1 if (z % 2 == 0) else r2
        zig_pts.append((cx + math.cos(za) * zr, cy + math.sin(za) * zr))
    draw_poly_loop(r_draw, zig_pts, width=18)

    # 6 Delta Triangles ▲ and Runic Text
    delta_r = (r_outer_border + r1) * 0.5
    delta_size = size * 0.018
    for i in range(6):
        d_angle = math.radians(i * 60.0 - 90.0)
        dcx = cx + math.cos(d_angle) * delta_r
        dcy = cy + math.sin(d_angle) * delta_r
        t_pts = []
        for t in range(3):
            ta = d_angle + math.radians(t * 120.0)
            t_pts.append((dcx + math.cos(ta) * delta_size, dcy + math.sin(ta) * delta_size))
        r_draw.polygon(t_pts, fill=255)

    font_size = int(size * 0.034)
    font = None
    try:
        font = ImageFont.truetype("Content/SpellCraft/SpellRunes-Regular.otf", font_size)
    except:
        try:
            font = ImageFont.truetype("arialbd.ttf", font_size)
        except:
            font = ImageFont.load_default()
            
    runic_words = ["IGNIS", "TERRA", "VENTUS", "AQUA", "FULGUR", "LUX"]
    for i in range(6):
        sector_center_angle = math.radians(i * 60.0 + 30.0 - 90.0)
        word = runic_words[i]
        for char_idx, char in enumerate(word):
            char_offset = (char_idx - (len(word) - 1) / 2.0) * math.radians(4.8)
            char_angle = sector_center_angle + char_offset
            ch_x = cx + math.cos(char_angle) * delta_r
            ch_y = cy + math.sin(char_angle) * delta_r
            r_draw.text((ch_x, ch_y), char, fill=255, font=font, anchor="mm")

    # Inscribed Middle Circle (Thick 22px)
    r_draw.ellipse([cx - r3, cy - r3, cx + r3, cy + r3], outline=255, width=22)

    # 4 Cardinal Orbital Satellites
    sat_r = size * 0.082
    sat_centers = [(cx, cy - r2), (cx + r2, cy), (cx, cy + r2), (cx - r2, cy)]
    for s_idx, (scx, scy) in enumerate(sat_centers):
        r_draw.ellipse([scx - sat_r, scy - sat_r, scx + sat_r, scy + sat_r], outline=255, width=18)
        if s_idx == 0:
            tri = [(scx, scy - sat_r * 0.52), (scx + sat_r * 0.46, scy + sat_r * 0.38), (scx - sat_r * 0.46, scy + sat_r * 0.38)]
            r_draw.polygon(tri, outline=255, width=8)
            for tp in tri:
                r_draw.ellipse([tp[0]-8, tp[1]-8, tp[0]+8, tp[1]+8], fill=255)
        elif s_idx == 1:
            r_draw.ellipse([scx - sat_r * 0.45, scy - sat_r * 0.45, scx + sat_r * 0.45, scy + sat_r * 0.45], outline=255, width=8)
            r_draw.line([(scx, scy), (scx + sat_r * 0.6, scy)], fill=255, width=8)
        elif s_idx == 2:
            r_draw.arc([scx - sat_r * 0.5, scy - sat_r * 0.5, scx + sat_r * 0.5, scy + sat_r * 0.5], start=0, end=180, fill=255, width=10)
            r_draw.line([(scx, scy + sat_r * 0.2), (scx, scy + sat_r * 0.55)], fill=255, width=8)
        elif s_idx == 3:
            r_draw.arc([scx - sat_r * 0.5, scy - sat_r * 0.5, scx + sat_r * 0.5, scy + sat_r * 0.5], start=90, end=270, fill=255, width=10)
            r_draw.line([(scx - sat_r * 0.5, scy), (scx + sat_r * 0.4, scy)], fill=255, width=8)
            r_draw.polygon([(scx + sat_r * 0.55, scy), (scx + sat_r * 0.22, scy - 12), (scx + sat_r * 0.22, scy + 12)], fill=255)

    # --- 3. ELEMENT DISTINCT INSCRIBED STAR & DEDICATED CENTER CORE SYMBOLS ---
    if element_name == "Fire":
        # Inscribed Dual Triangles Hexagram
        tri1 = get_poly_pts(r2, 3, offset_deg=0.0)
        tri2 = get_poly_pts(r2, 3, offset_deg=180.0)
        draw_poly_loop(r_draw, tri1, width=22)
        draw_poly_loop(r_draw, tri2, width=22)
        
        # CENTER CORE: Sacred Upward Triangle Δ (Thick 26px)
        center_tri = get_poly_pts(r4, 3, offset_deg=0.0)
        draw_poly_loop(r_draw, center_tri, width=26)
        # Inner flame dot
        r_draw.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=255)

    elif element_name == "Earth":
        # Inscribed 8-Pointed Star
        sq1 = get_poly_pts(r2, 4, offset_deg=0.0)
        sq2 = get_poly_pts(r2, 4, offset_deg=45.0)
        draw_poly_loop(r_draw, sq1, width=22)
        draw_poly_loop(r_draw, sq2, width=22)
        
        # CENTER CORE: Solid Square / Diamond □ (Thick 26px)
        center_sq = get_poly_pts(r4, 4, offset_deg=45.0)
        draw_poly_loop(r_draw, center_sq, width=26)
        # Inner crystal cross +
        r_draw.line([(cx - r4*0.5, cy), (cx + r4*0.5, cy)], fill=255, width=16)
        r_draw.line([(cx, cy - r4*0.5), (cx, cy + r4*0.5)], fill=255, width=16)

    elif element_name == "Wind":
        # Inscribed Pentagram 5-Star
        p_pts = get_poly_pts(r2, 5, offset_deg=0.0)
        draw_star_chords(r_draw, p_pts, skip_step=2, width=22)
        
        # CENTER CORE: Regular Pentagon & Wind Swirl
        center_pent = get_poly_pts(r4, 5, offset_deg=0.0)
        draw_poly_loop(r_draw, center_pent, width=26)
        r_draw.arc([cx - r4*0.5, cy - r4*0.5, cx + r4*0.5, cy + r4*0.5], start=45, end=315, fill=255, width=16)

    elif element_name == "Water":
        # Inscribed Hexagonal Matrix
        h_pts = get_poly_pts(r2, 6, offset_deg=0.0)
        draw_poly_loop(r_draw, h_pts, width=22)
        draw_star_chords(r_draw, h_pts, skip_step=2, width=18)
        
        # CENTER CORE: 6-Armed Snowflake / Hexagon
        center_hex = get_poly_pts(r4, 6, offset_deg=0.0)
        draw_poly_loop(r_draw, center_hex, width=24)
        for p in center_hex:
            r_draw.line([(cx, cy), p], fill=255, width=14)
        r_draw.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], fill=255)

    elif element_name == "Lightning":
        # Inscribed Heptagram 7-Star
        hep_pts = get_poly_pts(r2, 7, offset_deg=0.0)
        draw_star_chords(r_draw, hep_pts, skip_step=3, width=22)
        
        # CENTER CORE: Sharp Lightning Bolt Sigil ⚡
        center_hep = get_poly_pts(r4, 7, offset_deg=0.0)
        draw_poly_loop(r_draw, center_hep, width=20)
        bolt = [
            (cx - r4*0.2, cy - r4*0.8),
            (cx + r4*0.5, cy - r4*0.1),
            (cx, cy - r4*0.05),
            (cx + r4*0.3, cy + r4*0.8),
            (cx - r4*0.4, cy + r4*0.1),
            (cx + r4*0.05, cy + r4*0.05)
        ]
        r_draw.polygon(bolt, fill=255)

    elif element_name == "DarkArcane":
        # Inscribed Chaos 8-Star
        oct_pts = get_poly_pts(r2, 8, offset_deg=0.0)
        draw_star_chords(r_draw, oct_pts, skip_step=3, width=22)
        
        # CENTER CORE: Occult Chaos Void Eye
        center_oct = get_poly_pts(r4, 8, offset_deg=22.5)
        draw_poly_loop(r_draw, center_oct, width=24)
        # Slit Pupil
        r_draw.ellipse([cx - r4*0.6, cy - r4*0.25, cx + r4*0.6, cy + r4*0.25], outline=255, width=14)
        r_draw.ellipse([cx - 12, cy - r4*0.22, cx + 12, cy + r4*0.22], fill=255)

    elif element_name == "Light":
        # Inscribed 10-Pointed Decagram Radiant Star
        dec_pts = get_poly_pts(r2, 10, offset_deg=0.0)
        draw_star_chords(r_draw, dec_pts, skip_step=3, width=22)
        
        # CENTER CORE: Radiant 12-Ray Solar Sunburst
        r_draw.ellipse([cx - r4*0.6, cy - r4*0.6, cx + r4*0.6, cy + r4*0.6], outline=255, width=22)
        for s in range(12):
            sa = math.radians(s * 30.0)
            sp1 = (cx + math.cos(sa) * (r4*0.65), cy + math.sin(sa) * (r4*0.65))
            sp2 = (cx + math.cos(sa) * (r4*0.95), cy + math.sin(sa) * (r4*0.95))
            r_draw.line([sp1, sp2], fill=255, width=14)
        r_draw.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], fill=255)

    else:
        # Master / Fusion Decagram Matrix
        dec_pts = get_poly_pts(r2, 10, offset_deg=0.0)
        draw_poly_loop(r_draw, dec_pts, width=20)
        draw_star_chords(r_draw, dec_pts, skip_step=3, width=18)
        
        hex_pts = get_poly_pts(r4, 6, offset_deg=0.0)
        draw_poly_loop(r_draw, hex_pts, width=24)
        r_draw.ellipse([cx - 28, cy - 28, cx + 28, cy + 28], fill=255)

    # --- 4. Saturated Gaussian Neon Halo (Channel G) ---
    combined_mask = Image.new("L", (size, size), 0)
    comb_draw = ImageDraw.Draw(combined_mask)
    comb_draw.bitmap((0, 0), r_img, fill=255)
    comb_draw.bitmap((0, 0), b_img, fill=255)
    
    g_img = combined_mask.filter(ImageFilter.GaussianBlur(24))
    g_wide = combined_mask.filter(ImageFilter.GaussianBlur(55))
    
    alpha_img = Image.new("L", (size, size), 0)
    p_a = alpha_img.load()
    p_r = r_img.load()
    p_b = b_img.load()
    p_g = g_img.load()
    p_gw = g_wide.load()
    
    for y in range(size):
        for x in range(size):
            r_val = p_r[x, y]
            b_val = p_b[x, y]
            g_val = p_g[x, y]
            gw_val = p_gw[x, y]
            
            a = min(255, int(r_val * 1.0 + b_val * 0.95 + g_val * 0.8 + gw_val * 0.45))
            p_a[x, y] = a

    final_rgba = Image.merge("RGBA", (r_img, g_img, b_img, alpha_img))
    final_rgba.save(output_path, "PNG")
    print(f"Generated {output_path}")

def generate_all():
    elements = ["Master", "Fire", "Earth", "Wind", "Water", "Lightning", "DarkArcane", "Light", "Fusion"]
    for el in elements:
        generate_element_texture(el)

if __name__ == "__main__":
    generate_all()

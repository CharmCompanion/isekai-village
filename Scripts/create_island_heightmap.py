import math
import struct
import zlib

def create_island_heightmap_r16(filepath="F:/DEVELOPMENT/Games/SpellCraft/Content/SpellCraft/Textures/Island_Heightmap_1009.r16", size=1009):
    """
    Generates a 1009x1009 16-bit raw heightmap matching Unreal Engine recommended landscape dimensions:
    - Center/Base elevation: Z ~ 0 to 300
    - South Beach Cove (X: 100-350, Y: 400-600): Flat, gentle sand entry at water level (Height ~ 32768 + 200)
    - Winding Valley Trail: Ascending path from South Beach toward the North
    - North Tower Plateau (X: 650-850, Y: 400-600): Broad, flat elevated plateau (Height ~ 32768 + 4500)
    - Coastline: Natural organic noise falloff into deep ocean water (Height = 32000)
    """
    import os
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    base_water_height = 32768  # Sea level
    beach_height = base_water_height + 300
    plateau_height = base_water_height + 4200

    data = bytearray()

    cx, cy = size / 2.0, size / 2.0
    radius = size * 0.40

    for y in range(size):
        ny = (y - cy) / radius # -1 to 1 (South is negative ny, North is positive ny)
        for x in range(size):
            nx = (x - cx) / radius # -1 to 1 (West is negative nx, East is positive nx)

            dist_from_center = math.sqrt(nx * nx + ny * ny)

            # Island boundary with organic coastline noise
            noise1 = math.sin(nx * 6.0) * math.cos(ny * 6.0) * 0.08
            noise2 = math.sin(nx * 14.0 + ny * 10.0) * 0.04
            noise3 = math.cos(nx * 28.0 - ny * 20.0) * 0.02
            effective_radius = 0.85 + noise1 + noise2 + noise3

            if dist_from_center > effective_radius:
                # Deep ocean floor
                h = base_water_height - 1200
            else:
                # Island landmass falloff factor (0 at coast, 1 at center)
                coast_factor = (effective_radius - dist_from_center) / effective_radius
                coast_factor = math.pow(coast_factor, 0.45) # Sharp coastal drop into water

                # Elevation profile along North-South axis
                # ny = -0.7 is South Beach (Low), ny = +0.5 is North Plateau (High)
                t_north = (ny + 0.7) / 1.3 # 0 at south beach, 1 at north plateau
                t_north = max(0.0, min(1.0, t_north))

                # South Beach Cove (ny < -0.3): Very gentle, low elevation
                if ny < -0.2:
                    beach_factor = (-0.2 - ny) / 0.6
                    base_elev = beach_height + (math.sin(nx * 8.0) * 100.0)
                    h = int(base_water_height + (base_elev - base_water_height) * coast_factor)
                # North Plateau (ny > 0.3 and abs(nx) < 0.45): Flat building terrace
                elif ny > 0.25 and abs(nx) < 0.40:
                    plateau_factor = min(1.0, (ny - 0.25) / 0.35)
                    base_elev = beach_height + (plateau_height - beach_height) * plateau_factor
                    # Add subtle terrain variation
                    base_elev += math.sin(nx * 10.0) * math.cos(ny * 10.0) * 80.0
                    h = int(base_elev)
                # Winding Valley Trail (Mid island)
                else:
                    valley_t = (ny + 0.2) / 0.45
                    base_elev = beach_height + (plateau_height - beach_height) * (valley_t * 0.7)
                    # Flanking ridges
                    ridge_noise = math.cos(nx * 5.0) * 400.0
                    base_elev += ridge_noise
                    h = int(base_water_height + (base_elev - base_water_height) * coast_factor)

            h = max(0, min(65535, h))
            data += struct.pack("<H", h)

    with open(filepath, "wb") as f:
        f.write(data)

    print(f"16-bit Heightmap successfully written to {filepath} ({len(data)} bytes)!")

if __name__ == "__main__":
    create_island_heightmap_r16()

import noise

PLAINS_COLOR = (124, 196, 94)
FOREST_COLOR = (34, 139, 34)
MOUNTAIN_COLOR = (120, 120, 120)
SNOW_COLOR = (235, 235, 235)
DESERT_COLOR = (225, 200, 120)
TAIGA_COLOR = (45, 90, 70)
TOUNDRA_COLOR = (160, 185, 160)


def _noise(
    x: float,
    y: float,
    scale: float,
    *,
    octaves: int,
    persistence: float,
    lacunarity: float,
    base: int,
) -> float:
    return noise.pnoise2(
        x / scale,
        y / scale,
        octaves=octaves,
        persistence=persistence,
        lacunarity=lacunarity,
        base=base,
    )


def get_tile_biome(tile_x: int, tile_y: int, seed: int, scale: float = 60.0) -> str:
    continent_scale = scale * 6.5
    detail_scale = scale * 2.2
    moisture_scale = scale * 4.2
    temp_scale = scale * 5.5

    warp = _noise(
        tile_x,
        tile_y,
        continent_scale * 0.7,
        octaves=2,
        persistence=0.5,
        lacunarity=2.0,
        base=seed + 77,
    )
    warp_x = tile_x + warp * 28.0
    warp_y = tile_y + warp * 28.0

    elevation = _noise(
        warp_x,
        warp_y,
        continent_scale,
        octaves=4,
        persistence=0.5,
        lacunarity=2.0,
        base=seed,
    )
    detail = _noise(
        warp_x,
        warp_y,
        detail_scale,
        octaves=2,
        persistence=0.55,
        lacunarity=2.0,
        base=seed + 11,
    )
    moisture = _noise(
        warp_x,
        warp_y,
        moisture_scale,
        octaves=3,
        persistence=0.55,
        lacunarity=2.0,
        base=seed + 31,
    )
    temperature = _noise(
        warp_x,
        warp_y,
        temp_scale,
        octaves=2,
        persistence=0.5,
        lacunarity=2.0,
        base=seed + 53,
    )

    elevation = (elevation + 1.0) * 0.5
    detail = (detail + 1.0) * 0.5
    moisture = (moisture + 1.0) * 0.5
    temperature = (temperature + 1.0) * 0.5

    elevation = elevation * 0.8 + detail * 0.2
    temperature = temperature - elevation * 0.4

    if elevation > 0.80:  # altitude
        return "snow"
    if elevation > 0.68:
        return "mountain"
    if temperature > 0.45:
        if moisture < 0.35:  # humidité
            return "desert"
        if moisture > 0.60:
            return "forest"
        return "plains"
    else:  # zones froides
        if moisture > 0.50:
            return "taiga"
        return "toundra"


def color_for_biome(biome: str, elevation: float = 0.5):
    # variation est un entier entre -20 et +20 selon l'élévation de la tile
    # elevation=0.5 (milieu) → variation=0, elevation=1.0 (haut) → +20, elevation=0.0 (bas) → -20
    variation = int((elevation - 0.5) * 40)

    # dictionnaire qui associe chaque nom de biome à sa couleur de base
    colors = {
        "snow": SNOW_COLOR,
        "mountain": MOUNTAIN_COLOR,
        "desert": DESERT_COLOR,
        "forest": FOREST_COLOR,
        "taiga": TAIGA_COLOR,
        "toundra": TOUNDRA_COLOR,
    }

    # récupère la couleur du biome, ou PLAINS_COLOR si le biome est inconnu
    r, g, b = colors.get(biome, PLAINS_COLOR)

    # applique la variation sur chaque canal RGB
    # max(0, ...) empêche de descendre sous 0, min(255, ...) empêche de dépasser 255
    return (
        max(0, min(255, r + variation)),
        max(0, min(255, g + variation)),
        max(0, min(255, b + variation)),
    )


def get_tile_color(tile_x: int, tile_y: int, seed: int, scale: float = 60.0):
    # détermine le biome de la tile
    biome = get_tile_biome(tile_x, tile_y, seed, scale)

    # recalcule l'élévation pour la passer à color_for_biome
    # on utilise les mêmes paramètres que dans get_tile_biome pour être cohérent
    continent_scale = scale * 6.5
    warp = _noise(
        tile_x,
        tile_y,
        continent_scale * 0.7,
        octaves=2,
        persistence=0.5,
        lacunarity=2.0,
        base=seed + 77,
    )
    # décale les coordonnées avec le warp pour des formes plus naturelles (même logique que get_tile_biome)
    warp_x = tile_x + warp * 28.0
    warp_y = tile_y + warp * 28.0
    # calcule l'élévation brute entre -1.0 et 1.0
    elevation = _noise(
        warp_x,
        warp_y,
        continent_scale,
        octaves=4,
        persistence=0.5,
        lacunarity=2.0,
        base=seed,
    )
    # normalise l'élévation entre 0.0 et 1.0
    elevation = (elevation + 1.0) * 0.5

    # retourne la couleur finale avec la variation d'élévation appliquée
    return color_for_biome(biome, elevation)

import noise

RIVER_COLOR = (65, 105, 225)
PLAINS_COLOR = (124, 196, 94)
FOREST_COLOR = (34, 139, 34)
MOUNTAIN_COLOR = (120, 120, 120)
SNOW_COLOR = (235, 235, 235)


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
    river_scale = scale * 2.8

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
    temperature = temperature - elevation * 0.5

    river_noise = abs(
        _noise(
            warp_x,
            warp_y,
            river_scale,
            octaves=1,
            persistence=0.5,
            lacunarity=2.0,
            base=seed + 101,
        )
    )

    if river_noise < 0.025 and elevation < 0.72:
        return "river"
    if elevation > 0.82 or (elevation > 0.7 and temperature < 0.25):
        return "snow"
    if elevation > 0.68:
        return "mountain"
    if moisture > 0.55:
        return "forest"
    return "plains"


def color_for_biome(biome: str):
    if biome == "river":
        return RIVER_COLOR
    if biome == "snow":
        return SNOW_COLOR
    if biome == "mountain":
        return MOUNTAIN_COLOR
    if biome == "forest":
        return FOREST_COLOR
    return PLAINS_COLOR


def get_tile_color(tile_x: int, tile_y: int, seed: int, scale: float = 60.0):
    biome = get_tile_biome(tile_x, tile_y, seed, scale)
    return color_for_biome(biome)

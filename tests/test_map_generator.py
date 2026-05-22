from client.core import biome
from client.core import map_generator as mg


def test_generate_background_surface_uses_tile_color(monkeypatch):
    monkeypatch.setattr(
        mg, "get_tile_color", lambda x, y, seed, scale: biome.SNOW_COLOR
    )

    surface = mg.generate_background_surface(20, 20)

    assert surface.get_at((1, 1))[:3] == biome.SNOW_COLOR


def test_generate_background_surface_uses_tile_color_with_alt_value(monkeypatch):
    monkeypatch.setattr(
        mg, "get_tile_color", lambda x, y, seed, scale: biome.FOREST_COLOR
    )

    surface = mg.generate_background_surface(20, 20)

    assert surface.get_at((1, 1))[:3] == biome.FOREST_COLOR

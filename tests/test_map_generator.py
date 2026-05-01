from client.core import map_generator as mg


def test_generate_background_surface_water(monkeypatch):
    monkeypatch.setattr(mg.noise, "pnoise2", lambda x, y, base=0: -1.0)

    surface = mg.generate_background_surface(20, 20)

    assert surface.get_at((1, 1))[:3] == mg.WATER_COLOR


def test_generate_background_surface_city(monkeypatch):
    monkeypatch.setattr(mg.noise, "pnoise2", lambda x, y, base=0: 1.0)

    surface = mg.generate_background_surface(20, 20)

    assert surface.get_at((1, 1))[:3] == mg.CITY_COLOR

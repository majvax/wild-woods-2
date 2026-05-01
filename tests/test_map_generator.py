from client.core import map_generator as mg


def test_generer_surface_fond_water(monkeypatch):
    monkeypatch.setattr(mg.noise, "pnoise2", lambda x, y, base=0: -1.0)

    surface = mg.generer_surface_fond(20, 20)

    assert surface.get_at((1, 1))[:3] == mg.COULEUR_EAU


def test_generer_surface_fond_city(monkeypatch):
    monkeypatch.setattr(mg.noise, "pnoise2", lambda x, y, base=0: 1.0)

    surface = mg.generer_surface_fond(20, 20)

    assert surface.get_at((1, 1))[:3] == mg.COULEUR_VILLE

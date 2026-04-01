import pygame
import noise
import random

COULEUR_EAU = (65, 105, 225)  # Bleu
COULEUR_FORET = (34, 139, 34)  # Vert
COULEUR_VILLE = (128, 128, 128)  # Gris

TAILLE_CASE = 10


def generer_surface_fond(largeur: int, hauteur: int):

    surface = pygame.Surface((largeur, hauteur))
    graine = random.randint(0, 1000)
    echelle = 20.0

    colonnes = int(largeur / TAILLE_CASE)
    lignes = int(hauteur / TAILLE_CASE)

    for y in range(lignes):
        for x in range(colonnes):
            valeur_bruit = noise.pnoise2(x / echelle, y / echelle, base=graine)

            if valeur_bruit < -0.5:
                couleur = COULEUR_EAU
            elif valeur_bruit < 0.2:
                couleur = COULEUR_FORET
            else:
                couleur = COULEUR_VILLE

            rect = (x * TAILLE_CASE, y * TAILLE_CASE, TAILLE_CASE, TAILLE_CASE)
            pygame.draw.rect(surface, couleur, rect)

    return surface

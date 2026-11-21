"""
Campo de estrellas con parallax + destellos (lobby epico)
"""
import random
import math
import pygame
from config import TEXTO, SUAVE, AZUL, CIAN, MORADO, DORADO


class Estrellas:
    def __init__(self, w, h, n=160):
        self.w, self.h = w, h
        self.stars = []
        for _ in range(n):
            capa = random.choice([0.25, 0.55, 1.0, 1.4])
            self.stars.append({
                "x": random.uniform(0, w),
                "y": random.uniform(0, h),
                "z": capa,
                "s": random.uniform(0.4, 2.6) * (0.6 + capa * 0.5),
                "c": random.choice([TEXTO, SUAVE, AZUL, CIAN, MORADO, DORADO, (180, 200, 255)]),
                "tw": random.uniform(0, 6.28),
            })
        self.t = 0.0

    def update(self, dt=1/30):
        self.t += dt
        for s in self.stars:
            s["y"] += s["z"] * 22 * dt
            s["tw"] += dt * (1.5 + s["z"])
            if s["y"] > self.h + 8:
                s["y"] = -8
                s["x"] = random.uniform(0, self.w)
                s["z"] = random.choice([0.25, 0.55, 1.0, 1.4])

    def draw(self, superficie):
        for s in self.stars:
            brillo = 0.55 + 0.45 * (0.5 + 0.5 * math.sin(s["tw"]))
            r = max(1, int(s["s"] * s["z"] * brillo))
            col = tuple(min(255, int(c * brillo)) for c in s["c"][:3])
            pygame.draw.circle(superficie, col, (int(s["x"]), int(s["y"])), r)
            if s["z"] > 1.0 and r >= 2:
                pygame.draw.circle(superficie, (*col, 40) if len(col) == 3 else col,
                                   (int(s["x"]), int(s["y"])), r + 2, 1)

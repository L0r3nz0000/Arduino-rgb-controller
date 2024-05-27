import math

class CubicBezierFilter:
    def lightness(x):
        y = ((x - .5) * 1.6) ** 3 + .5
        return max(min(y, 1), 0)
    
    def saturation(x):
        if x > 0:  # Dominio del logaritmo
            y = (math.log10(x) + 2) / 2
        else:
            y = 1
        return max(min(y, 1), 0)
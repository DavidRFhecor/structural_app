"""
material_library.py  →  structural_app/shared/domain/material_library.py
=========================================================================
Catálogo de hormigones y aceros según EC2 / EHE-08.

USO EN UN ADAPTADOR:
    from structural_app.shared.domain.material_library import MATERIAL_LIB
    mat = MATERIAL_LIB.resolve_materials("HA-30", "B 500 S")
    fck, fcd, fyd = mat["fck"], mat["fcd"], mat["fyd"]
"""
from dataclasses import dataclass, field
from typing import Dict, Optional

GAMMA_C     = 1.5    # hormigón, situación persistente
GAMMA_S     = 1.15   # acero,    situación persistente
GAMMA_S_SIS = 1.0    # acero,    combinación sísmica (EHE Art.15)


@dataclass
class ConcreteGrade:
    name: str
    fck: float          # MPa
    fcm:  float = field(init=False)
    fctm: float = field(init=False)
    Ecm:  float = field(init=False)   # GPa
    eps_cu2: float = 0.0035
    eps_c2:  float = 0.0020

    def __post_init__(self):
        self.fcm  = self.fck + 8.0
        self.fctm = (0.30 * self.fck ** (2/3)
                     if self.fck <= 50
                     else 2.12 * (1 + self.fcm / 10) ** (1/3))
        self.Ecm  = 22.0 * (self.fcm / 10) ** 0.3

    def fcd(self, gamma_c: float = GAMMA_C) -> float:
        return self.fck / gamma_c

    def fctd(self, gamma_c: float = GAMMA_C) -> float:
        return self.fctm / gamma_c


@dataclass
class SteelGrade:
    name: str
    fyk: float          # MPa
    Es: float = 200_000.0

    def fyd(self, gamma_s: float = GAMMA_S) -> float:
        return self.fyk / gamma_s

    def eps_yd(self, gamma_s: float = GAMMA_S) -> float:
        return self.fyd(gamma_s) / self.Es


class MaterialLibrary:
    _CONCRETES: Dict[str, ConcreteGrade] = {
        g.name: g for g in [
            ConcreteGrade("HA-20", 20.0),
            ConcreteGrade("HA-25", 25.0),
            ConcreteGrade("HA-30", 30.0),
            ConcreteGrade("HA-35", 35.0),
            ConcreteGrade("HA-40", 40.0),
            ConcreteGrade("HA-45", 45.0),
            ConcreteGrade("HA-50", 50.0),
            ConcreteGrade("HA-55", 55.0),
            ConcreteGrade("HA-60", 60.0),
        ]
    }
    _STEELS: Dict[str, SteelGrade] = {
        g.name: g for g in [
            SteelGrade("B 400 S", 400.0),
            SteelGrade("B 500 S", 500.0),
            SteelGrade("B 500 T", 500.0),
            SteelGrade("B 600 S", 600.0),
            SteelGrade("Y 1570",  1570.0, Es=195_000.0),
            SteelGrade("Y 1670",  1670.0, Es=195_000.0),
            SteelGrade("Y 1770",  1770.0, Es=195_000.0),
            SteelGrade("Y 1860",  1860.0, Es=195_000.0),
        ]
    }

    def get_concrete(self, name: str) -> Optional[ConcreteGrade]:
        return self._CONCRETES.get(name)

    def get_steel(self, name: str) -> Optional[SteelGrade]:
        return self._STEELS.get(name)

    def resolve_materials(
        self,
        concrete_name: str,
        steel_name: str,
        gamma_c: float = GAMMA_C,
        gamma_s: float = GAMMA_S,
    ) -> dict:
        """Devuelve dict con fck, fcd, fctm, Ecm, fyk, fyd, Es."""
        result = {}
        conc  = self.get_concrete(concrete_name)
        steel = self.get_steel(steel_name)
        if conc:
            result.update({
                "fck":  conc.fck,
                "fcd":  round(conc.fcd(gamma_c), 3),
                "fctm": round(conc.fctm, 3),
                "Ecm":  round(conc.Ecm, 2),
            })
        if steel:
            result.update({
                "fyk": steel.fyk,
                "fyd": round(steel.fyd(gamma_s), 3),
                "Es":  steel.Es,
            })
        return result

    @classmethod
    def concrete_options_for_json(cls) -> list:
        """Lista lista para pegar en 'options' de un campo type='select'."""
        return [{"value": n, "label": n, "fck": g.fck}
                for n, g in sorted(cls._CONCRETES.items())]

    @classmethod
    def steel_options_for_json(cls) -> list:
        return [{"value": n, "label": n, "fyk": g.fyk}
                for n, g in sorted(cls._STEELS.items())]


# Instancia global — importar directamente en los adaptadores
MATERIAL_LIB = MaterialLibrary()
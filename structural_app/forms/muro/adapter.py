"""
forms/muro/adapter.py
=====================
Adaptador del formulario "Muro de Contención".
Sustituye al stub actual con cálculo real de estabilidad (Rankine)
y devuelve SolverResponse con todos los campos enriquecidos:
  - scenarios          (EST con SC / EST sin SC)
  - intermediate_tables (empujes por altura)
  - material_results   (HA-25 por defecto; preparado para select)
  - measurements       (m³ hormigón, kg acero, precio estimado)
  - warnings           (avisos no bloqueantes)
"""
import math
from pydantic import BaseModel, Field
from typing import List, Optional

from structural_app.shared.domain.result_models import (
    SolverResponse, CheckResult,
    ScenarioResult,
    IntermediateTable, TableColumn,
    MaterialResult, DerivedValue,
    MeasurementResult, MeasurementLine,
)
from structural_app.shared.domain.material_library import MATERIAL_LIB


# ---------------------------------------------------------------------------
# Modelo de entrada — coincide con los IDs del config.json actual
# ---------------------------------------------------------------------------
class Estrato(BaseModel):
    espesor: float = Field(gt=0, default=1.0)
    gamma:   float = Field(gt=0, default=18.0)
    phi:     float = Field(ge=10, le=45, default=30.0)


class MuroInput(BaseModel):
    # Dimensiones
    h_muro:   float = Field(gt=0, default=4.0)
    b_zapata: float = Field(gt=0, default=2.5)
    # Cargas (campo "ved" del config.json actual — se usa como cortante horizontal)
    ved: float = Field(ge=0, default=150.0)
    # Tabla de estratos
    tabla_estratos: List[Estrato] = []
    # Materiales (preparado para cuando el config.json tenga type=select)
    hormigon: str = "HA-25"
    acero:    str = "B 500 S"


# ---------------------------------------------------------------------------
# Función principal
# ---------------------------------------------------------------------------
def calculate_element(payload: dict) -> SolverResponse:
    payload.pop("_features", None)

    # Convertir la tabla de estratos de lista-de-listas a lista-de-dicts
    if "tabla_estratos" in payload and payload["tabla_estratos"]:
        primera_fila = payload["tabla_estratos"][0]
        if isinstance(primera_fila, (list, tuple)):
            cols = ["espesor", "gamma", "phi"]
            payload["tabla_estratos"] = [
                dict(zip(cols, fila)) for fila in payload["tabla_estratos"]
            ]

    try:
        data = MuroInput(**payload)
    except Exception as e:
        return SolverResponse(
            is_ok=False,
            summary=f"Error en datos de entrada: {e}",
            checks=[],
        )

    # ── 1. Materiales ──────────────────────────────────────────────────────
    mat = MATERIAL_LIB.resolve_materials(data.hormigon, data.acero)
    fck = mat.get("fck", 25.0)
    fcd = mat.get("fcd", fck / 1.5)
    fyk = mat.get("fyk", 500.0)
    fyd = mat.get("fyd", fyk / 1.15)
    fctm = mat.get("fctm", 0.30 * fck ** (2/3))

    material_results = MaterialResult(items=[
        DerivedValue(label="fck",  value=fck,          unit="MPa", formula=data.hormigon),
        DerivedValue(label="fcd",  value=round(fcd, 2), unit="MPa", formula=f"fck / γc = {fck} / 1.5"),
        DerivedValue(label="fctm", value=round(fctm,3), unit="MPa"),
        DerivedValue(label="fyk",  value=fyk,          unit="MPa", formula=data.acero),
        DerivedValue(label="fyd",  value=round(fyd, 2), unit="MPa", formula=f"fyk / γs = {fyk} / 1.15"),
    ])

    # ── 2. Propiedades del terreno (promedio ponderado de estratos) ─────────
    if data.tabla_estratos:
        espesor_total = sum(e.espesor for e in data.tabla_estratos)
        gamma_medio   = sum(e.espesor * e.gamma for e in data.tabla_estratos) / espesor_total
        phi_medio     = sum(e.espesor * e.phi   for e in data.tabla_estratos) / espesor_total
    else:
        gamma_medio, phi_medio = 18.0, 30.0

    phi_r = math.radians(phi_medio)
    Ka    = (1 - math.sin(phi_r)) / (1 + math.sin(phi_r))     # Rankine

    # ── 3. Tabla de empujes por altura ─────────────────────────────────────
    h_zapata = 0.5          # estimado; cuando haya campo en config.json usarlo
    H_total  = data.h_muro + h_zapata
    sc       = 10.0         # kN/m² SC estimada (cuando haya campo, usar payload)

    N_SEC = 11
    rows_empujes = []
    for i in range(N_SEC):
        h  = data.h_muro * i / (N_SEC - 1)
        Ea = 0.5 * Ka * gamma_medio * h**2
        Esc= Ka * sc * h
        Md = Ea * h / 3 + Esc * h / 2
        rows_empujes.append({
            "H":   round(h, 2),
            "Ka":  round(Ka, 4),
            "Ea":  round(Ea,  2),
            "Esc": round(Esc, 2),
            "Md":  round(Md,  2),
        })

    Ea_base  = 0.5 * Ka * gamma_medio * data.h_muro**2
    Esc_base = Ka * sc * data.h_muro
    H_h      = Ea_base + Esc_base          # fuerza horizontal total (kN/m)

    tabla_empujes = IntermediateTable(
        id="empujes_por_altura",
        title="Empujes por altura del muro",
        columns=[
            TableColumn(id="H",   label="H",        unit="m",      format=".2f"),
            TableColumn(id="Ka",  label="Ka",        unit="—",      format=".4f"),
            TableColumn(id="Ea",  label="Ea",        unit="kN/m",   format=".2f"),
            TableColumn(id="Esc", label="Esc (SC)",  unit="kN/m",   format=".2f"),
            TableColumn(id="Md",  label="Md",        unit="mkN/m",  format=".2f",
                        highlight=True),
        ],
        rows=rows_empujes,
        footer={
            "H": "Base", "Ka": round(Ka, 4),
            "Ea": round(Ea_base, 2), "Esc": round(Esc_base, 2),
            "Md": round(rows_empujes[-1]["Md"], 2),
        },
        note=(f"Ka = {Ka:.4f} (Rankine, phi_med = {phi_medio:.1f}°, "
              f"gamma_med = {gamma_medio:.1f} kN/m³)."),
    )

    # ── 4. Checks de estabilidad ───────────────────────────────────────────
    def _estabilidad(con_sc: bool) -> tuple[List[CheckResult], bool]:
        checks = []
        h_prom = (0.3 + 0.5) / 2          # estimado mientras no haya campo
        peso_muro    = 25.0 * h_prom * data.h_muro
        peso_zapata  = 25.0 * data.b_zapata * h_zapata
        peso_relleno = gamma_medio * (data.b_zapata - 0.5 - h_prom) * data.h_muro
        sc_v = sc * data.b_zapata if con_sc else 0.0
        V    = peso_muro + peso_zapata + peso_relleno + sc_v
        H_horiz = H_h if con_sc else Ea_base

        # también sumamos el cortante externo ved
        H_horiz += data.ved / data.h_muro   # distribución lineal estimada

        mu = math.tan(math.radians(phi_medio))

        # Deslizamiento
        FS_d = (mu * V) / H_horiz if H_horiz > 0 else 99.0
        checks.append(CheckResult(
            description="Seguridad al Deslizamiento",
            status=FS_d >= 1.5,
            value=round(FS_d, 3), limit=1.5, unit="FS",
            ratio=round(FS_d / 1.5, 3),
            reference="EC7 §6.5.3",
        ))

        # Vuelco
        M_e = V * (data.b_zapata / 2)
        M_v = H_horiz * (H_total / 3)
        FS_v = M_e / M_v if M_v > 0 else 99.0
        checks.append(CheckResult(
            description="Seguridad al Vuelco",
            status=FS_v >= 1.8,
            value=round(FS_v, 3), limit=1.8, unit="FS",
            ratio=round(FS_v / 1.8, 3),
            reference="EC7 §6.5.4",
        ))

        # Tensión en terreno
        ecc   = abs((M_e - M_v) / V) if V > 0 else 0.0
        sigma = (V / data.b_zapata) * (1 + 6 * ecc / data.b_zapata)
        sigma_adm = 2.0   # kg/cm² default; cuando haya campo usarlo
        sig_kgcm2 = sigma / 10.0
        checks.append(CheckResult(
            description="Tensión máx. en terreno",
            status=sig_kgcm2 <= sigma_adm,
            value=round(sig_kgcm2, 3), limit=sigma_adm, unit="kg/cm²",
            ratio=round(sig_kgcm2 / sigma_adm, 3),
            reference="EC7 §6.5.2",
        ))

        return checks, all(c.status for c in checks)

    checks_sc,   ok_sc   = _estabilidad(con_sc=True)
    checks_nosc, ok_nosc = _estabilidad(con_sc=False)

    scenarios = {
        "Estático (con SC)":  ScenarioResult(
            label="Estático (con SC)",  checks=checks_sc,   is_ok=ok_sc),
        "Estático (sin SC)":  ScenarioResult(
            label="Estático (sin SC)",  checks=checks_nosc, is_ok=ok_nosc),
    }

    # ── 5. Mediciones estimadas ────────────────────────────────────────────
    e_prom   = 0.4
    vol_alz  = e_prom * data.h_muro
    vol_zap  = data.b_zapata * h_zapata
    kg_acero = (vol_alz + vol_zap) * 80.0
    p_horm   = 85.0
    p_acero  = 0.90

    measurements = MeasurementResult(
        lines=[
            MeasurementLine(
                description="Hormigón alzado",
                quantity=round(vol_alz, 3), unit="m³/m",
                unit_price=p_horm, total=round(vol_alz * p_horm, 2),
            ),
            MeasurementLine(
                description="Hormigón zapata",
                quantity=round(vol_zap, 3), unit="m³/m",
                unit_price=p_horm, total=round(vol_zap * p_horm, 2),
            ),
            MeasurementLine(
                description="Acero (estimación 80 kg/m³)",
                quantity=round(kg_acero, 1), unit="kg/m",
                unit_price=p_acero, total=round(kg_acero * p_acero, 2),
            ),
        ],
        grand_total=round(
            (vol_alz + vol_zap) * p_horm + kg_acero * p_acero, 2
        ),
        currency="€",
    )

    # ── 6. Avisos ──────────────────────────────────────────────────────────
    warnings = []
    if data.h_muro > 6.0:
        warnings.append(
            f"Muro alto (H = {data.h_muro} m > 6 m): "
            "considerar análisis sísmico y revisión de armado."
        )
    if not data.tabla_estratos:
        warnings.append(
            "No se han definido estratos del terreno. "
            "Se han usado valores por defecto (γ=18 kN/m³, φ=30°)."
        )
    if Ka > 0.40:
        warnings.append(
            f"Ka = {Ka:.3f} elevado. Verificar el ángulo de fricción del relleno."
        )

    # ── 7. Respuesta ───────────────────────────────────────────────────────
    global_ok = ok_sc and ok_nosc

    return SolverResponse(
        is_ok=global_ok,
        summary=(
            f"Muro H={data.h_muro} m · B={data.b_zapata} m · "
            f"{data.hormigon} · phi_med={phi_medio:.1f}°"
        ),
        checks=checks_sc,                      # checks raíz = escenario principal
        scenarios=scenarios,
        intermediate_tables=[tabla_empujes],
        material_results=material_results,
        measurements=measurements,
        warnings=warnings,
    )
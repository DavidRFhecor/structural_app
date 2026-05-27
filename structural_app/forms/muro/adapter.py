"""
forms/muro/adapter.py
=====================
Adaptador del formulario "Muro de Contención".
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
# Modelo de entrada — IDs exactos del config.json
# ---------------------------------------------------------------------------
class Estrato(BaseModel):
    espesor: float = Field(gt=0, default=1.0)
    gamma:   float = Field(gt=0, default=18.0)
    phi:     float = Field(ge=10, le=45, default=30.0)


class MuroInput(BaseModel):
    # Geometría muro
    h_muro:        float = Field(gt=0, default=6.5)
    e_coronacion:  float = Field(gt=0, default=0.5)
    incl_trasdos:  float = Field(gt=0, default=100000.0)
    long_alzado:   float = Field(gt=0, default=1.0)

    # Geometría zapata
    puntera:       float = Field(ge=0, default=1.5)
    talon:         float = Field(ge=0, default=3.0)
    canto_min_zap: float = Field(gt=0, default=1.0)
    canto_max_zap: float = Field(gt=0, default=1.5)
    long_zapata:   float = Field(gt=0, default=1.0)

    # Relleno
    gamma_relleno: float = Field(gt=0, default=18.0)
    phi_relleno:   float = Field(ge=10, le=45, default=27.0)
    delta_coulomb: float = Field(ge=0, default=15.0)
    beta_relleno:  float = Field(ge=0, default=0.0)
    sc:            float = Field(ge=0, default=10.0)

    # Terreno de apoyo
    sigma_adm_est:  float = Field(gt=0, default=2.0)
    sigma_adm_sis:  float = Field(gt=0, default=3.0)
    pct_comprimido: float = Field(ge=0, default=75.0)
    phi_terreno:    float = Field(ge=10, le=45, default=30.0)

    # Tabla de estratos
    tabla_estratos: List[Estrato] = []

    # Acciones en cabeza
    carga_h: float = 0.0
    carga_v: float = 0.0
    momento: float = 0.0

    # Sismo
    considerar_sismo: bool  = False
    inercia_muro:     bool  = True
    inercia_zapata:   bool  = False
    ac_horizontal:    float = 0.07
    ac_vertical:      float = 0.035

    # Coeficientes de seguridad
    fs_desliz_est: float = 1.5
    fs_desliz_sis: float = 1.1
    fs_vuelco_est: float = 1.8
    fs_vuelco_sis: float = 1.265

    # Materiales
    hormigon: str = "HA-25"
    acero:    str = "B 500 S"

    # Parámetros Coulomb
    coulomb_d: float = 15.0
    coulomb_a: float = 0.0


# ---------------------------------------------------------------------------
# Cálculos parciales (botones del formulario)
# ---------------------------------------------------------------------------
def validate_geo(data: dict) -> dict:
    """Validación parcial de la geometría del muro."""
    h_muro       = float(data.get("h_muro", 0) or 0)
    e_coronacion = float(data.get("e_coronacion", 0) or 0)
    puntera      = float(data.get("puntera", 0) or 0)
    talon        = float(data.get("talon", 0) or 0)
    ancho_total  = puntera + e_coronacion + talon

    return {
        "geo_status": "OK" if h_muro > 0 and e_coronacion > 0 and ancho_total > 0 else "ERROR",
        "b_zapata":   round(ancho_total, 3),
    }


def calc_earth_coefficients(data: dict) -> dict:
    """Cálculo de Ka (Rankine) y Kp."""
    phi = math.radians(float(data.get("phi_relleno", 30) or 30))
    ka  = (1 - math.sin(phi)) / (1 + math.sin(phi))
    kp  = 1 / ka if ka != 0 else 0

    return {
        "ka_val": round(ka, 3),
        "kp_val": round(kp, 3),
    }


# ---------------------------------------------------------------------------
# Función principal
# ---------------------------------------------------------------------------
def calculate_element(payload: dict) -> SolverResponse:
    payload.pop("_features", None)

    # ── 0. Cálculos intermedios — se ejecutan siempre al calcular ──────────
    #    Sus resultados se devuelven en form_data_updates para que
    #    base_state los escriba de vuelta en form_data y actualice la UI.
    intermedios = {}
    intermedios.update(validate_geo(payload))
    intermedios.update(calc_earth_coefficients(payload))
    payload.update(intermedios)

    # Convertir tabla_estratos de lista-de-listas a lista-de-dicts
    if "tabla_estratos" in payload and payload["tabla_estratos"]:
        primera_fila = payload["tabla_estratos"][0]
        if isinstance(primera_fila, (list, tuple)):
            cols = ["espesor", "gamma", "phi"]
            payload["tabla_estratos"] = [
                dict(zip(cols, fila)) for fila in payload["tabla_estratos"]
            ]

    # Filtrar solo los campos que MuroInput conoce
    known    = MuroInput.model_fields.keys()
    filtered = {k: v for k, v in payload.items() if k in known}

    try:
        data = MuroInput(**filtered)
    except Exception as e:
        return SolverResponse(
            is_ok=False,
            summary=f"Error en datos de entrada: {e}",
            checks=[],
        )

    # Derivados geométricos
    b_zapata = data.puntera + data.e_coronacion + data.talon
    h_zapata = data.canto_max_zap

    # ── 1. Materiales ──────────────────────────────────────────────────────
    mat  = MATERIAL_LIB.resolve_materials(data.hormigon, data.acero)
    fck  = mat.get("fck", 25.0)
    fcd  = mat.get("fcd", fck / 1.5)
    fyk  = mat.get("fyk", 500.0)
    fyd  = mat.get("fyd", fyk / 1.15)
    fctm = mat.get("fctm", 0.30 * fck ** (2 / 3))

    material_results = MaterialResult(items=[
        DerivedValue(label="fck",  value=fck,            unit="MPa", formula=data.hormigon),
        DerivedValue(label="fcd",  value=round(fcd,  2), unit="MPa", formula=f"fck / γc = {fck} / 1.5"),
        DerivedValue(label="fctm", value=round(fctm, 3), unit="MPa"),
        DerivedValue(label="fyk",  value=fyk,            unit="MPa", formula=data.acero),
        DerivedValue(label="fyd",  value=round(fyd,  2), unit="MPa", formula=f"fyk / γs = {fyk} / 1.15"),
    ])

    # ── 2. Propiedades del terreno (promedio ponderado de estratos) ─────────
    if data.tabla_estratos:
        espesor_total = sum(e.espesor for e in data.tabla_estratos)
        gamma_medio   = sum(e.espesor * e.gamma for e in data.tabla_estratos) / espesor_total
        phi_medio     = sum(e.espesor * e.phi   for e in data.tabla_estratos) / espesor_total
    else:
        gamma_medio = data.gamma_relleno
        phi_medio   = data.phi_relleno

    Ka = intermedios["ka_val"]

    # ── 3. Tabla de empujes por altura ─────────────────────────────────────
    N_SEC = 11
    rows_empujes = []
    for i in range(N_SEC):
        h   = data.h_muro * i / (N_SEC - 1)
        Ea  = 0.5 * Ka * gamma_medio * h ** 2
        Esc = Ka * data.sc * h
        Md  = Ea * h / 3 + Esc * h / 2
        rows_empujes.append({
            "H":   round(h,   2),
            "Ka":  round(Ka,  4),
            "Ea":  round(Ea,  2),
            "Esc": round(Esc, 2),
            "Md":  round(Md,  2),
        })

    Ea_base  = 0.5 * Ka * gamma_medio * data.h_muro ** 2
    Esc_base = Ka * data.sc * data.h_muro
    H_h      = Ea_base + Esc_base

    tabla_empujes = IntermediateTable(
        id="empujes_por_altura",
        title="Empujes por altura del muro",
        columns=[
            TableColumn(id="H",   label="H",       unit="m",     format=".2f"),
            TableColumn(id="Ka",  label="Ka",       unit="—",     format=".4f"),
            TableColumn(id="Ea",  label="Ea",       unit="kN/m",  format=".2f"),
            TableColumn(id="Esc", label="Esc (SC)", unit="kN/m",  format=".2f"),
            TableColumn(id="Md",  label="Md",       unit="mkN/m", format=".2f", highlight=True),
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
    e_base_alzado  = data.e_coronacion + data.h_muro / data.incl_trasdos
    e_media_alzado = (data.e_coronacion + e_base_alzado) / 2

    peso_alzado  = 25.0 * e_media_alzado * data.h_muro
    peso_zapata  = 25.0 * b_zapata * h_zapata
    peso_relleno = data.gamma_relleno * data.talon * data.h_muro

    x_alzado  = data.puntera + e_media_alzado / 2
    x_zapata  = b_zapata / 2
    x_relleno = data.puntera + data.e_coronacion + data.talon / 2

    def _estabilidad(con_sc: bool) -> tuple[List[CheckResult], bool]:
        sc_v = data.sc * b_zapata if con_sc else 0.0
        V    = peso_alzado + peso_zapata + peso_relleno + sc_v + data.carga_v

        M_est = (
            peso_alzado  * x_alzado  +
            peso_zapata  * x_zapata  +
            peso_relleno * x_relleno +
            sc_v         * (b_zapata / 2) +
            data.carga_v * (data.puntera + data.e_coronacion / 2)
        )

        H_act = Ea_base + (Esc_base if con_sc else 0.0) + data.carga_h
        M_des = (
            Ea_base  * data.h_muro / 3 +
            (Esc_base * data.h_muro / 2 if con_sc else 0.0) +
            data.carga_h * data.h_muro +
            data.momento
        )

        checks = []

        # Deslizamiento
        mu   = math.tan(math.radians(data.phi_terreno))
        FS_d = (mu * V) / H_act if H_act > 0 else 99.0
        checks.append(CheckResult(
            description="Seguridad al Deslizamiento",
            status=FS_d >= data.fs_desliz_est,
            value=round(FS_d, 3), limit=data.fs_desliz_est, unit="FS",
            ratio=round(FS_d / data.fs_desliz_est, 3),
            reference="EC7 §6.5.3",
        ))

        # Vuelco
        FS_v = M_est / M_des if M_des > 0 else 99.0
        checks.append(CheckResult(
            description="Seguridad al Vuelco",
            status=FS_v >= data.fs_vuelco_est,
            value=round(FS_v, 3), limit=data.fs_vuelco_est, unit="FS",
            ratio=round(FS_v / data.fs_vuelco_est, 3),
            reference="EC7 §6.5.4",
        ))

        # Tensión en terreno
        M_net = M_est - M_des
        ecc   = abs(b_zapata / 2 - M_net / V) if V > 0 else 0.0

        if ecc <= b_zapata / 6:
            sigma_max = (V / b_zapata) * (1 + 6 * ecc / b_zapata)
            pct_comp  = 100.0
        else:
            a         = 3 * (b_zapata / 2 - ecc)
            sigma_max = 2 * V / (3 * a) if a > 0 else 0.0
            pct_comp  = (a / b_zapata) * 100

        sig_kgcm2 = sigma_max / 10.0
        checks.append(CheckResult(
            description="Tensión máx. en terreno",
            status=sig_kgcm2 <= data.sigma_adm_est,
            value=round(sig_kgcm2, 3), limit=data.sigma_adm_est, unit="kg/cm²",
            ratio=round(sig_kgcm2 / data.sigma_adm_est, 3),
            reference="EC7 §6.5.2",
        ))

        # % zapata comprimida
        checks.append(CheckResult(
            description="Zapata comprimida",
            status=pct_comp >= data.pct_comprimido,
            value=round(pct_comp, 1), limit=data.pct_comprimido, unit="%",
            ratio=round(pct_comp / data.pct_comprimido, 3) if data.pct_comprimido > 0 else 1.0,
        ))

        return checks, all(c.status for c in checks)

    checks_sc,   ok_sc   = _estabilidad(con_sc=True)
    checks_nosc, ok_nosc = _estabilidad(con_sc=False)

    scenarios = {
        "Estático (con SC)": ScenarioResult(label="Estático (con SC)", checks=checks_sc,   is_ok=ok_sc),
        "Estático (sin SC)": ScenarioResult(label="Estático (sin SC)", checks=checks_nosc, is_ok=ok_nosc),
    }

    # ── 5. Mediciones ──────────────────────────────────────────────────────
    vol_alz  = e_media_alzado * data.h_muro
    vol_zap  = b_zapata * h_zapata
    kg_acero = (vol_alz + vol_zap) * 80.0
    p_horm, p_acero = 85.0, 0.90

    measurements = MeasurementResult(
        lines=[
            MeasurementLine(description="Hormigón alzado",
                quantity=round(vol_alz, 3), unit="m³/m",
                unit_price=p_horm, total=round(vol_alz * p_horm, 2)),
            MeasurementLine(description="Hormigón zapata",
                quantity=round(vol_zap, 3), unit="m³/m",
                unit_price=p_horm, total=round(vol_zap * p_horm, 2)),
            MeasurementLine(description="Acero (estimación 80 kg/m³)",
                quantity=round(kg_acero, 1), unit="kg/m",
                unit_price=p_acero, total=round(kg_acero * p_acero, 2)),
        ],
        grand_total=round((vol_alz + vol_zap) * p_horm + kg_acero * p_acero, 2),
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
            "Se han usado γ y φ del relleno para el terreno de apoyo."
        )
    if Ka > 0.40:
        warnings.append(
            f"Ka = {Ka:.3f} elevado. Verificar el ángulo de fricción del relleno."
        )
    if b_zapata < data.h_muro * 0.4:
        warnings.append(
            f"Zapata estrecha (B/H = {b_zapata / data.h_muro:.2f} < 0.4). Riesgo de vuelco."
        )

    # ── 7. Respuesta ───────────────────────────────────────────────────────
    global_ok = ok_sc and ok_nosc

    return SolverResponse(
        is_ok=global_ok,
        summary=(
            f"Muro H={data.h_muro} m · B={b_zapata:.2f} m · "
            f"Ka={Ka:.3f} · {data.hormigon} / {data.acero}"
        ),
        checks=checks_sc,
        scenarios=scenarios,
        intermediate_tables=[tabla_empujes],
        material_results=material_results,
        measurements=measurements,
        warnings=warnings,
        form_data_updates=intermedios,  # ← ka_val, kp_val, b_zapata, geo_status
    )
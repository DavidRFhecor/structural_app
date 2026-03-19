import pytest
from structural_app.forms.muro.dto import MuroDTO
from structural_app.forms.muro.adapter import calculate_element

@pytest.mark.asyncio
async def test_muro_stability_logic():
    """Verifica que el adaptador devuelve ratios de vuelco correctos."""
    # 1. Caso de prueba extraído del Excel histórico
    input_data = {
        "h_muro": 4.0, "e_superior": 0.3, "e_inferior": 0.4,
        "b_zapata": 2.5, "c_puntera": 0.8, "h_zapata": 0.6
    }
    dto = MuroDTO(**input_data)
    
    # 2. Ejecutar cálculo a través del adaptador
    response = await calculate_element(dto)
    
    # 3. Validaciones de integridad
    assert response.is_ok is True
    assert len(response.checks) > 0
    # Verificamos que el ratio de vuelco sea el esperado (valor del Excel)
    vuelco_check = next(c for c in response.checks if "Vuelco" in c.description)
    assert 0.40 <= vuelco_check.ratio <= 0.60
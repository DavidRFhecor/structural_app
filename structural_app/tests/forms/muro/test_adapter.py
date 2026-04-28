import pytest
from structural_app.forms.muro.adapter import calculate_element

@pytest.mark.asyncio
async def test_muro_stability_logic():
    """Verifica que el adaptador procesa correctamente el diccionario de datos."""
    
    # 1. Caso de prueba con diccionario directo (Sin usar DTOs)
    input_data = {
        "h_muro": 4.0, "e_superior": 0.3, "e_inferior": 0.4,
        "b_zapata": 2.5, "c_puntera": 0.8, "h_zapata": 0.6,
        "diametro": 500.0, "recubrimiento": 40.0, "ved": 150.0, "fck": 30.0 # Parámetros requeridos por tu adaptador actual
    }
    
    # 2. Ejecutar cálculo a través del adaptador pasándole el diccionario
    response = calculate_element(**input_data)
    
    # 3. Validaciones de integridad
    assert response.is_ok is True
    assert len(response.checks) > 0
    
    # Verificamos que se haya generado correctamente el check de cortante
    cortante_check = next(c for c in response.checks if "Cortante" in c.description)
    assert cortante_check is not None
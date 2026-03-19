from pydantic import field_validator

class StructuralValidators:
    @staticmethod
    def must_be_positive(value: float, info):
        if value <= 0:
            raise ValueError(f"{info.field_name} debe ser mayor que cero.")
        return value

    @staticmethod
    def validate_fck(value: float):
        if value < 12 or value > 100:
            raise ValueError("fck fuera de rango normativo (12-100 MPa).")
        return value
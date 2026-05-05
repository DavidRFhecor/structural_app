"""
form_renderer.py  →  structural_app/shared/components/form_renderer.py
=======================================================================
Renderer con soporte para: number, select, toggle, derived, data_table.
Usa config.has_tabs (bool declarado en FormConfig) en lugar de .get("tabs")
para evitar el VarAttributeError de Reflex.
"""
import reflex as rx
from structural_app.core.base_state import BaseState
from structural_app.shared.components.data_table import custom_data_table


# ============================================================================
# Estilos compartidos (estilo hoja técnica de cálculo)
# ============================================================================
SECTION_HEADER_STYLE = {
    "background": "rgb(0, 50, 100)",
    "color": "white",
    "padding": "4px 12px",
    "font_size": "12px",
    "font_weight": "600",
    "letter_spacing": "0.04em",
    "width": "100%",
}

ROW_BORDER = "1px solid var(--gray-4)"

SYMBOL_STYLE = {
    "color": "var(--blue-11)",
    "font_style": "italic",
    "font_size": "13px",
    "min_width": "28px",
    "text_align": "center",
    "font_family": "'Georgia', 'Times New Roman', serif",
}

LABEL_STYLE = {
    "font_size": "12px",
    "color": "var(--gray-12)",
    "flex": "1",
    "line_height": "1.3",
}

VALUE_STYLE = {
    "min_width": "90px",
    "max_width": "110px",
    "style": {"font_size": "12px", "font_family": "'Courier New', monospace"},
}

UNIT_STYLE = {
    "font_size": "11px",
    "color": "var(--gray-9)",
    "min_width": "44px",
    "text_align": "left",
}

DERIVED_STYLE = {
    "font_size": "12px",
    "color": "var(--blue-11)",
    "font_weight": "600",
    "min_width": "90px",
    "max_width": "110px",
    "text_align": "right",
    "background": "var(--blue-2)",
    "border_radius": "4px",
    "padding": "2px 6px",
}


# ============================================================================
# Renderizadores por tipo de campo
# ============================================================================

def _dots_spacer() -> rx.Component:
    return rx.box(
        border_bottom="1px dotted var(--gray-5)",
        flex="1",
        margin_bottom="4px",
        min_width="8px",
    )


def _field_row_number(field: rx.Var, state_ptr) -> rx.Component:
    # f.id es un Var de Reflex, usamos .to(str) para la clave del diccionario
    val = state_ptr.form_data[field.id.to(str)] 
    
    return rx.hstack(
        rx.text(field.symbol, **SYMBOL_STYLE), # Acceso con punto
        rx.text(field.label, **LABEL_STYLE),
        _dots_spacer(),
        rx.input(
            value=val.to(str), 
            on_change=lambda v: state_ptr.set_value(field.id, v),
            variant="surface",
            size="1",
            **VALUE_STYLE,
        ),
        rx.text(field.unit, **UNIT_STYLE),
        width="100%", align="center", padding_y="3px", border_bottom=ROW_BORDER, spacing="2",
    )

def _field_row_select(field: rx.Var, state_ptr) -> rx.Component:
    val = state_ptr.form_data[field["id"].to(str)]
    return rx.hstack(
        rx.text(field["symbol"], **SYMBOL_STYLE),
        rx.text(field["label"], **LABEL_STYLE),
        _dots_spacer(),
        rx.select.root(
            rx.select.trigger(
                style={"min_width": "100px", "font_size": "12px"},
            ),
            rx.select.content(
                rx.foreach(
                    field["options"],
                    lambda opt: rx.select.item(opt["label"], value=opt["value"]),
                ),
            ),
            value=val,
            on_change=lambda v: state_ptr.set_select_value(field["id"], v),
        ),
        rx.text(field["unit"], **UNIT_STYLE),
        width="100%",
        align="center",
        padding_y="3px",
        border_bottom=ROW_BORDER,
        spacing="2",
    )


def _field_row_toggle(field: rx.Var, state_ptr) -> rx.Component:
    val = state_ptr.form_data[field["id"].to(str)]
    return rx.hstack(
        rx.text(field["symbol"], **SYMBOL_STYLE),
        rx.text(field["label"], **LABEL_STYLE),
        _dots_spacer(),
        rx.hstack(
            rx.cond(
                val,
                rx.text("SÍ", size="1", weight="bold", color_scheme="blue"),
                rx.text("NO", size="1", color_scheme="gray"),
            ),
            rx.switch(
                checked=val,
                on_change=lambda v: state_ptr.set_toggle_value(field["id"], v),
                size="1",
            ),
            spacing="2",
            align="center",
        ),
        rx.text("", **UNIT_STYLE),
        width="100%",
        align="center",
        padding_y="3px",
        border_bottom=ROW_BORDER,
        spacing="2",
    )


def _field_row_derived(field: rx.Var, state_ptr) -> rx.Component:
    return rx.hstack(
        rx.text(field["symbol"], **SYMBOL_STYLE),
        rx.text(field["label"], **LABEL_STYLE),
        _dots_spacer(),
        rx.text("—", **DERIVED_STYLE),
        rx.text(field["unit"], **UNIT_STYLE),
        width="100%",
        align="center",
        padding_y="3px",
        border_bottom=ROW_BORDER,
        spacing="2",
    )


def _field_row(field: rx.Var, state_ptr) -> rx.Component:
    """Dispatcher por tipo usando el atributo .type"""
    return rx.cond(
        field.type == "select",
        _field_row_select(field, state_ptr),
        rx.cond(
            field.type == "toggle",
            _field_row_toggle(field, state_ptr),
            rx.cond(
                field.type == "derived",
                _field_row_derived(field, state_ptr),
                _field_row_number(field, state_ptr),
            ),
        ),
    )


# ============================================================================
# Grupo de campos (sección con cabecera azul oscuro)
# ============================================================================

def _render_group(group: rx.Var, state_ptr) -> rx.Component:
    return rx.vstack(
        rx.box(rx.text(group.name, **SECTION_HEADER_STYLE), width="100%"),
        rx.vstack(
            # AQUÍ SE SOLUCIONA EL ERROR: Reflex ahora sabe que .fields es una List
            rx.foreach(group.fields, lambda f: _field_row(f, state_ptr)),
            width="100%", spacing="0", padding_x="2", padding_bottom="2",
        ),
        width="100%", spacing="0", border="1px solid var(--gray-5)", border_radius="4px", overflow="hidden", mb="3",
    )


# ============================================================================
# Tabla editable
# ============================================================================

def _render_data_table(element: rx.Var, state_ptr) -> rx.Component:
    table_id = element["id"].to(str) 
    
    return rx.vstack(
        rx.box(rx.text(element["title"], **SECTION_HEADER_STYLE), width="100%"),
        rx.box(
            custom_data_table(
                matrix_data=state_ptr.form_data[table_id],
                columns=element["columns"],
                # CASTING EXPLÍCITO: Convertimos a lista para que Reflex reconozca .length()
                rows=element["default_rows"].to(list).length(), 
                on_edit_fn=lambda pos, val: state_ptr.update_table_cell(table_id, pos, val),
            ),
            padding="2",
        ),
        width="100%",
        spacing="0",
        border="1px solid var(--gray-5)",
        border_radius="4px",
        overflow="hidden",
        mb="3",
    )

# ============================================================================
# Elemento genérico: grupo O tabla según su tipo
# ============================================================================

def _render_element(element: rx.Var, state_ptr) -> rx.Component:
    return rx.cond(
        element.type == "data_table",
        _render_data_table(element, state_ptr),
        _render_group(element, state_ptr),
    )


# ============================================================================
# Contenido de una pestaña
# ============================================================================

def _render_tab_content(tab: rx.Var, state_ptr) -> rx.Component:
    return rx.vstack(
        # Especificamos que 'tab.groups' contiene diccionarios (Dict)
        rx.foreach(tab.groups, lambda g: _render_element(g, state_ptr)), 
        width="100%",
        align_items="stretch",
        padding_top="3",
    )


# ============================================================================
# Cabecera del formulario
# ============================================================================

def render_form_header(config: rx.Var) -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.heading(config.title, size="6", color="rgb(0,50,100)"), # <-- CORRECCIÓN
            rx.cond(
                config.extended_info, # <-- CORRECCIÓN
                rx.icon(
                    "info", size=18, color="var(--blue-9)",
                    cursor="pointer", on_click=BaseState.toggle_theory,
                    style={"_hover": {"opacity": 0.7}},
                ),
                rx.cond(
                    config.references.length() > 0, # <-- CORRECCIÓN
                    rx.icon(
                        "info", size=18, color="var(--blue-9)",
                        cursor="pointer", on_click=BaseState.toggle_theory,
                        style={"_hover": {"opacity": 0.7}},
                    ),
                    rx.box(),
                ),
            ),
            align="center",
            spacing="3",
        ),
        rx.divider(),
        width="100%",
        mb="3",
    )


# ============================================================================
# render_dynamic_form — punto de entrada principal
# Usa config.has_tabs (bool declarado en FormConfig) en lugar de .get("tabs")
# ============================================================================

def render_dynamic_form(config: rx.Var, state_ptr) -> rx.Component:
    tabs_ui = rx.tabs.root(
        rx.tabs.list(
            rx.foreach(
                config.tabs,
                # 'tab' es de clase FormTab, pero para Reflex es un Var
                lambda tab: rx.tabs.trigger(
                    tab.label, 
                    value=tab.id, 
                    style={"font_size": "12px", "padding": "6px 12px"},
                ),
            ),
            style={"border_bottom": "2px solid rgb(0,50,100)"},
        ),
        rx.foreach(
            config.tabs,
            lambda tab: rx.tabs.content(
                _render_tab_content(tab, state_ptr),
                value=tab.id,
            ),
        ),
        width="100%",
    )

    legacy_ui = rx.vstack(
        rx.foreach(
            config.groups, # <-- CORRECCIÓN
            lambda element: _render_element(element, state_ptr),
        ),
        width="100%",
        align_items="stretch",
    )

    return rx.vstack(
        render_form_header(config),
        rx.cond(config.has_tabs, tabs_ui, legacy_ui), # <-- CORRECCIÓN
        rx.button(
            rx.hstack(
                rx.icon("calculator", size=16),
                rx.text("CALCULAR"),
                spacing="2",
                align="center",
            ),
            on_click=state_ptr.calculate,
            loading=state_ptr.is_calculating,
            width="100%",
            size="2",
            style={
                "background": "rgb(0,50,100)",
                "color": "white",
                "font_weight": "700",
                "letter_spacing": "0.08em",
                "margin_top": "8px",
                "border_radius": "4px",
                "_hover": {"background": "rgb(0,70,140)"},
            },
        ),
        width="100%",
        spacing="0",
    )


# ============================================================================
# Alias de compatibilidad (por si otros módulos los importan)
# ============================================================================

def render_field(field: rx.Var, state_ptr):
    return _field_row(field, state_ptr)

def render_group(group: rx.Var, state_ptr):
    return _render_group(group, state_ptr)

def render_element(element, state_ptr):
    if isinstance(element, dict) and element.get("type") == "data_table":
        table_id = element["id"]
        cols = [{"title": c["title"], "type": "float"} for c in element["columns"]]
        return rx.box(
            rx.heading(element["title"], size="3", margin_bottom="0.5em"),
            custom_data_table(
                matrix_data=state_ptr.form_data[table_id],
                columns=cols,
                on_edit_fn=lambda pos, val: state_ptr.update_table_cell(table_id, pos, val),
            ),
            padding="1em",
            border="1px solid var(--gray-5)",
            border_radius="4px",
        )
    return _render_group(element, state_ptr)

def render_form_tabs(config: dict) -> rx.Component:
    tabs = config.get("tabs", [])
    return rx.tabs.root(
        rx.tabs.list(*[rx.tabs.trigger(t["label"], value=t["id"]) for t in tabs]),
        *[rx.tabs.content(
            rx.vstack(*[render_element(g, BaseState) for g in t.get("groups", [])], width="100%"),
            value=t["id"],
        ) for t in tabs],
        default_value=tabs[0]["id"] if tabs else "",
        width="100%",
    )
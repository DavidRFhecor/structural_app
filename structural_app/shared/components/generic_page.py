import reflex as rx

from structural_app.core.base_state import BaseState
from structural_app.shared.components.layout import main_layout
from structural_app.shared.components.generic_page_standard import standard_page_content
from structural_app.shared.components.generic_page_split_tabs import split_tabs_page_content


def generic_form_page() -> rx.Component:
    config = BaseState.active_form_config

    return main_layout(
        rx.cond(
            # Cambiamos la condición para que sea más flexible
            (config.page_layout.type == "split_tabs") | (config.has_tabs),
            split_tabs_page_content(config),
            standard_page_content(config),
        ),
        state_class=BaseState,
    )
import reflex as rx
from reflex.state import BaseState


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _ratio_bar(ratio: rx.Var) -> rx.Component:
    pct = (ratio * 100).to(str) + "%"
    color = rx.cond(ratio >= 1.0, "var(--green-9)", "var(--red-9)")
    return rx.box(
        rx.box(
            height="4px",
            width=pct,
            background=color,
            border_radius="full",
            transition="width 0.3s ease",
        ),
        width="100%",
        background="var(--gray-4)",
        border_radius="full",
        overflow="hidden",
        mt="1",
    )


# ---------------------------------------------------------------------------
# check_card
# ---------------------------------------------------------------------------
def check_card(check: rx.Var) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text(check.description, size="2", weight="bold"),
                    rx.hstack(
                        rx.text(
                            check.value.to(str) + " " + check.unit,
                            size="4",
                            weight="bold",
                        ),
                        rx.text(
                            "/ " + check.limit.to(str),
                            size="2",
                            color_scheme="gray",
                        ),
                        align="baseline",
                        spacing="1",
                    ),
                    rx.cond(
                        check.reference != "",
                        rx.text(check.reference, size="1", color_scheme="gray"),
                        rx.box(),
                    ),
                    align_items="start",
                    spacing="1",
                ),
                rx.spacer(),
                rx.badge(
                    rx.cond(check.status, "CUMPLE", "NO CUMPLE"),
                    color_scheme=rx.cond(check.status, "green", "red"),
                    variant="solid",
                    size="2",
                ),
                width="100%",
                align="center",
            ),
            rx.cond(
                check.ratio > 0.0,
                _ratio_bar(check.ratio),
                rx.box(),
            ),
            width="100%",
            spacing="1",
        ),
        width="100%",
        variant="surface",
    )


# ---------------------------------------------------------------------------
# scenario_panel
# ---------------------------------------------------------------------------
def scenario_panel(label: rx.Var, scenario: rx.Var) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.text(label, size="3", weight="bold"),
                rx.spacer(),
                rx.badge(
                    rx.cond(scenario.is_ok, "OK", "FALLA"),
                    color_scheme=rx.cond(scenario.is_ok, "green", "red"),
                    variant="soft",
                ),
                width="100%",
                align="center",
            ),
            rx.foreach(scenario.checks, check_card),
            width="100%",
            spacing="2",
        ),
        width="100%",
        variant="surface",
        style={"border": rx.cond(
            scenario.is_ok,
            "1px solid var(--green-6)",
            "1px solid var(--red-6)",
        )},
    )


# ---------------------------------------------------------------------------
# intermediate_table_view
# ---------------------------------------------------------------------------
def intermediate_table_view(table: rx.Var) -> rx.Component:
    return rx.vstack(
        rx.text(table.title, size="3", weight="bold", mt="4"),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.foreach(
                        table.columns,
                        lambda col: rx.table.column_header_cell(
                            rx.cond(
                                col.unit != "",
                                col.label + " (" + col.unit + ")",
                                col.label,
                            ),
                            font_weight=rx.cond(col.highlight, "bold", "normal"),
                            color=rx.cond(col.highlight, "var(--blue-11)", "inherit"),
                        ),
                    ),
                ),
            ),
            rx.table.body(
                rx.foreach(
                    table.rows,
                    lambda row: rx.table.row(
                        rx.foreach(
                            table.columns,
                            lambda col: rx.table.cell(
                                row[col.id].to(str),
                                font_weight=rx.cond(col.highlight, "bold", "normal"),
                            ),
                        ),
                    ),
                ),
            ),
            variant="surface",
            width="100%",
        ),
        rx.cond(
            table.note != "",
            rx.text(table.note, size="1", color_scheme="gray", font_style="italic"),
            rx.box(),
        ),
        width="100%",
        spacing="2",
    )


# ---------------------------------------------------------------------------
# material_results_view
# ---------------------------------------------------------------------------
def material_results_view(mat: rx.Var) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.text("Propiedades de Materiales", size="3", weight="bold"),
            rx.table.root(
                rx.table.body(
                    rx.foreach(
                        mat["items"],
                        lambda item: rx.table.row(
                            rx.table.cell(rx.text(item["label"], weight="bold", size="2")),
                            rx.table.cell(rx.text(item["value"].to(str) + " " + item["unit"], size="2")),
                            rx.table.cell(rx.text(item["formula"], size="1", color_scheme="gray")),
                        ),
                    ),
                ),
                variant="ghost",
                width="100%",
            ),
            width="100%",
            spacing="2",
        ),
        width="100%",
        variant="surface",
    )

# ---------------------------------------------------------------------------
# measurements_view
# ---------------------------------------------------------------------------
def measurements_view(meas: rx.Var) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.text("Mediciones y Precios", size="3", weight="bold"),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Descripción"),
                        rx.table.column_header_cell("Cantidad"),
                        rx.table.column_header_cell("Ud."),
                        rx.table.column_header_cell("P. Unit."),
                        rx.table.column_header_cell("Total"),
                    ),
                ),
                rx.table.body(
                    rx.foreach(
                        meas.lines,
                        lambda line: rx.table.row(
                            rx.table.cell(line.description),
                            rx.table.cell(line.quantity.to(str)),
                            rx.table.cell(line.unit),
                            rx.table.cell(line.unit_price.to(str) + " " + meas.currency),
                            rx.table.cell(
                                line.total.to(str) + " " + meas.currency,
                                font_weight="bold",
                            ),
                        ),
                    ),
                ),
            ),
            rx.hstack(
                rx.spacer(),
                rx.text("TOTAL: ", weight="bold", size="3"),
                rx.text(
                    meas.grand_total.to(str) + " " + meas.currency,
                    weight="bold", size="3", color_scheme="blue",
                ),
            ),
            width="100%",
            spacing="2",
        ),
        width="100%",
        variant="surface",
    )


# ---------------------------------------------------------------------------
# results_panel — punto de entrada principal
# ---------------------------------------------------------------------------
def results_panel(state: any) -> rx.Component:
    res = state.results

    return rx.vstack(
        rx.heading("Resultados del Cálculo", size="6", color="rgb(0, 50, 100)", mb="2"),

        rx.cond(
            res,
            rx.vstack(

                # 1. Resumen
                rx.callout(
                    res.summary,
                    icon="info",
                    color_scheme=rx.cond(res.is_ok, "blue", "red"),
                    width="100%",
                ),

                # 2. Avisos — usando len() en lugar de .length()
                rx.cond(
                    res.warnings.length() > 0,
                    rx.vstack(
                        rx.foreach(
                            res.warnings,
                            lambda w: rx.callout(
                                w,
                                icon="triangle_alert",
                                color_scheme="yellow",
                                width="100%",
                            ),
                        ),
                        width="100%",
                        spacing="2",
                    ),
                    rx.box(),
                ),

                # 3. Materiales derivados
                rx.cond(
                    res.material_results,
                    material_results_view(res.material_results),
                    rx.box(),
                ),

                # 4a. Escenarios
                rx.cond(
                    res.scenarios.length() > 0,
                    rx.vstack(
                        rx.text("Comprobaciones por Escenario", size="3", weight="bold", mt="4"),
                        rx.foreach(
                            
                            res.scenarios.values(), 
                            lambda scenario: scenario_panel(scenario.label, scenario),
                        ),
                        width="100%",
                        spacing="3",
                    ),
                    # 4b. Checks planos (legacy)
                    rx.vstack(
                        rx.text("Comprobaciones Normativas", size="3", weight="bold", mt="4"),
                        rx.foreach(res.checks, check_card),
                        width="100%",
                        spacing="2",
                    ),
                ),

                # 5. Tablas intermedias
                rx.cond(
                    res.intermediate_tables.length() > 0,
                    rx.vstack(
                        rx.foreach(res.intermediate_tables, intermediate_table_view),
                        width="100%",
                        spacing="3",
                    ),
                    rx.box(),
                ),

                # 6. Mediciones
                rx.cond(
                    res.measurements,
                    measurements_view(res.measurements),
                    rx.box(),
                ),

                # 7. Gráfico Plotly (comportamiento original)
                rx.cond(
                    res.plot_data,
                    rx.vstack(
                        rx.text("Visualización y Diagramas", size="3", weight="bold", mt="6"),
                        rx.plotly(data=state.plot_fig, width="100%", height="400px"),
                        width="100%",
                    ),
                    rx.box(),
                ),

                width="100%",
                align_items="start",
                spacing="3",
            ),

            # Estado vacío
            rx.center(
                rx.vstack(
                    rx.icon("calculator", size=40, color="var(--gray-8)"),
                    rx.text("Introduce los datos y pulsa 'Calcular'.", color_scheme="gray"),
                    align="center",
                    padding="10",
                    border="2px dashed var(--gray-4)",
                    border_radius="xl",
                    width="100%",
                ),
                width="100%",
            ),
        ),

        width="100%",
        spacing="4",
    )
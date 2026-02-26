import reflex as rx
from .ui.dashboard import dashboard_view
from .state import State

def index() -> rx.Component:
    """The main entry page of the Ghost Browser."""
    return rx.box(
        dashboard_view(),
        # ARCHITECT FIX: Version Bump
        rx.box(
            rx.text("v2.1.0 - Fullscreen Expansion", font_size="xs", color="gray", font_family="monospace"),
            position="fixed",
            bottom="0",
            left="0",
            width="100%",
            background_color="rgba(15, 15, 20, 0.95)",
            border_top="1px solid #333",
            padding="4px",
            text_align="center",
            z_index="9999"
        ),
        position="relative",
        min_height="100vh"
    )


app = rx.App(
    theme=rx.theme(
        appearance="dark", 
        has_background=True, 
        radius="large", 
        accent_color="iris"
    ),
)
app.add_page(index, title="Ghost Browser | Private Hub", on_load=State.on_load)
import reflex as rx
from .ui.dashboard import dashboard_view
from .state import State

def index() -> rx.Component:
    """The main entry page of the Ghost Browser."""
    return rx.fragment(
        # The overlapping floating button has been removed from here.
        dashboard_view(),
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

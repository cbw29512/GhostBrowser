import reflex as rx
from ..state import State

def ghost_card(title: str, url: str):
    """Component for individual site cards."""
    return rx.card(
        rx.vstack(
            rx.heading(title, size="4"),
            rx.text(url, size="1", color_secondary="gray"),
            rx.button(
                "Launch Ghost",
                on_click=lambda: State.launch_ghost_session(url),
                width="100%",
                variant="soft",
                color_scheme="iris"
            ),
            align="start",
            spacing="2",
        ),
        width="200px",
    )

def vault_header():
    """Top bar for vault status and authentication."""
    return rx.hstack(
        rx.heading("Ghost Hub", size="7"),
        rx.spacer(),
        rx.cond(
            State.is_vault_unlocked,
            rx.badge("Vault Unlocked", color_scheme="green", variant="solid"),
            rx.hstack(
                rx.input(
                    placeholder="Enter Master Password",
                    type="password",
                    on_change=State.set_master_password_input,
                ),
                rx.button("Unlock", on_click=State.unlock_vault),
            )
        ),
        width="100%",
        padding="1em",
        border_bottom="1px solid #333",
    )

def dashboard_view():
    """Main landing view after login."""
    return rx.vstack(
        vault_header(),
        rx.flex(
            ghost_card("Search", "https://duckduckgo.com"),
            ghost_card("Bank", "https://chase.com"),
            ghost_card("Mail", "https://proton.me"),
            flex_wrap="wrap",
            spacing="4",
            padding="2em",
        ),
        width="100%",
    )

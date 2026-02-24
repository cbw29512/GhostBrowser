import reflex as rx
from ..state import State

def ghost_card(title: str, url: str):
    return rx.card(
        rx.vstack(
            rx.heading(title, size="4"),
            rx.text(url, size="1", color="gray"),
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
        width="250px",
    )

def add_site_modal():
    """Dialog for adding new Ghost Cards."""
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(rx.icon(tag="plus"), "Add Site", variant="solid", color_scheme="iris"),
        ),
        rx.dialog.content(
            rx.dialog.title("Add New Ghost Site"),
            rx.vstack(
                rx.text("Enter the details for the anonymous session:"),
                rx.input(placeholder="Site Name (e.g. My Bank)", width="100%"),
                rx.input(placeholder="Target URL (https://...)", width="100%"),
                rx.hstack(
                    rx.dialog.close(rx.button("Cancel", variant="soft", color_scheme="gray")),
                    rx.dialog.close(rx.button("Save Card", color_scheme="iris")),
                    width="100%",
                    justify="end",
                ),
                spacing="4",
            ),
        ),
    )

def browser_portal():
    return rx.vstack(
        rx.hstack(
            rx.badge("LIVE SESSION", color_scheme="red", variant="outline"),
            rx.spacer(),
            rx.button("Kill Session & Wipe RAM", on_click=State.terminate_session, color_scheme="red"),
            width="100%",
        ),
        rx.html(f'<iframe src="{State.browser_url}" style="width:100%; height:80vh; border:none; border-radius:10px;"></iframe>'),
        width="100%",
    )

def dashboard_view():
    return rx.vstack(
        rx.hstack(
            rx.heading("Ghost Hub", size="7"),
            rx.spacer(),
            rx.cond(State.is_vault_unlocked, add_site_modal(), rx.text("")),
            rx.cond(
                State.is_vault_unlocked,
                rx.badge("Vault Unlocked", color_scheme="green", variant="solid"),
                rx.hstack(
                    rx.input(placeholder="Password", type="password", on_change=State.set_master_password_input),
                    rx.button("Unlock", on_click=State.unlock_vault),
                )
            ),
            width="100%",
            padding="1em",
        ),
        rx.cond(
            State.is_browser_running,
            browser_portal(),
            rx.flex(
                ghost_card("Search", "https://duckduckgo.com"),
                ghost_card("Bank", "https://chase.com"),
                flex_wrap="wrap",
                spacing="4",
                padding="2em",
            ),
        ),
        width="100%",
    )

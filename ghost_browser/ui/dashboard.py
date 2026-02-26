import reflex as rx
from ..state import State

COMMON_URLS = [
    "https://www.youtube.com", "https://www.chase.com",
    "https://www.google.com", "https://www.amazon.com",
    "https://www.reddit.com", "https://www.netflix.com",
    "https://www.proton.me", "https://www.bankofamerica.com"
]

def pii_vault_drawer():
    return rx.drawer.root(
        rx.drawer.trigger(rx.button(rx.icon("user"), "Global PII Vault", variant="soft", color_scheme="orange")),
        rx.drawer.overlay(z_index="5"),
        rx.drawer.portal(
            rx.drawer.content(
                rx.vstack(
                    rx.hstack(
                        rx.heading("Global Identity Vault", size="6"),
                        rx.spacer(),
                        rx.drawer.close(rx.icon_button(rx.icon("x"), variant="ghost", color_scheme="gray")),
                        width="100%"
                    ),
                    rx.text("Auto-fill data. AES-128 Fernet encrypted on disk.", color="gray"),
                    rx.divider(),
                    rx.scroll_area(
                        rx.vstack(
                            rx.input(placeholder="Full Name", on_change=State.set_pii_name, width="100%"),
                            rx.input(placeholder="Email Address", on_change=State.set_pii_email, width="100%"),
                            rx.input(placeholder="Phone Number", on_change=State.set_pii_phone, width="100%"),
                            rx.input(placeholder="Street Address", on_change=State.set_pii_address, width="100%"),
                            rx.hstack(
                                rx.input(placeholder="City", on_change=State.set_pii_city, width="50%"),
                                rx.input(placeholder="State", on_change=State.set_pii_state, width="25%"),
                                rx.input(placeholder="Zip", on_change=State.set_pii_zip, width="25%"),
                                width="100%"
                            ),
                            rx.input(placeholder="Credit Card Number", on_change=State.set_pii_cc, width="100%", type="password"),
                            width="100%", spacing="3"
                        ),
                        height="400px", type="always", scrollbars="vertical", width="100%"
                    ),
                    rx.drawer.close(rx.button("Encrypt & Save Identity", on_click=State.save_pii, width="100%", color_scheme="orange")),
                    align="start", width="100%", spacing="4"
                ),
                top="auto", right="0", height="100%", width="400px",
                padding="2em", background_color="var(--gray-2)",
            )
        ),
        direction="right",
    )

def ghost_card(card: rx.Var):
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading(card.display_name, size="4"),
                rx.spacer(),
                rx.icon_button(
                    rx.icon("pencil"), size="1", variant="ghost", color_scheme="gray",
                    on_click=State.prepare_edit(card)
                ),
                rx.icon_button(
                    rx.icon("trash-2"), size="1", variant="ghost", color_scheme="red",
                    on_click=State.delete_card(card.id)
                ),
                width="100%"
            ),
            rx.text(card.target_url, size="1", color="gray"),
            rx.cond(
                card.authorize_pii,
                rx.badge(rx.icon("shield-check", size=12), "PII Authorized", color_scheme="orange", variant="soft"),
                rx.badge(rx.icon("shield-off", size=12), "PII Denied", color_scheme="gray", variant="outline")
            ),
            rx.button(
                "Launch Ghost",
                on_click=State.launch_ghost_session(card.target_url),
                width="100%", variant="soft", color_scheme="iris"
            ),
            align="start", spacing="2", width="100%"
        ),
        width="280px",
    )

def edit_site_modal():
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Edit Ghost Site"),
            rx.vstack(
                rx.input(value=State.edit_site_name, on_change=State.set_edit_site_name, width="100%"),
                rx.input(
                    value=State.edit_site_url, on_change=State.set_edit_site_url,
                    width="100%", custom_attrs={"list": "url-suggestions"}
                ),
                rx.checkbox(
                    "Authorize PII Injection",
                    checked=State.edit_authorize_pii,
                    on_change=State.set_edit_authorize_pii,
                    color_scheme="orange"
                ),
                rx.hstack(
                    rx.button("Cancel", variant="soft", color_scheme="gray", on_click=State.cancel_edit),
                    rx.button("Save Changes", on_click=State.save_edit, color_scheme="iris"),
                    width="100%", justify="end",
                ),
                spacing="4",
            ),
        ),
        open=State.is_edit_modal_open, on_open_change=State.set_is_edit_modal_open,
    )

def add_site_modal():
    return rx.dialog.root(
        rx.dialog.trigger(rx.button(rx.icon(tag="plus"), "Add Site", variant="solid", color_scheme="iris")),
        rx.dialog.content(
            rx.dialog.title("Add New Ghost Site"),
            rx.vstack(
                rx.input(placeholder="Site Name", on_change=State.set_new_site_name, width="100%"),
                rx.input(
                    placeholder="Select or Type URL...", on_change=State.set_new_site_url,
                    width="100%", custom_attrs={"list": "url-suggestions"}
                ),
                rx.html(
                    '<datalist id="url-suggestions">'
                    + ''.join([f'<option value="{u}"></option>' for u in COMMON_URLS])
                    + '</datalist>'
                ),
                rx.checkbox("Authorize PII Injection for this site", on_change=State.set_new_authorize_pii, color_scheme="orange"),
                rx.hstack(
                    rx.dialog.close(rx.button("Cancel", variant="soft", color_scheme="gray")),
                    rx.dialog.close(rx.button("Save Card", on_click=State.add_card, color_scheme="iris")),
                    width="100%", justify="end",
                ),
                spacing="4",
            ),
        ),
    )

def browser_portal():
    return rx.vstack(
        # ARCHITECT FIX: All secondary header bars and warnings deleted!
        # Only the raw iframe remains, stretched to 85vh.
        rx.box(
            rx.el.iframe(
                src=State.browser_url,
                style={
                    "width": "100%",
                    "height": "85vh",
                    "border": "none",
                    "border_radius": "8px",
                    "background_color": "#1a1a1a",
                }
            ),
            width="100%", height="85vh", border_radius="8px", overflow="hidden"
        ),
        width="100%",
    )

def loading_screen():
    return rx.center(
        rx.vstack(
            rx.spinner(size="3"),
            rx.heading("Provisioning Secure Enclave...", size="6"),
            rx.text("Allocating RAM disk, initializing isolated OS, and routing network...", color="gray"),
            align="center", spacing="5",
        ),
        width="100%", height="60vh"
    )

def setup_splash_screen():
    return rx.center(
        rx.card(
            rx.vstack(
                rx.icon("shield-plus", size=48, color="var(--iris-9)"),
                rx.heading("System Initialization", size="6"),
                rx.text("Create your Master Admin Profile to secure the vault.", color="gray", text_align="center"),
                rx.input(placeholder="Admin Username", on_change=State.set_setup_username, width="100%"),
                rx.input(placeholder="Master Password", type="password", on_change=State.set_setup_password, width="100%"),
                rx.input(placeholder="Confirm Password", type="password", on_change=State.set_setup_confirm, width="100%"),
                rx.text(
                    "Password must be 8+ chars, with an uppercase, lowercase, number, and special character.",
                    size="1", color="gray"
                ),
                rx.button("Initialize Vault", on_click=State.create_admin, color_scheme="iris", width="100%"),
                align="center", spacing="4", padding="2em"
            ),
            width="400px"
        ),
        width="100%", padding_top="10vh"
    )

def locked_splash_screen():
    return rx.center(
        rx.vstack(
            rx.icon("shield-alert", size=64, color="var(--gray-9)"),
            rx.heading("Vault Secured", size="6", color="var(--gray-11)"),
            rx.text("Identity Verification Required.", color="var(--gray-10)"),
            align="center", spacing="4", padding_top="15vh"
        ),
        width="100%"
    )

def main_dashboard():
    return rx.vstack(
        rx.cond(
            State.is_booting,
            loading_screen(),
            rx.cond(
                State.is_browser_running,
                browser_portal(),
                rx.cond(
                    State.site_cards,
                    rx.flex(rx.foreach(State.site_cards, ghost_card), flex_wrap="wrap", spacing="4", padding="2em"),
                    rx.center(
                        rx.button(rx.icon("download"), "Load Starter Cards", on_click=State.on_load, size="4", color_scheme="green"),
                        padding_top="10vh", width="100%"
                    )
                )
            )
        ),
        width="100%"
    )

def dashboard_view():
    return rx.vstack(
        edit_site_modal(),
        # --- DYNAMIC HEADER ---
        rx.hstack(
            rx.heading("Ghost Hub", size="7"),
            rx.spacer(),
            
            # ARCHITECT FIX: Moved the active session controls to the top bar!
            rx.cond(
                State.is_browser_running,
                rx.hstack(
                    rx.badge(rx.icon("shield-check", size=14), "Pinned: ", rx.text.strong(State.active_domain), color_scheme="orange", variant="solid"),
                    rx.button(rx.icon("external-link"), "Pop Out", variant="solid", color_scheme="blue", on_click=State.pop_out_session, cursor="pointer"),
                    rx.button("Kill Session", on_click=State.terminate_session, color_scheme="red"),
                    rx.divider(orientation="vertical", height="2em"),
                    spacing="4",
                    align_items="center",
                )
            ),

            rx.cond(
                State.has_admin & State.is_vault_unlocked,
                rx.hstack(
                    pii_vault_drawer(),
                    add_site_modal(),
                    rx.color_mode.button(),
                    rx.badge("Vault Unlocked", color_scheme="green"),
                    rx.button(rx.icon("lock"), "Lock Vault", on_click=State.lock_vault, color_scheme="red", variant="soft")
                ),
                rx.cond(
                    State.has_admin,
                    rx.hstack(
                        rx.color_mode.button(),
                        rx.input(placeholder="Username", on_change=State.set_login_username),
                        rx.input(
                            placeholder="Master Password", type="password",
                            value=State.master_password_input, on_change=State.set_master_password_input
                        ),
                        rx.button("Unlock", on_click=State.unlock_vault),
                    ),
                    rx.color_mode.button()
                )
            ),
            width="100%", padding="1em", border_bottom="1px solid var(--gray-4)", align_items="center",
        ),
        # --- DYNAMIC BODY ---
        rx.cond(
            State.has_admin,
            rx.cond(State.is_vault_unlocked, main_dashboard(), locked_splash_screen()),
            setup_splash_screen()
        ),
        width="100%",
    )
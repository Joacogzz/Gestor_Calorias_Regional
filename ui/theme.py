import flet as ft

# Colors - Semantic Material 3 Colors
PRIMARY = "primary"
SECONDARY = "secondary"
BACKGROUND = "background"
SURFACE = "surface"
SURFACE_VARIANT = "surfacevariant"
TEXT_PRIMARY = "onbackground"
TEXT_SECONDARY = "onsurfacevariant"
DANGER = "error"

# Card Style
def get_card_style():
    return {
        "bgcolor": SURFACE,
        "border_radius": 24,
        "padding": 25,
        "margin": ft.Margin(left=0, top=0, right=0, bottom=15),
        "shadow": ft.BoxShadow(blur_radius=10, color="#1A000000", offset=ft.Offset(0, 4)),
    }

# Input Style
def get_input_style(label, icon=None):
    return {
        "label": label,
        "border_color": PRIMARY,
        "cursor_color": PRIMARY,
        "color": TEXT_PRIMARY,
        "label_style": ft.TextStyle(color=TEXT_SECONDARY),
        "border_radius": 16,
        "prefix_icon": icon,
        "filled": True,
        "fill_color": SURFACE_VARIANT,
        "border": ft.InputBorder.NONE,
        "focused_border_width": 2,
        "content_padding": 16,
    }

# Button Style
def get_button_style():
    return ft.ButtonStyle(
        color="onprimary",
        bgcolor=PRIMARY,
        shape=ft.RoundedRectangleBorder(radius=16),
        padding=20,
    )

def get_secondary_button_style():
    return ft.ButtonStyle(
        color=PRIMARY,
        bgcolor=SURFACE_VARIANT,
        shape=ft.RoundedRectangleBorder(radius=16),
        padding=20,
    )

def header_text(text):
    return ft.Text(text, size=28, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY)

def subheader_text(text):
    return ft.Text(text, size=18, weight=ft.FontWeight.W_600, color=TEXT_SECONDARY)

def normal_text(text, color=TEXT_PRIMARY, size=14, weight=ft.FontWeight.NORMAL, expand=False):
    return ft.Text(text, size=size, color=color, weight=weight, expand=expand)

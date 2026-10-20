import flet as ft

# =====================================================================
# SISTEMA DE DISEÑO: PALETA "DEEP OBSIDIAN & EMERALD VITALITY"
# =====================================================================

# Superficies & Fondos (Obsidiana Profundo)
BG_OBSIDIAN = "#0D1117"
BG_OBSIDIAN_ALT = "#10141D"
SURFACE = "#161B26"
SURFACE_CARD = "#161B26"
SURFACE_VARIANT = "#1F2636"
SURFACE_ELEVATED = "#232B3C"
SURFACE_BORDER = "#262E3F"
SURFACE_BORDER_ACTIVE = "#3B475E"

# Acentos Principales: Esmeralda Vital / Menta Neón
PRIMARY = "#10B981"          # Emerald 500
PRIMARY_LIGHT = "#34D399"    # Mint 400
PRIMARY_DARK = "#059669"     # Emerald 600
PRIMARY_BG = "#064E3B"       # Subtle badge background

# Acento Secundario & Utilidades
SECONDARY = "#38BDF8"        # Sky Blue / Cyan
SECONDARY_VARIANT = "#0284C7"

# Identidad Cromática Estricta de Macronutrientes
COLOR_PROTEIN = "#8B5CF6"       # Púrpura elegante (Violet 500)
COLOR_PROTEIN_LIGHT = "#A78BFA" # Púrpura suave (Violet 400)
COLOR_PROTEIN_BG = "#2E1B4E"    # Púrpura oscuro para fondo de badge

COLOR_CARBS = "#F59E0B"         # Ámbar / Dorado cálido (Amber 500)
COLOR_CARBS_LIGHT = "#FBBF24"   # Ámbar suave (Amber 400)
COLOR_CARBS_BG = "#3D2700"      # Ámbar oscuro para fondo de badge

COLOR_FAT = "#F97316"           # Coral / Naranja sutil (Orange 500)
COLOR_FAT_LIGHT = "#FB923C"     # Coral suave (Orange 400)
COLOR_FAT_BG = "#3D1B00"        # Coral oscuro para fondo de badge

COLOR_WATER = "#06B6D4"         # Cian / Aqua eléctrico (Cyan 500)
COLOR_WATER_LIGHT = "#38BDF8"   # Aqua brillante
COLOR_WATER_BG = "#083344"      # Aqua profundo

# Alimentos Regionales & Tradicionales
COLOR_REGIONAL = "#10B981"      # Esmeralda Vitalidad
COLOR_REGIONAL_BG = "#064E3B"
COLOR_TRADITIONAL = "#818CF8"   # Índigo Suave
COLOR_RECIPE = "#EC4899"        # Rosa / Magenta gastronómico

# Estados & Semántica
DANGER = "#EF4444"              # Rojo Coral
DANGER_LIGHT = "#F87171"
DANGER_BG = "#450A0A"
WARNING = "#F59E0B"
SUCCESS = "#10B981"

# Tipografía & Contraste
TEXT_PRIMARY = "#F8FAFC"        # Blanco suave / Slate 50
TEXT_SECONDARY = "#94A3B8"      # Slate 400
TEXT_MUTED = "#64748B"          # Slate 500

# Animación Estándar para Micro-interacciones
STANDARD_ANIMATION = ft.Animation(duration=200, curve=ft.AnimationCurve.EASE_OUT)
SMOOTH_ANIMATION = ft.Animation(duration=350, curve=ft.AnimationCurve.EASE_OUT_CUBIC)

# =====================================================================
# ESTILOS DE COMPONENTES REUTILIZABLES
# =====================================================================

def get_card_style(padding=20, border_radius=18, animate=True):
    """Estilo base unificado para tarjetas premium con efecto de elevación y borde fino."""
    style = {
        "bgcolor": SURFACE_CARD,
        "border_radius": border_radius,
        "padding": padding,
        "margin": ft.Margin(left=0, top=0, right=0, bottom=14),
        "border": ft.border.all(1, SURFACE_BORDER),
        "shadow": ft.BoxShadow(
            blur_radius=16,
            color="#14000000",
            offset=ft.Offset(0, 4)
        ),
    }
    if animate:
        style["animate"] = STANDARD_ANIMATION
    return style

def get_input_style(label, icon=None):
    """Estilo moderno para cajas de texto en modo obsidiana."""
    return {
        "label": label,
        "border_color": SURFACE_BORDER,
        "focused_border_color": PRIMARY,
        "cursor_color": PRIMARY,
        "color": TEXT_PRIMARY,
        "label_style": ft.TextStyle(color=TEXT_SECONDARY, size=13),
        "border_radius": 14,
        "prefix_icon": icon,
        "filled": True,
        "fill_color": SURFACE_VARIANT,
        "border": ft.InputBorder.OUTLINE,
        "focused_border_width": 1.5,
        "content_padding": ft.Padding(left=16, top=14, right=16, bottom=14),
    }

def get_button_style():
    """Botón principal de alta visibilidad en esmeralda vibrante."""
    return ft.ButtonStyle(
        color="#FFFFFF",
        bgcolor={
            ft.ControlState.DEFAULT: PRIMARY,
            ft.ControlState.HOVERED: PRIMARY_DARK,
            ft.ControlState.PRESSED: PRIMARY_DARK,
        },
        shape=ft.RoundedRectangleBorder(radius=14),
        padding=ft.Padding(left=20, top=16, right=20, bottom=16),
        elevation={"default": 2, "hovered": 5},
        animation_duration=200,
    )

def get_secondary_button_style():
    """Botón secundario sutil con fondo semi-elevado y borde obsidiana."""
    return ft.ButtonStyle(
        color=TEXT_PRIMARY,
        bgcolor={
            ft.ControlState.DEFAULT: SURFACE_VARIANT,
            ft.ControlState.HOVERED: SURFACE_ELEVATED,
        },
        shape=ft.RoundedRectangleBorder(radius=14),
        padding=ft.Padding(left=18, top=14, right=18, bottom=14),
        side=ft.BorderSide(1, SURFACE_BORDER),
        animation_duration=200,
    )

def get_accent_button_style(color=PRIMARY, text_color="#FFFFFF"):
    """Botón con color de acento personalizado."""
    return ft.ButtonStyle(
        color=text_color,
        bgcolor={
            ft.ControlState.DEFAULT: color,
            ft.ControlState.HOVERED: PRIMARY_DARK,
        },
        shape=ft.RoundedRectangleBorder(radius=12),
        padding=ft.Padding(left=14, top=10, right=14, bottom=10),
    )

# =====================================================================
# HELPERS DE TIPOGRAFÍA Y BADGES
# =====================================================================

def header_text(text):
    return ft.Text(text, size=24, weight=ft.FontWeight.W_700, color=TEXT_PRIMARY)

def subheader_text(text):
    return ft.Text(text, size=16, weight=ft.FontWeight.W_600, color=TEXT_PRIMARY)

def normal_text(text, color=TEXT_PRIMARY, size=13, weight=ft.FontWeight.NORMAL, expand=False):
    return ft.Text(text, size=size, color=color, weight=weight, expand=expand)

def with_opacity(opacity: float, hex_color: str) -> str:
    """Combines an opacity float (0.0 to 1.0) with a 6-digit hex string (#RRGGBB)."""
    if hex_color and hex_color.startswith("#"):
        c = hex_color[1:]
        if len(c) == 6:
            alpha = int(opacity * 255)
            return f"#{alpha:02x}{c}"
    return hex_color

def create_snackbar(content, bgcolor=SURFACE_CARD, duration=3000):
    """Genera un SnackBar flotante con bordes redondeados y estilo premium."""
    if not isinstance(content, ft.Control):
        content = ft.Text(str(content), size=13, color=TEXT_PRIMARY, weight=ft.FontWeight.W_500)
    return ft.SnackBar(
        content=content,
        bgcolor=bgcolor,
        behavior=ft.SnackBarBehavior.FLOATING,
        shape=ft.RoundedRectangleBorder(radius=14),
        duration=duration,
    )

def badge(text, icon=None, bg_color=PRIMARY_BG, text_color=PRIMARY_LIGHT, font_size=11):
    """Crea una micro-etiqueta redondeada (chip/pill badge) estilizada."""
    controls = []
    if icon:
        controls.append(ft.Icon(icon, size=13, color=text_color))
    controls.append(ft.Text(text, size=font_size, weight=ft.FontWeight.W_600, color=text_color))
    
    return ft.Container(
        content=ft.Row(controls, spacing=5, alignment=ft.MainAxisAlignment.CENTER),
        bgcolor=bg_color,
        border_radius=20,
        padding=ft.Padding(left=10, top=4, right=10, bottom=4),
        border=ft.border.all(1, with_opacity(0.3, text_color)),
    )

def regional_badge():
    """Badge distintivo para platos regionales autóctonos del Litoral/Misiones."""
    return badge("Regional", icon=ft.Icons.LOCATION_ON_ROUNDED, bg_color="#064E3B", text_color=PRIMARY_LIGHT)

def recipe_badge():
    """Badge para recetas creadas por el usuario."""
    return badge("Receta", icon=ft.Icons.MENU_BOOK_ROUNDED, bg_color="#3B122D", text_color="#F472B6")

# =====================================================================
# MÁSCARAS DE DIFUMINADO / DESVANECIDO PARA DESPLAZAMIENTO (VIGNETTE)
# =====================================================================

def fade_scroll_vertical(content, top_fade=False, bottom_fade=True, height=None, border_radius=None):
    """
    Aplica una máscara de degradado (ShaderMask) vertical para difuminar suavemente el borde
    inferior cuando un elemento queda cortado al final, manteniendo el inicio 100% nítido y claro.
    """
    colors = []
    stops = []
    
    if top_fade:
        colors.extend([ft.Colors.TRANSPARENT, ft.Colors.BLACK])
        stops.extend([0.0, 0.04])
    else:
        colors.append(ft.Colors.BLACK)
        stops.append(0.0)
        
    if bottom_fade:
        colors.extend([ft.Colors.BLACK, ft.Colors.TRANSPARENT])
        stops.extend([0.96, 1.0])
    else:
        colors.append(ft.Colors.BLACK)
        stops.append(1.0)
        
    gradient = ft.LinearGradient(
        begin=ft.alignment.top_center,
        end=ft.alignment.bottom_center,
        colors=colors,
        stops=stops
    )
    
    mask = ft.ShaderMask(
        content=content,
        shader=gradient,
        blend_mode=ft.BlendMode.DST_IN,
        border_radius=border_radius,
        expand=True if height is not None else False
    )
    
    if height is not None:
        return ft.Container(content=mask, height=height)
    return mask

def fade_scroll_horizontal(content, left_fade=False, right_fade=True, border_radius=None):
    """
    Aplica una máscara de degradado (ShaderMask) horizontal únicamente en el borde
    derecho donde se corta el chip, manteniendo el inicio completamente nítido.
    """
    colors = []
    stops = []
    
    if left_fade:
        colors.extend([ft.Colors.TRANSPARENT, ft.Colors.BLACK])
        stops.extend([0.0, 0.04])
    else:
        colors.append(ft.Colors.BLACK)
        stops.append(0.0)
        
    if right_fade:
        colors.extend([ft.Colors.BLACK, ft.Colors.TRANSPARENT])
        stops.extend([0.91, 1.0])
    else:
        colors.append(ft.Colors.BLACK)
        stops.append(1.0)
        
    gradient = ft.LinearGradient(
        begin=ft.alignment.center_left,
        end=ft.alignment.center_right,
        colors=colors,
        stops=stops
    )
    
    return ft.ShaderMask(
        content=content,
        shader=gradient,
        blend_mode=ft.BlendMode.DST_IN,
        border_radius=border_radius
    )

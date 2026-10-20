import flet as ft
import database as db
from ui import theme

def get_dashboard_view(page: ft.Page, navigate_to_diary, refresh_dashboard):
    profile = db.get_profile()
    if not profile:
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.ACCOUNT_CIRCLE_ROUNDED, size=60, color=theme.PRIMARY),
                theme.header_text("Bienvenido al Gestor"),
                theme.normal_text("Por favor, configura tu perfil para calcular tus metas metabólicas.", color=theme.TEXT_SECONDARY),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            alignment=ft.Alignment(0, 0),
            **theme.get_card_style(padding=30)
        )
        
    target_cal = profile.get('target_calories', 2000)
    entries = db.get_diary_entries()
    
    total_cal = sum(e['calories'] for e in entries)
    total_prot = sum(e['protein'] for e in entries)
    total_carb = sum(e['carbs'] for e in entries)
    total_fat = sum(e['fat'] for e in entries)
    
    water_ml = db.get_water_today()
    water_target = profile.get('water_goal', 2000)
    
    cal_progress = min(total_cal / target_cal, 1.0) if target_cal > 0 else 0
    is_over_cal = total_cal > target_cal
    cal_color = theme.DANGER if is_over_cal else theme.PRIMARY
    remaining_cal = int(target_cal - total_cal)
    
    # -------------------------------------------------------------
    # 1. ANILLO CENTRAL DE CALORÍAS Y RESUMEN HERO
    # -------------------------------------------------------------
    progress_ring = ft.Stack(
        controls=[
            ft.ProgressRing(
                value=cal_progress,
                color=cal_color,
                bgcolor=theme.SURFACE_VARIANT,
                width=150,
                height=150,
                stroke_width=12,
                stroke_cap=ft.StrokeCap.ROUND,
                animate_opacity=theme.STANDARD_ANIMATION,
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text(f"{int(total_cal)}", size=30, weight=ft.FontWeight.W_800, color=theme.TEXT_PRIMARY),
                    ft.Text(f"de {target_cal} kcal", size=12, color=theme.TEXT_SECONDARY, weight=ft.FontWeight.W_500),
                    ft.Container(
                        content=theme.badge(
                            f"{abs(remaining_cal)} kcal {'restantes' if remaining_cal >= 0 else 'excedidas'}",
                            icon=ft.Icons.BOLT_ROUNDED if remaining_cal >= 0 else ft.Icons.WARNING_AMBER_ROUNDED,
                            bg_color=theme.PRIMARY_BG if remaining_cal >= 0 else theme.DANGER_BG,
                            text_color=theme.PRIMARY_LIGHT if remaining_cal >= 0 else theme.DANGER_LIGHT,
                            font_size=10
                        ),
                        margin=ft.Margin(top=2, left=0, right=0, bottom=0)
                    )
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=1),
                alignment=ft.Alignment(0, 0),
                width=150,
                height=150,
            )
        ],
        alignment=ft.Alignment(0, 0)
    )

    # -------------------------------------------------------------
    # 2. SECCIÓN DE MACRONUTRIENTES UNIFICADA (DISEÑO MÓVIL PROFESIONAL)
    # -------------------------------------------------------------
    t_prot = profile.get('target_protein', 150)
    t_carb = profile.get('target_carbs', 200)
    t_fat = profile.get('target_fat', 60)

    def macro_row_item(name, current_g, target_g, color, light_color):
        ratio = (current_g / target_g) if target_g and target_g > 0 else 0
        pct = int(min(ratio, 1.0) * 100)
        
        return ft.Column([
            ft.Row([
                ft.Row([
                    ft.Container(width=8, height=8, border_radius=4, bgcolor=color),
                    ft.Text(name, size=13, weight=ft.FontWeight.W_600, color=theme.TEXT_PRIMARY),
                ], spacing=8),
                ft.Row([
                    ft.Text(f"{int(current_g)}g", size=13, weight=ft.FontWeight.W_700, color=theme.TEXT_PRIMARY),
                    ft.Text(f"/ {int(target_g)}g", size=12, color=theme.TEXT_MUTED),
                    ft.Container(
                        content=ft.Text(f"{pct}%", size=10, weight=ft.FontWeight.W_700, color=light_color),
                        padding=ft.Padding(left=6, top=1, right=6, bottom=1),
                        border_radius=6,
                        bgcolor=theme.with_opacity(0.12, color),
                    )
                ], spacing=4)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.ProgressBar(
                value=min(ratio, 1.0),
                color=color,
                bgcolor=theme.SURFACE_CARD,
                height=6,
                border_radius=3
            )
        ], spacing=5)

    macros_section = ft.Container(
        content=ft.Column([
            ft.Row([
                theme.subheader_text("Macronutrientes"),
            ], alignment=ft.MainAxisAlignment.START),
            ft.Container(height=4),
            macro_row_item("Proteínas", total_prot, t_prot, theme.COLOR_PROTEIN, theme.COLOR_PROTEIN_LIGHT),
            ft.Container(height=2),
            macro_row_item("Carbohidratos", total_carb, t_carb, theme.COLOR_CARBS, theme.COLOR_CARBS_LIGHT),
            ft.Container(height=2),
            macro_row_item("Grasas", total_fat, t_fat, theme.COLOR_FAT, theme.COLOR_FAT_LIGHT),
        ], spacing=6),
        padding=ft.Padding(left=14, top=14, right=14, bottom=14),
        bgcolor=theme.SURFACE_VARIANT,
        border_radius=14,
        border=ft.border.all(1, theme.SURFACE_BORDER)
    )

    hero_card = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Image(src="icon.png", width=22, height=22, border_radius=6, fit=ft.ImageFit.CONTAIN),
                theme.subheader_text("Balance Calórico Diario"),
            ], spacing=8),
            ft.Container(height=10),
            ft.Row([progress_ring], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=16),
            macros_section
        ]),
        **theme.get_card_style(padding=18)
    )

    # -------------------------------------------------------------
    # 3. WIDGET DE HIDRATACIÓN (RESUMEN EJECUTIVO Y ESTADO DE META)
    # -------------------------------------------------------------
    water_progress = min(water_ml / water_target, 1.0) if water_target > 0 else 0
    water_pct = int(water_progress * 100)

    water_card = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.Icons.WATER_DROP_ROUNDED, color=theme.COLOR_WATER_LIGHT, size=24),
                        bgcolor=theme.COLOR_WATER_BG,
                        border_radius=12,
                        padding=10,
                        border=ft.border.all(1, theme.with_opacity(0.3, theme.COLOR_WATER_LIGHT))
                    ),
                    ft.Column([
                        ft.Row([
                            theme.subheader_text("Hidratación"),
                            ft.Container(
                                content=ft.Text(f"{water_pct}%", size=11, weight=ft.FontWeight.W_700, color=theme.COLOR_WATER_LIGHT),
                                bgcolor=theme.COLOR_WATER_BG,
                                padding=ft.Padding(left=8, top=2, right=8, bottom=2),
                                border_radius=8,
                            )
                        ], spacing=6),
                        ft.Row([
                            ft.Text(f"{water_ml}", size=18, weight=ft.FontWeight.W_800, color=theme.TEXT_PRIMARY),
                            ft.Text(f"/ {water_target} ml", size=13, color=theme.TEXT_SECONDARY)
                        ], spacing=4)
                    ], spacing=2)
                ], spacing=10),
                ft.IconButton(
                    ft.Icons.CHEVRON_RIGHT_ROUNDED,
                    icon_color=theme.TEXT_MUTED,
                    tooltip="Registrar hidratación",
                    on_click=lambda _: navigate_to_diary("hydration")
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=8),
            ft.ProgressBar(
                value=water_progress, 
                color=theme.COLOR_WATER, 
                bgcolor=theme.SURFACE_VARIANT, 
                height=8, 
                border_radius=5
            ),
        ]),
        on_click=lambda _: navigate_to_diary("hydration"),
        **theme.get_card_style(padding=16)
    )
    
    # -------------------------------------------------------------
    # 4. ALERTA DE LÍMITE SUPERADO
    # -------------------------------------------------------------
    if is_over_cal:
        excess = int(total_cal - target_cal)
        alert = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(ft.Icons.WARNING_ROUNDED, color=theme.DANGER_LIGHT, size=20),
                    bgcolor=theme.DANGER_BG,
                    padding=8,
                    border_radius=10,
                ),
                ft.Column([
                    ft.Text("Límite calórico superado", color=theme.DANGER_LIGHT, weight=ft.FontWeight.W_700, size=13),
                    ft.Text(f"Has sobrepasado tu meta por {excess} kcal hoy.", color=theme.TEXT_SECONDARY, size=12),
                ], spacing=1, expand=True)
            ], spacing=10),
            padding=12,
            border=ft.border.all(1, theme.DANGER),
            border_radius=14,
            bgcolor=theme.DANGER_BG,
            margin=ft.Margin(0, 0, 0, 10)
        )
    else:
        alert = ft.Container()

    # Botón CTA de alto impacto
    register_btn = ft.ElevatedButton(
        "Registrar Consumo", 
        icon=ft.Icons.ADD_ROUNDED, 
        on_click=lambda _: navigate_to_diary("top"), 
        style=theme.get_button_style(), 
        width=float('inf')
    )

    return ft.Column([
        alert,
        hero_card,
        water_card,
        ft.Container(register_btn, margin=ft.Margin(top=4, left=0, right=0, bottom=16))
    ], scroll=ft.ScrollMode.HIDDEN, spacing=4)

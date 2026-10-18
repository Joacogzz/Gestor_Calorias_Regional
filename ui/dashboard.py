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

    # Métricas clave en pastillas estilizadas (Meta, Consumidas, Restantes)
    def stat_pill(label, value_str, color, icon):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, size=14, color=color),
                    ft.Text(label, size=11, color=theme.TEXT_SECONDARY, weight=ft.FontWeight.W_500),
                ], spacing=4, alignment=ft.MainAxisAlignment.CENTER),
                ft.Text(value_str, size=15, weight=ft.FontWeight.W_700, color=theme.TEXT_PRIMARY),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
            bgcolor=theme.SURFACE_VARIANT,
            padding=ft.Padding(left=12, top=10, right=12, bottom=10),
            border_radius=14,
            border=ft.border.all(1, theme.SURFACE_BORDER),
            expand=True,
            animate=theme.STANDARD_ANIMATION,
        )

    summary_row = ft.Row([
        stat_pill("Meta Diaria", f"{target_cal}", theme.TEXT_SECONDARY, ft.Icons.FLAG_ROUNDED),
        stat_pill("Consumidas", f"{int(total_cal)}", theme.PRIMARY_LIGHT, ft.Icons.LOCAL_FIRE_DEPARTMENT_ROUNDED),
        stat_pill("Restantes", f"{max(0, remaining_cal)}", theme.SECONDARY, ft.Icons.TRENDING_DOWN_ROUNDED),
    ], spacing=8)

    # -------------------------------------------------------------
    # 2. SECCIÓN DE MACRONUTRIENTES
    # -------------------------------------------------------------
    t_prot = profile.get('target_protein', 150)
    t_carb = profile.get('target_carbs', 200)
    t_fat = profile.get('target_fat', 60)

    def macro_card_modern(name, current_g, target_g, color, bg_color, light_color, icon):
        ratio = (current_g / target_g) if target_g and target_g > 0 else 0
        pct = int(min(ratio, 1.0) * 100)
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Row([
                        ft.Container(
                            content=ft.Icon(icon, size=14, color=light_color),
                            bgcolor=bg_color,
                            border_radius=8,
                            padding=4,
                        ),
                        ft.Text(name, size=12, weight=ft.FontWeight.W_600, color=theme.TEXT_PRIMARY),
                    ], spacing=6),
                    ft.Text(f"{pct}%", size=11, weight=ft.FontWeight.W_700, color=light_color)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=4),
                # Barra de progreso estilizada
                ft.ProgressBar(
                    value=min(ratio, 1.0),
                    color=color,
                    bgcolor=theme.SURFACE_VARIANT,
                    height=7,
                    border_radius=4
                ),
                ft.Container(height=2),
                ft.Row([
                    ft.Text(f"{int(current_g)}g", size=13, weight=ft.FontWeight.W_700, color=theme.TEXT_PRIMARY),
                    ft.Text(f"/ {int(target_g)}g", size=11, color=theme.TEXT_MUTED)
                ], spacing=2)
            ], spacing=2),
            bgcolor=theme.SURFACE_VARIANT,
            padding=12,
            border_radius=14,
            border=ft.border.all(1, theme.SURFACE_BORDER),
            expand=True,
            animate=theme.STANDARD_ANIMATION,
        )

    macros_grid = ft.Row([
        macro_card_modern("Proteína", total_prot, t_prot, theme.COLOR_PROTEIN, theme.COLOR_PROTEIN_BG, theme.COLOR_PROTEIN_LIGHT, ft.Icons.FITNESS_CENTER_ROUNDED),
        macro_card_modern("Carbos", total_carb, t_carb, theme.COLOR_CARBS, theme.COLOR_CARBS_BG, theme.COLOR_CARBS_LIGHT, ft.Icons.GRAIN_ROUNDED),
        macro_card_modern("Grasas", total_fat, t_fat, theme.COLOR_FAT, theme.COLOR_FAT_BG, theme.COLOR_FAT_LIGHT, ft.Icons.OPACITY_ROUNDED),
    ], spacing=8)

    hero_card = ft.Container(
        content=ft.Column([
            ft.Row([
                theme.subheader_text("Balance Calórico Diario"),
                theme.badge("Mifflin-St Jeor", icon=ft.Icons.AUTO_GRAPH_ROUNDED, bg_color=theme.SURFACE_VARIANT, text_color=theme.TEXT_SECONDARY, font_size=10)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=10),
            ft.Row([progress_ring], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=14),
            summary_row,
            ft.Container(height=12),
            macros_grid
        ]),
        **theme.get_card_style(padding=18)
    )

    # -------------------------------------------------------------
    # 3. WIDGET DE HIDRATACIÓN (AGUA)
    # -------------------------------------------------------------
    water_progress = min(water_ml / water_target, 1.0) if water_target > 0 else 0
    water_pct = int(water_progress * 100)

    def quick_add_water(amount):
        if amount > 0:
            db.add_water(amount)
        elif amount < 0:
            if water_ml + amount < 0:
                db.add_water(-water_ml)
            else:
                db.add_water(amount)
        refresh_dashboard()

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
                            theme.badge(f"{water_pct}%", bg_color=theme.COLOR_WATER_BG, text_color=theme.COLOR_WATER_LIGHT, font_size=11)
                        ], spacing=6),
                        ft.Row([
                            ft.Text(f"{water_ml}", size=18, weight=ft.FontWeight.W_800, color=theme.TEXT_PRIMARY),
                            ft.Text(f"/ {water_target} ml", size=13, color=theme.TEXT_SECONDARY)
                        ], spacing=4)
                    ], spacing=2)
                ], spacing=10),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=8),
            # Barra de progreso de hidratación
            ft.ProgressBar(
                value=water_progress, 
                color=theme.COLOR_WATER, 
                bgcolor=theme.SURFACE_VARIANT, 
                height=9, 
                border_radius=6
            ),
            ft.Container(height=10),
            # Botones táctiles rápidos
            ft.Row([
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.LOCAL_DRINK_ROUNDED, size=15, color=theme.COLOR_WATER_LIGHT),
                        ft.Text("+250 ml", size=12, weight=ft.FontWeight.W_600, color=theme.TEXT_PRIMARY)
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=4),
                    bgcolor=theme.SURFACE_VARIANT,
                    border_radius=12,
                    padding=ft.Padding(left=12, top=10, right=12, bottom=10),
                    border=ft.border.all(1, theme.SURFACE_BORDER),
                    on_click=lambda _: quick_add_water(250),
                    expand=True,
                    animate=theme.STANDARD_ANIMATION,
                ),
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.WATER_ROUNDED, size=15, color=theme.COLOR_WATER_LIGHT),
                        ft.Text("+500 ml", size=12, weight=ft.FontWeight.W_600, color=theme.TEXT_PRIMARY)
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=4),
                    bgcolor=theme.SURFACE_VARIANT,
                    border_radius=12,
                    padding=ft.Padding(left=12, top=10, right=12, bottom=10),
                    border=ft.border.all(1, theme.SURFACE_BORDER),
                    on_click=lambda _: quick_add_water(500),
                    expand=True,
                    animate=theme.STANDARD_ANIMATION,
                ),
                ft.Container(
                    content=ft.Icon(ft.Icons.REMOVE_ROUNDED, size=18, color=theme.DANGER_LIGHT),
                    bgcolor=theme.SURFACE_VARIANT,
                    border_radius=12,
                    padding=ft.Padding(left=14, top=10, right=14, bottom=10),
                    border=ft.border.all(1, theme.SURFACE_BORDER),
                    on_click=lambda _: quick_add_water(-250),
                    tooltip="Restar 250 ml",
                    animate=theme.STANDARD_ANIMATION,
                ),
            ], spacing=8)
        ]),
        **theme.get_card_style(padding=18)
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
        "Registrar Alimento", 
        icon=ft.Icons.ADD_ROUNDED, 
        on_click=lambda _: navigate_to_diary(), 
        style=theme.get_button_style(), 
        width=float('inf')
    )

    return ft.Column([
        alert,
        hero_card,
        water_card,
        ft.Container(register_btn, margin=ft.Margin(top=4, left=0, right=0, bottom=16))
    ], scroll=ft.ScrollMode.AUTO, spacing=4)

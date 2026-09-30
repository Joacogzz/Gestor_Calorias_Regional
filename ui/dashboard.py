import flet as ft
import database as db
from ui import theme

def get_dashboard_view(page: ft.Page, navigate_to_diary, refresh_dashboard):
    profile = db.get_profile()
    if not profile:
        return ft.Container(
            content=ft.Column([
                theme.header_text("Bienvenido al Gestor de Calorías Regional"),
                theme.normal_text("Por favor, configura tu perfil para comenzar."),
            ]),
            **theme.get_card_style()
        )
        
    target_cal = profile['target_calories']
    entries = db.get_diary_entries()
    
    total_cal = sum(e['calories'] for e in entries)
    total_prot = sum(e['protein'] for e in entries)
    total_carb = sum(e['carbs'] for e in entries)
    total_fat = sum(e['fat'] for e in entries)
    
    water_ml = db.get_water_today()
    
    cal_progress = min(total_cal / target_cal, 1.0) if target_cal > 0 else 0
    cal_color = theme.PRIMARY if total_cal <= target_cal else theme.DANGER
    

        
    progress_ring = ft.Stack(
        controls=[
            ft.ProgressRing(
                value=cal_progress,
                color=cal_color,
                bgcolor="#1A1A1A", # Dark track for contrast
                width=150,
                height=150,
                stroke_width=15
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text(f"{int(total_cal)}", size=30, weight=ft.FontWeight.BOLD, color=theme.TEXT_PRIMARY),
                    ft.Text(f"/ {target_cal} kcal", size=14, color=theme.TEXT_SECONDARY)
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.Alignment(0, 0),
                width=150,
                height=150,
            )
        ]
    )
    
    t_prot = profile.get('target_protein', 150)
    t_carb = profile.get('target_carbs', 200)
    t_fat = profile.get('target_fat', 60)
    
    macros_row = ft.Row([
        macro_card("Proteínas", total_prot, t_prot, theme.PRIMARY),
        macro_card("Carbos", total_carb, t_carb, theme.SECONDARY),
        macro_card("Grasas", total_fat, t_fat, theme.DANGER),
    ], alignment=ft.MainAxisAlignment.SPACE_EVENLY)

    water_input = ft.TextField(
        value="250",
        width=80,
        keyboard_type=ft.KeyboardType.NUMBER,
        text_align=ft.TextAlign.CENTER,
        content_padding=5,
        border_radius=10,
        bgcolor=theme.SURFACE_VARIANT,
        border_color=theme.PRIMARY,
    )

    def add_water_click(e):
        try:
            amount = int(water_input.value)
            if amount > 0:
                db.add_water(amount)
                refresh_dashboard()
        except ValueError:
            pass

    def remove_water_click(e):
        try:
            amount = int(water_input.value)
            if amount > 0:
                # Evitar que el agua total sea menor a 0
                if water_ml - amount < 0:
                    db.add_water(-water_ml)
                else:
                    db.add_water(-amount)
                refresh_dashboard()
        except ValueError:
            pass

    water_target = profile.get('water_goal', 2000)
    water_progress = min(water_ml / water_target, 1.0) if water_target > 0 else 0

    water_card = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Row([
                    ft.Icon(ft.Icons.WATER_DROP, color="blue", size=40),
                    ft.Column([
                        theme.subheader_text("Agua consumida"),
                        theme.normal_text(f"{water_ml} / {water_target} ml hoy", size=18)
                    ]),
                ]),
                ft.Row([
                    water_input,
                    ft.IconButton(ft.Icons.REMOVE_CIRCLE, icon_color=theme.DANGER, on_click=remove_water_click, icon_size=35),
                    ft.IconButton(ft.Icons.ADD_CIRCLE, icon_color=theme.PRIMARY, on_click=add_water_click, icon_size=35)
                ], alignment=ft.MainAxisAlignment.CENTER)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, wrap=True),
            ft.ProgressBar(value=water_progress, color="blue", bgcolor=theme.SURFACE, height=10, border_radius=5)
        ]),
        **theme.get_card_style()
    )
    
    if total_cal > target_cal:
        alert = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.WARNING, color=theme.DANGER),
                ft.Text("¡Has superado tu límite calórico diario!", color=theme.DANGER, weight=ft.FontWeight.BOLD)
            ]),
            padding=10,
            border=ft.Border(top=ft.BorderSide(1, theme.DANGER), right=ft.BorderSide(1, theme.DANGER), bottom=ft.BorderSide(1, theme.DANGER), left=ft.BorderSide(1, theme.DANGER)),
            border_radius=10,
            bgcolor="errorcontainer"
        )
    else:
        alert = ft.Container()

    return ft.Column([
        theme.header_text("Resumen de Hoy"),
        alert,
        ft.Container(
            content=ft.Column([
                ft.Row([progress_ring], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=20),
                macros_row
            ]),
            **theme.get_card_style()
        ),
        water_card,
        ft.ElevatedButton("Registrar Consumo", icon=ft.Icons.ADD, on_click=lambda _: navigate_to_diary(), style=theme.get_button_style(), width=float('inf'))
    ], scroll=ft.ScrollMode.AUTO)

def macro_card(title, value, target, color):
    prog = min(value/target, 1.0) if target and target > 0 else 0
    return ft.Column([
        theme.normal_text(title, color=theme.TEXT_SECONDARY, size=14),
        ft.Stack([
            ft.ProgressRing(value=prog, color=color, bgcolor="#1A1A1A", width=70, height=70, stroke_width=8),
            ft.Container(
                content=theme.normal_text(f"{int(value)}g", weight=ft.FontWeight.BOLD, size=16),
                alignment=ft.Alignment(0, 0),
                width=70, height=70
            )
        ]),
        theme.normal_text(f"Meta: {int(target) if target else '?'}g", color=theme.TEXT_SECONDARY, size=12)
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

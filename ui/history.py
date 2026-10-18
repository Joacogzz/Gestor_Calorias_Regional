import flet as ft
import database as db
from ui import theme
import datetime

def get_history_view(page: ft.Page, refresh_history):
    profile = db.get_profile()
    if not profile:
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.INSIGHTS_ROUNDED, size=50, color=theme.PRIMARY),
                theme.header_text("Historial de Progreso"),
                theme.normal_text("Por favor, configura tu perfil para comenzar a registrar tu historial.", color=theme.TEXT_SECONDARY),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
            alignment=ft.Alignment(0, 0),
            **theme.get_card_style(padding=24)
        )

    target_cal = profile.get('target_calories', 2000)
    history_data = db.get_historical_summary()

    if not history_data:
        return ft.Column([
            ft.Row([
                theme.header_text("Historial de Progreso"),
            ]),
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.CALENDAR_MONTH_ROUNDED, size=50, color=theme.TEXT_MUTED),
                    ft.Text("Aún no tienes registros históricos.", size=14, weight=ft.FontWeight.W_600, color=theme.TEXT_PRIMARY),
                    ft.Text("Registra tus comidas en el Diario hoy para ver aquí tu evolución.", size=12, color=theme.TEXT_SECONDARY),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6),
                alignment=ft.Alignment(0, 0),
                **theme.get_card_style(padding=30)
            )
        ], expand=True)

    months_es = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    day_abbr = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    
    # -------------------------------------------------------------
    # 1. GRÁFICOS SEMANALES (ÚLTIMOS 7 DÍAS)
    # -------------------------------------------------------------
    last_7 = history_data[:7][::-1] # El más antiguo a la izquierda
    
    cal_data = []
    water_data = []
    max_cal = target_cal if target_cal > 0 else 2000
    max_water = profile.get('water_goal', 2000)
    
    for day in last_7:
        d_obj = datetime.datetime.strptime(day['date'], '%Y-%m-%d')
        lbl = day_abbr[d_obj.weekday()]
        
        cal_val = float(day['calories'])
        if cal_val > max_cal:
            max_cal = cal_val
            
        water_val = float(day['water'])
        if water_val > max_water:
            max_water = water_val
            
        cal_data.append((lbl, cal_val))
        water_data.append((lbl, water_val))

    def create_bar_chart(data_pairs, max_val, title, icon, is_cal=True):
        bars = []
        for label, val in data_pairs:
            height = (val / max_val * 110) if max_val > 0 else 0
            
            if is_cal:
                bar_color = theme.DANGER if val > target_cal else theme.PRIMARY
            else:
                bar_color = theme.COLOR_WATER

            bars.append(
                ft.Column([
                    ft.Container(
                        width=22,
                        height=110,
                        bgcolor=theme.SURFACE_VARIANT,
                        border_radius=8,
                        alignment=ft.Alignment(0, 1),
                        content=ft.Container(
                            width=22,
                            height=max(6, height),
                            bgcolor=bar_color,
                            border_radius=ft.border_radius.only(top_left=8, top_right=8, bottom_left=4, bottom_right=4),
                            animate=theme.STANDARD_ANIMATION,
                            tooltip=f"{int(val)} {'kcal' if is_cal else 'ml'}"
                        )
                    ),
                    ft.Text(label, size=11, color=theme.TEXT_SECONDARY, weight=ft.FontWeight.W_500)
                ], alignment=ft.MainAxisAlignment.END, spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            )
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, size=16, color=theme.PRIMARY_LIGHT if is_cal else theme.COLOR_WATER_LIGHT),
                    ft.Text(title, size=13, weight=ft.FontWeight.W_700, color=theme.TEXT_PRIMARY),
                ], spacing=6),
                ft.Container(height=6),
                ft.Row(bars, alignment=ft.MainAxisAlignment.SPACE_EVENLY, vertical_alignment=ft.CrossAxisAlignment.END)
            ]),
            bgcolor=theme.SURFACE_CARD,
            padding=14,
            border_radius=16,
            border=ft.border.all(1, theme.SURFACE_BORDER),
            expand=True
        )

    def export_csv(e):
        import csv
        filename = "historial_calorias.csv"
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Fecha", "Calorias", "Proteinas (g)", "Carbohidratos (g)", "Grasas (g)", "Agua (ml)"])
                for day in history_data:
                    writer.writerow([day['date'], int(day['calories']), int(day['protein']), int(day['carbs']), int(day['fat']), int(day['water'])])
            page.snack_bar = theme.create_snackbar(
                content=ft.Row([
                    ft.Icon(ft.Icons.DOWNLOAD_DONE_ROUNDED, color=theme.PRIMARY_LIGHT, size=18),
                    ft.Text(f"Exportado correctamente ({filename})", size=13, color=theme.TEXT_PRIMARY)
                ], spacing=8),
                bgcolor=theme.SURFACE_CARD,
                duration=3000
            )
            page.snack_bar.open = True
            page.update()
        except Exception:
            pass

    header = ft.Row([
        ft.Column([
            theme.header_text("Historial y Métricas"),
            ft.Text("Evolución de calorías y macronutrientes", size=12, color=theme.TEXT_SECONDARY)
        ], spacing=1),
        ft.ElevatedButton(
            "Exportar", 
            icon=ft.Icons.FILE_DOWNLOAD_ROUNDED, 
            on_click=export_csv, 
            style=theme.get_secondary_button_style()
        )
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    content_cols = [
        header,
        ft.Container(height=6),
        ft.Row([
            create_bar_chart(cal_data, max_cal, "Calorías (7 Días)", ft.Icons.LOCAL_FIRE_DEPARTMENT_ROUNDED, is_cal=True),
            create_bar_chart(water_data, max_water, "Agua (ml)", ft.Icons.WATER_DROP_ROUNDED, is_cal=False)
        ], spacing=10),
        ft.Container(height=8),
        ft.Row([
            theme.subheader_text("Registros Pasados"),
            theme.badge(f"{len(history_data)} días", icon=ft.Icons.HISTORY_ROUNDED, bg_color=theme.SURFACE_VARIANT, text_color=theme.TEXT_SECONDARY, font_size=10)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    ]
    
    # -------------------------------------------------------------
    # 2. AGRUPACIÓN MENSUAL Y TARJETAS DETALLADAS
    # -------------------------------------------------------------
    grouped_data = {}
    for day in history_data:
        date_obj = datetime.datetime.strptime(day['date'], '%Y-%m-%d')
        month_str = f"{months_es[date_obj.month - 1]} {date_obj.year}"
        
        if month_str not in grouped_data:
            grouped_data[month_str] = []
        grouped_data[month_str].append((date_obj, day))

    for month, days in grouped_data.items():
        month_label = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.CALENDAR_MONTH_ROUNDED, size=15, color=theme.PRIMARY_LIGHT),
                ft.Text(month, size=14, weight=ft.FontWeight.W_700, color=theme.TEXT_PRIMARY)
            ], spacing=6),
            padding=ft.Padding(left=4, top=8, right=4, bottom=4)
        )
        content_cols.append(month_label)
        
        for date_obj, day in days:
            cal = int(day['calories'])
            water = int(day['water'])
            
            cal_color = theme.DANGER if cal > target_cal else theme.PRIMARY
            day_str = f"{date_obj.day:02d}/{date_obj.month:02d}/{date_obj.year}"
            db_date_str = day['date']
            
            def delete_day_click(e, d_str=db_date_str):
                db.delete_historical_day(d_str)
                refresh_history()
                page.snack_bar = theme.create_snackbar(
                    content=ft.Text(f"Registros del día {d_str} eliminados."), 
                    bgcolor=theme.SURFACE_CARD
                )
                page.snack_bar.open = True
                page.update()

            day_card = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Row([
                            ft.Icon(ft.Icons.EVENT_NOTE_ROUNDED, color=theme.TEXT_SECONDARY, size=16),
                            ft.Text(day_str, weight=ft.FontWeight.W_700, size=14, color=theme.TEXT_PRIMARY),
                        ], spacing=6),
                        ft.Row([
                            ft.Container(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.LOCAL_FIRE_DEPARTMENT_ROUNDED, color=cal_color, size=14),
                                    ft.Text(f"{cal} / {target_cal} kcal", color=cal_color, weight=ft.FontWeight.W_700, size=12),
                                ], spacing=4),
                                bgcolor=theme.SURFACE_VARIANT,
                                padding=ft.Padding(left=8, top=4, right=8, bottom=4),
                                border_radius=8,
                            ),
                            ft.IconButton(
                                ft.Icons.DELETE_OUTLINE_ROUNDED, 
                                icon_color=theme.DANGER_LIGHT, 
                                icon_size=18, 
                                tooltip="Eliminar día",
                                on_click=delete_day_click
                            )
                        ], spacing=4)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    
                    ft.Divider(color=theme.SURFACE_BORDER, height=1),
                    
                    ft.Row([
                        # Proteínas
                        ft.Container(
                            content=ft.Row([
                                ft.Text("P:", size=11, weight=ft.FontWeight.W_700, color=theme.COLOR_PROTEIN_LIGHT),
                                ft.Text(f"{int(day['protein'])}g", size=11, color=theme.TEXT_PRIMARY)
                            ], spacing=2),
                            bgcolor=theme.COLOR_PROTEIN_BG,
                            padding=ft.Padding(left=8, top=4, right=8, bottom=4),
                            border_radius=8
                        ),
                        # Carbohidratos
                        ft.Container(
                            content=ft.Row([
                                ft.Text("C:", size=11, weight=ft.FontWeight.W_700, color=theme.COLOR_CARBS_LIGHT),
                                ft.Text(f"{int(day['carbs'])}g", size=11, color=theme.TEXT_PRIMARY)
                            ], spacing=2),
                            bgcolor=theme.COLOR_CARBS_BG,
                            padding=ft.Padding(left=8, top=4, right=8, bottom=4),
                            border_radius=8
                        ),
                        # Grasas
                        ft.Container(
                            content=ft.Row([
                                ft.Text("G:", size=11, weight=ft.FontWeight.W_700, color=theme.COLOR_FAT_LIGHT),
                                ft.Text(f"{int(day['fat'])}g", size=11, color=theme.TEXT_PRIMARY)
                            ], spacing=2),
                            bgcolor=theme.COLOR_FAT_BG,
                            padding=ft.Padding(left=8, top=4, right=8, bottom=4),
                            border_radius=8
                        ),
                        # Agua
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(ft.Icons.WATER_DROP_ROUNDED, color=theme.COLOR_WATER_LIGHT, size=13),
                                ft.Text(f"{water} ml", color=theme.COLOR_WATER_LIGHT, weight=ft.FontWeight.W_700, size=11)
                            ], spacing=2),
                            bgcolor=theme.COLOR_WATER_BG,
                            padding=ft.Padding(left=8, top=4, right=8, bottom=4),
                            border_radius=8
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ], spacing=8),
                padding=12,
                bgcolor=theme.SURFACE_CARD,
                border_radius=14,
                border=ft.border.all(1, theme.SURFACE_BORDER),
                margin=ft.Margin(0, 0, 0, 8),
                animate=theme.STANDARD_ANIMATION,
            )
            content_cols.append(day_card)

    return ft.Column(content_cols, expand=True, scroll=ft.ScrollMode.AUTO, spacing=4)

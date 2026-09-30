import flet as ft
import database as db
from ui import theme
import datetime

def get_history_view(page: ft.Page, refresh_history):
    profile = db.get_profile()
    if not profile:
        return ft.Container(
            content=ft.Column([
                theme.header_text("Historial de Progreso"),
                theme.normal_text("Por favor, configura tu perfil para comenzar."),
            ]),
            **theme.get_card_style()
        )

    target_cal = profile['target_calories']
    history_data = db.get_historical_summary()

    if not history_data:
        return ft.Column([
            theme.header_text("Historial de Progreso"),
            ft.Container(
                content=theme.normal_text("Aún no tienes registros históricos. ¡Empieza a registrar en tu diario hoy!"),
                **theme.get_card_style()
            )
        ], expand=True)

    months_es = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    day_abbr = ["L", "M", "Mi", "J", "V", "S", "D"]
    
    # --- GRÁFICOS SEMANALES (Últimos 7 días) ---
    last_7 = history_data[:7][::-1] # Invertir para que el más viejo quede a la izquierda
    
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

    def create_bar_chart(data_pairs, max_val, title, dynamic_colors=False):
        bars = []
        for label, val in data_pairs:
            height = (val / max_val * 120) if max_val > 0 else 0
            
            bar_color = theme.PRIMARY
            if dynamic_colors:
                bar_color = theme.DANGER if val > target_cal else theme.PRIMARY
            else:
                bar_color = "blue"

            bars.append(
                ft.Column([
                    ft.Container(
                        width=20,
                        height=120,
                        bgcolor="#1A1A1A",
                        border_radius=10,
                        alignment=ft.Alignment(0, 1),
                        content=ft.Container(
                            width=20,
                            height=max(5, height),
                            bgcolor=bar_color,
                            border_radius=10,
                        )
                    ),
                    theme.normal_text(label, size=12, color=theme.TEXT_SECONDARY)
                ], alignment=ft.MainAxisAlignment.END, spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            )
        
        return ft.Container(
            content=ft.Column([
                theme.subheader_text(title),
                ft.Row(bars, alignment=ft.MainAxisAlignment.SPACE_EVENLY, vertical_alignment=ft.CrossAxisAlignment.END)
            ]),
            **theme.get_card_style()
        )

    def export_csv(e):
        import csv
        import os
        filename = "historial_calorias.csv"
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Fecha", "Calorias", "Proteinas (g)", "Carbohidratos (g)", "Grasas (g)", "Agua (ml)"])
                for day in history_data:
                    writer.writerow([day['date'], int(day['calories']), int(day['protein']), int(day['carbs']), int(day['fat']), int(day['water'])])
            page.snack_bar = ft.SnackBar(ft.Text(f"Exportado correctamente a la carpeta del programa ({filename})"), bgcolor=theme.PRIMARY)
            page.snack_bar.open = True
            page.update()
        except Exception as ex:
            pass

    header = ft.Row([
        theme.header_text("Historial de Progreso"),
        ft.Container(expand=True),
        ft.ElevatedButton("Exportar CSV", icon=ft.Icons.DOWNLOAD, on_click=export_csv, style=theme.get_button_style())
    ])

    content_cols = [
        header,
        theme.subheader_text("Resumen de los últimos 7 días"),
        ft.Row([
            ft.Container(content=create_bar_chart(cal_data, max_cal, "Calorías", True), expand=True),
            ft.Container(content=create_bar_chart(water_data, max_water, "Agua (ml)", False), expand=True)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    ]
    
    # Agrupar por mes
    grouped_data = {}
    for day in history_data:
        date_obj = datetime.datetime.strptime(day['date'], '%Y-%m-%d')
        month_str = f"{months_es[date_obj.month - 1]} {date_obj.year}"
        
        if month_str not in grouped_data:
            grouped_data[month_str] = []
        grouped_data[month_str].append((date_obj, day))

    for month, days in grouped_data.items():
        month_label = ft.Container(
            content=theme.subheader_text(month),
            padding=10
        )
        content_cols.append(month_label)
        
        for date_obj, day in days:
            cal = int(day['calories'])
            water = int(day['water'])
            
            cal_color = theme.PRIMARY if cal <= target_cal else theme.DANGER
            day_str = f"{date_obj.day:02d}/{date_obj.month:02d}/{date_obj.year}"
            db_date_str = day['date']
            
            def delete_day_click(e, d_str=db_date_str):
                db.delete_historical_day(d_str)
                refresh_history()
                page.snack_bar = ft.SnackBar(ft.Text(f"Día {d_str} eliminado."), bgcolor=theme.SECONDARY)
                page.snack_bar.open = True
                page.update()

            day_card = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.CALENDAR_TODAY, color=theme.TEXT_SECONDARY, size=20),
                        theme.normal_text(day_str, weight=ft.FontWeight.BOLD, size=16),
                        ft.Container(expand=True),
                        ft.Icon(ft.Icons.LOCAL_FIRE_DEPARTMENT, color=cal_color, size=18),
                        theme.normal_text(f"{cal} / {target_cal} kcal", color=cal_color, weight=ft.FontWeight.BOLD),
                        ft.IconButton(ft.Icons.DELETE, icon_color=theme.DANGER, icon_size=20, on_click=delete_day_click)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    
                    ft.Divider(color=theme.TEXT_SECONDARY),
                    
                    ft.Row([
                        ft.Column([
                            theme.normal_text("Proteínas", size=12, color=theme.TEXT_SECONDARY),
                            theme.normal_text(f"{int(day['protein'])}g", weight=ft.FontWeight.BOLD)
                        ]),
                        ft.Column([
                            theme.normal_text("Carbos", size=12, color=theme.TEXT_SECONDARY),
                            theme.normal_text(f"{int(day['carbs'])}g", weight=ft.FontWeight.BOLD)
                        ]),
                        ft.Column([
                            theme.normal_text("Grasas", size=12, color=theme.TEXT_SECONDARY),
                            theme.normal_text(f"{int(day['fat'])}g", weight=ft.FontWeight.BOLD)
                        ]),
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(ft.Icons.WATER_DROP, color="blue", size=16),
                                theme.normal_text(f"{water} ml", color="blue", weight=ft.FontWeight.BOLD)
                            ]),
                            bgcolor="secondarycontainer",
                            padding=8,
                            border_radius=8
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ]),
                **theme.get_card_style()
            )
            content_cols.append(day_card)

    return ft.Column(content_cols, expand=True, scroll=ft.ScrollMode.AUTO)

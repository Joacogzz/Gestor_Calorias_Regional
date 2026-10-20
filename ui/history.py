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
    water_target = profile.get('water_goal', 2000)
    history_data = db.get_historical_summary()



    months_es = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    day_abbr = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    day_names_es = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    today_str = datetime.date.today().strftime('%Y-%m-%d')
    
    # -------------------------------------------------------------
    # 1. GENERACIÓN DE LOS ÚLTIMOS 7 DÍAS CONTINUOS
    # -------------------------------------------------------------
    today = datetime.date.today()
    last_7_dates = [(today - datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)]
    history_map = {d['date']: d for d in history_data}
    
    last_7_info = []
    max_c = target_cal if target_cal > 0 else 2000
    max_w = water_target if water_target > 0 else 2000

    for idx, d_str in enumerate(last_7_dates):
        d_obj = datetime.datetime.strptime(d_str, '%Y-%m-%d')
        lbl = day_abbr[d_obj.weekday()]
        entry = history_map.get(d_str, {'calories': 0, 'water': 0, 'protein': 0, 'carbs': 0, 'fat': 0})
        c_val = float(entry.get('calories', 0))
        w_val = float(entry.get('water', 0))
        if c_val > max_c: max_c = c_val
        if w_val > max_w: max_w = w_val
        last_7_info.append({
            'idx': idx,
            'date': d_str,
            'day_lbl': lbl,
            'cal': c_val,
            'water': w_val
        })

    # -------------------------------------------------------------
    # 2. GRÁFICO NATIVO DE CALORÍAS (FT.LINECHART CON META DE REFERENCIA)
    # -------------------------------------------------------------
    cal_line_points = [
        ft.LineChartDataPoint(d['idx'], d['cal']) for d in last_7_info
    ]
    target_line_points = [
        ft.LineChartDataPoint(0, target_cal),
        ft.LineChartDataPoint(6, target_cal)
    ]
    
    cal_axis_labels = [
        ft.ChartAxisLabel(value=d['idx'], label=ft.Text(d['day_lbl'], size=10, color=theme.TEXT_SECONDARY, weight=ft.FontWeight.W_600))
        for d in last_7_info
    ]

    cal_line_chart = ft.LineChart(
        data_series=[
            # Línea de referencia de la meta calórica (Línea punteada en ámbar)
            ft.LineChartData(
                data_points=target_line_points,
                color=theme.COLOR_CARBS,
                stroke_width=2,
                dash_pattern=[4, 4],
                curved=False,
                point=False,
            ),
            # Curva de consumo real en esmeralda con relleno suave inferior
            ft.LineChartData(
                data_points=cal_line_points,
                color=theme.PRIMARY,
                stroke_width=3,
                curved=True,
                stroke_cap_round=True,
                below_line_bgcolor=theme.with_opacity(0.12, theme.PRIMARY),
                point=True,
            )
        ],
        bottom_axis=ft.ChartAxis(
            labels=cal_axis_labels,
            labels_size=20
        ),
        horizontal_grid_lines=ft.ChartGridLines(color=theme.SURFACE_BORDER, width=1, dash_pattern=[4, 4]),
        border=ft.Border(
            bottom=ft.BorderSide(1, theme.SURFACE_BORDER),
            left=ft.BorderSide(1, theme.SURFACE_BORDER)
        ),
        min_y=0,
        max_y=max(max_c * 1.15, target_cal * 1.2),
        min_x=0,
        max_x=6,
        interactive=True,
        expand=True,
        tooltip_bgcolor=theme.SURFACE_CARD,
    )

    cal_chart_card = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Row([
                    ft.Icon(ft.Icons.SHOW_CHART_ROUNDED, size=16, color=theme.PRIMARY_LIGHT),
                    ft.Text("Calorías (Últimos 7 Días)", size=13, weight=ft.FontWeight.W_700, color=theme.TEXT_PRIMARY),
                ], spacing=6),
                ft.Row([
                    ft.Container(
                        content=ft.Row([
                            ft.Container(width=10, height=2, bgcolor=theme.COLOR_CARBS),
                            ft.Text(f"Meta: {target_cal} kcal", size=10, color=theme.COLOR_CARBS_LIGHT, weight=ft.FontWeight.W_600)
                        ], spacing=4),
                        bgcolor=theme.COLOR_CARBS_BG,
                        padding=ft.Padding(left=6, top=3, right=6, bottom=3),
                        border_radius=8
                    )
                ], spacing=4)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=4),
            ft.Container(content=cal_line_chart, height=150, padding=ft.Padding(left=4, top=4, right=14, bottom=0))
        ], spacing=4),
        bgcolor=theme.SURFACE_CARD,
        padding=14,
        border_radius=16,
        border=ft.border.all(1, theme.SURFACE_BORDER),
    )

    # -------------------------------------------------------------
    # 3. GRÁFICO NATIVO DE HIDRATACIÓN (FT.BARCHART FRENTE AL OBJETIVO)
    # -------------------------------------------------------------
    water_bar_groups = []
    for d in last_7_info:
        water_bar_groups.append(
            ft.BarChartGroup(
                x=d['idx'],
                bar_rods=[
                    ft.BarChartRod(
                        from_y=0,
                        to_y=d['water'],
                        width=16,
                        color=theme.COLOR_WATER,
                        border_radius=ft.border_radius.vertical(top=6),
                        tooltip=f"{int(d['water'])} / {water_target} ml",
                        bg_to_y=water_target,
                        bg_color=theme.SURFACE_VARIANT
                    )
                ]
            )
        )

    water_bar_chart = ft.BarChart(
        bar_groups=water_bar_groups,
        bottom_axis=ft.ChartAxis(
            labels=cal_axis_labels,
            labels_size=20
        ),
        horizontal_grid_lines=ft.ChartGridLines(color=theme.SURFACE_BORDER, width=1, dash_pattern=[4, 4]),
        border=ft.Border(
            bottom=ft.BorderSide(1, theme.SURFACE_BORDER),
            left=ft.BorderSide(1, theme.SURFACE_BORDER)
        ),
        min_y=0,
        max_y=max(max_w * 1.15, water_target * 1.2),
        interactive=True,
        expand=True,
        tooltip_bgcolor=theme.SURFACE_CARD,
    )

    water_chart_card = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Row([
                    ft.Icon(ft.Icons.BAR_CHART_ROUNDED, size=16, color=theme.COLOR_WATER_LIGHT),
                    ft.Text("Hidratación Diaria vs Objetivo", size=13, weight=ft.FontWeight.W_700, color=theme.TEXT_PRIMARY),
                ], spacing=6),
                ft.Container(
                    content=ft.Text(f"Meta: {water_target} ml", size=10, color=theme.COLOR_WATER_LIGHT, weight=ft.FontWeight.W_600),
                    bgcolor=theme.COLOR_WATER_BG,
                    padding=ft.Padding(left=6, top=3, right=6, bottom=3),
                    border_radius=8
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=4),
            ft.Container(content=water_bar_chart, height=150, padding=ft.Padding(left=4, top=4, right=14, bottom=0))
        ], spacing=4),
        bgcolor=theme.SURFACE_CARD,
        padding=14,
        border_radius=16,
        border=ft.border.all(1, theme.SURFACE_BORDER),
    )

    def open_date_detail_dialog(date_str):
        date_entries = db.get_diary_entries(date_str)
        date_water = db.get_water_for_date(date_str)
        
        total_cal = int(sum(e['calories'] for e in date_entries))
        total_prot = int(sum(e['protein'] for e in date_entries))
        total_carb = int(sum(e['carbs'] for e in date_entries))
        total_fat = int(sum(e['fat'] for e in date_entries))
        
        try:
            d_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            formatted_date = f"{day_names_es[d_obj.weekday()]}, {d_obj.day:02d} de {months_es[d_obj.month - 1]} {d_obj.year}"
        except Exception:
            formatted_date = date_str
            
        cal_color = theme.DANGER if total_cal > target_cal else theme.PRIMARY
        is_today = (date_str == today_str)

        # Resumen organizado de métricas en 2 niveles (sin palabras cortadas)
        tier1_cal = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(ft.Icons.LOCAL_FIRE_DEPARTMENT_ROUNDED, size=18, color=cal_color),
                    bgcolor=theme.with_opacity(0.18, cal_color),
                    padding=6,
                    border_radius=8,
                ),
                ft.Column([
                    ft.Text("Calorías", size=10, color=theme.TEXT_SECONDARY),
                    ft.Text(f"{total_cal} kcal", size=13, weight=ft.FontWeight.W_700, color=cal_color),
                ], spacing=1, expand=True),
            ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=theme.SURFACE_VARIANT,
            padding=ft.Padding(10, 8, 10, 8),
            border_radius=10,
            border=ft.border.all(1, theme.SURFACE_BORDER),
            expand=True
        )

        tier1_water = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(ft.Icons.WATER_DROP_ROUNDED, size=18, color=theme.COLOR_WATER_LIGHT),
                    bgcolor=theme.COLOR_WATER_BG,
                    padding=6,
                    border_radius=8,
                ),
                ft.Column([
                    ft.Text("Agua", size=10, color=theme.TEXT_SECONDARY),
                    ft.Text(f"{date_water} ml", size=13, weight=ft.FontWeight.W_700, color=theme.COLOR_WATER_LIGHT),
                ], spacing=1, expand=True),
            ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=theme.SURFACE_VARIANT,
            padding=ft.Padding(10, 8, 10, 8),
            border_radius=10,
            border=ft.border.all(1, theme.SURFACE_BORDER),
            expand=True
        )

        tier2_prot = ft.Container(
            content=ft.Column([
                ft.Text("Proteína", size=10.5, color=theme.COLOR_PROTEIN_LIGHT, weight=ft.FontWeight.W_600),
                ft.Text(f"{total_prot}g", size=12.5, weight=ft.FontWeight.W_700, color=theme.TEXT_PRIMARY),
            ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=theme.COLOR_PROTEIN_BG,
            padding=ft.Padding(6, 6, 6, 6),
            border_radius=8,
            border=ft.border.all(1, theme.with_opacity(0.3, theme.COLOR_PROTEIN)),
            expand=True
        )

        tier2_carbs = ft.Container(
            content=ft.Column([
                ft.Text("Carbos", size=10.5, color=theme.COLOR_CARBS_LIGHT, weight=ft.FontWeight.W_600),
                ft.Text(f"{total_carb}g", size=12.5, weight=ft.FontWeight.W_700, color=theme.TEXT_PRIMARY),
            ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=theme.COLOR_CARBS_BG,
            padding=ft.Padding(6, 6, 6, 6),
            border_radius=8,
            border=ft.border.all(1, theme.with_opacity(0.3, theme.COLOR_CARBS)),
            expand=True
        )

        tier2_fat = ft.Container(
            content=ft.Column([
                ft.Text("Grasas", size=10.5, color=theme.COLOR_FAT_LIGHT, weight=ft.FontWeight.W_600),
                ft.Text(f"{total_fat}g", size=12.5, weight=ft.FontWeight.W_700, color=theme.TEXT_PRIMARY),
            ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=theme.COLOR_FAT_BG,
            padding=ft.Padding(6, 6, 6, 6),
            border_radius=8,
            border=ft.border.all(1, theme.with_opacity(0.3, theme.COLOR_FAT)),
            expand=True
        )

        metrics_summary = ft.Column([
            ft.Row([tier1_cal, tier1_water], spacing=8),
            ft.Row([tier2_prot, tier2_carbs, tier2_fat], spacing=8),
        ], spacing=6)

        foods_content = []
        if not date_entries:
            foods_content.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.NO_FOOD_ROUNDED, size=32, color=theme.TEXT_MUTED),
                        ft.Text("No se registraron comidas en esta fecha.", size=12, color=theme.TEXT_SECONDARY),
                        ft.Text(f"Hidratación registrada: {date_water} ml", size=11, color=theme.COLOR_WATER_LIGHT),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                    padding=20,
                    alignment=ft.Alignment(0, 0)
                )
            )
        else:
            grouped = {
                "Desayuno": {"icon": ft.Icons.WB_SUNNY_ROUNDED, "color": theme.COLOR_CARBS, "items": []},
                "Almuerzo": {"icon": ft.Icons.SUNNY, "color": theme.PRIMARY, "items": []},
                "Cena": {"icon": ft.Icons.NIGHTLIGHT_ROUNDED, "color": theme.COLOR_PROTEIN, "items": []},
                "Snack": {"icon": ft.Icons.COOKIE_ROUNDED, "color": theme.SECONDARY, "items": []}
            }
            for e in date_entries:
                m = e.get('meal_type', 'Snack')
                if m not in grouped:
                    grouped[m] = {"icon": ft.Icons.RESTAURANT_ROUNDED, "color": theme.PRIMARY, "items": []}
                grouped[m]["items"].append(e)

            for meal_name, data in grouped.items():
                items = data["items"]
                if not items:
                    continue
                meal_cals = sum(i['calories'] for i in items)
                foods_content.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Row([
                                ft.Icon(data["icon"], size=15, color=data["color"]),
                                ft.Text(meal_name, size=13, weight=ft.FontWeight.W_700, color=theme.TEXT_PRIMARY),
                            ], spacing=6),
                            theme.badge(f"{int(meal_cals)} kcal", icon=ft.Icons.BOLT_ROUNDED, bg_color=theme.SURFACE_VARIANT, text_color=theme.PRIMARY_LIGHT, font_size=10)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        padding=ft.Padding(2, 6, 2, 2)
                    )
                )
                for itm in items:
                    fname = itm['food_name']
                    is_portion = "porción" in fname.lower()
                    is_liquid = any(w in fname.lower() for w in ['leche', 'jugo', 'agua', 'yogur', 'aceite'])
                    if is_portion:
                        qty_str = f"{itm['amount_g'] / 100.0:g} porción"
                    elif is_liquid:
                        qty_str = f"{itm['amount_g']:g} ml"
                    else:
                        qty_str = f"{itm['amount_g']:g} g"

                    foods_content.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Text(fname, size=12.5, weight=ft.FontWeight.W_600, color=theme.TEXT_PRIMARY, expand=True),
                                    ft.Text(f"{int(itm['calories'])} kcal", size=12, weight=ft.FontWeight.W_700, color=theme.PRIMARY_LIGHT),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ft.Row([
                                    ft.Text(qty_str, size=10.5, color=theme.TEXT_SECONDARY),
                                    ft.Text("•", size=10, color=theme.TEXT_MUTED),
                                    ft.Text(f"P: {int(itm['protein'])}g", size=10, color=theme.COLOR_PROTEIN_LIGHT, weight=ft.FontWeight.W_600),
                                    ft.Text(f"C: {int(itm['carbs'])}g", size=10, color=theme.COLOR_CARBS_LIGHT, weight=ft.FontWeight.W_600),
                                    ft.Text(f"G: {int(itm['fat'])}g", size=10, color=theme.COLOR_FAT_LIGHT, weight=ft.FontWeight.W_600),
                                ], spacing=6)
                            ], spacing=2),
                            padding=ft.Padding(10, 6, 10, 6),
                            bgcolor=theme.SURFACE_VARIANT,
                            border_radius=10,
                            border=ft.border.all(1, theme.SURFACE_BORDER)
                        )
                    )

        title_widgets = [
            ft.Row([
                ft.Icon(ft.Icons.CALENDAR_MONTH_ROUNDED, color=theme.PRIMARY_LIGHT, size=18),
                ft.Text(formatted_date, size=13, weight=ft.FontWeight.W_700, color=theme.TEXT_PRIMARY),
            ], spacing=6, expand=True)
        ]
        if is_today:
            title_widgets.append(theme.badge("Hoy", bg_color=theme.PRIMARY, text_color="white", font_size=10))

        dlg = ft.AlertDialog(
            title=ft.Row(title_widgets, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            content=ft.Container(
                content=ft.Column([
                    metrics_summary,
                    ft.Divider(color=theme.SURFACE_BORDER, height=1),
                    ft.Row([
                        theme.subheader_text("Alimentos Consumidos"),
                        theme.badge(f"{len(date_entries)} items", bg_color=theme.SURFACE_VARIANT, text_color=theme.TEXT_SECONDARY, font_size=10)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Container(content=ft.ListView(foods_content, spacing=6), height=240)
                ], tight=True, spacing=10),
                width=340,
            ),
            actions=[
                ft.ElevatedButton(
                    "Cerrar", 
                    on_click=lambda _: close_dlg(dlg), 
                    style=ft.ButtonStyle(
                        color=theme.TEXT_PRIMARY,
                        bgcolor=theme.SURFACE_VARIANT,
                        shape=ft.RoundedRectangleBorder(radius=10),
                        padding=ft.Padding(18, 10, 18, 10),
                        side=ft.BorderSide(1, theme.SURFACE_BORDER),
                    )
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=theme.SURFACE_CARD,
        )
        def close_dlg(d):
            d.open = False
            page.update()

        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def on_date_picked(e):
        if date_picker.value:
            picked_str = date_picker.value.strftime('%Y-%m-%d')
            open_date_detail_dialog(picked_str)

    date_picker = ft.DatePicker(
        on_change=on_date_picked,
        first_date=datetime.datetime(2020, 1, 1),
        last_date=datetime.datetime.now() + datetime.timedelta(days=1),
        help_text="Seleccionar fecha",
        cancel_text="Cancelar",
        confirm_text="Aceptar",
        error_format_text="Formato de fecha inválido",
        error_invalid_text="Fecha fuera de rango",
        field_hint_text="dd/mm/aaaa",
        field_label_text="Ingresar fecha",
    )
    page.overlay.append(date_picker)

    def open_calendar(e):
        try:
            page.open(date_picker)
        except Exception:
            date_picker.open = True
            page.update()

    def export_csv(e):
        if not history_data:
            page.snack_bar = theme.create_snackbar(
                content=ft.Text("No hay registros históricos para exportar.", size=13, color=theme.TEXT_PRIMARY),
                bgcolor=theme.SURFACE_CARD,
                duration=3000
            )
            page.snack_bar.open = True
            page.update()
            return
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

    header = ft.Column([
        ft.Column([
            theme.header_text("Historial y Métricas"),
            ft.Text("Evolución semanal y balance de macros", size=12, color=theme.TEXT_SECONDARY)
        ], spacing=2),
        ft.Row([
            ft.ElevatedButton(
                "Ver Fecha", 
                icon=ft.Icons.CALENDAR_MONTH_ROUNDED, 
                on_click=open_calendar, 
                style=ft.ButtonStyle(
                    color=theme.TEXT_PRIMARY,
                    bgcolor=theme.SURFACE_VARIANT,
                    shape=ft.RoundedRectangleBorder(radius=12),
                    padding=ft.Padding(left=12, top=9, right=14, bottom=9),
                    side=ft.BorderSide(1, theme.SURFACE_BORDER),
                ),
                expand=True
            ),
            ft.ElevatedButton(
                "Exportar Historial", 
                icon=ft.Icons.DOWNLOAD_ROUNDED, 
                on_click=export_csv, 
                style=ft.ButtonStyle(
                    color=theme.PRIMARY_LIGHT,
                    bgcolor=theme.PRIMARY_BG,
                    shape=ft.RoundedRectangleBorder(radius=12),
                    padding=ft.Padding(left=12, top=9, right=14, bottom=9),
                    side=ft.BorderSide(1, theme.with_opacity(0.3, theme.PRIMARY)),
                ),
                expand=True
            )
        ], spacing=8)
    ], spacing=10)

    content_cols = [
        header,
        ft.Container(height=4),
        cal_chart_card,
        water_chart_card,
        ft.Container(height=6),
        ft.Row([
            theme.subheader_text("Registros Pasados"),
            theme.badge(f"{len(history_data)} días", icon=ft.Icons.HISTORY_ROUNDED, bg_color=theme.SURFACE_VARIANT, text_color=theme.TEXT_SECONDARY, font_size=10)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    ]
    
    if not history_data:
        content_cols.append(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.CALENDAR_MONTH_ROUNDED, size=36, color=theme.TEXT_MUTED),
                    ft.Text("Aún no tienes registros históricos.", size=13, weight=ft.FontWeight.W_600, color=theme.TEXT_PRIMARY),
                    ft.Text("Registra tus comidas en el Diario hoy para ver aquí tus días anteriores.", size=11.5, color=theme.TEXT_SECONDARY),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                alignment=ft.Alignment(0, 0),
                padding=20,
                bgcolor=theme.SURFACE_CARD,
                border_radius=14,
                border=ft.border.all(1, theme.SURFACE_BORDER)
            )
        )
    
    # -------------------------------------------------------------
    # 4. AGRUPACIÓN MENSUAL Y TARJETAS DETALLADAS
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
            padding=ft.Padding(left=4, top=6, right=4, bottom=2)
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

            day_title_row = [
                ft.Icon(ft.Icons.EVENT_NOTE_ROUNDED, color=theme.TEXT_SECONDARY, size=16),
                ft.Text(day_str, weight=ft.FontWeight.W_700, size=13.5, color=theme.TEXT_PRIMARY),
            ]
            if db_date_str == today_str:
                day_title_row.append(theme.badge("Hoy", bg_color=theme.PRIMARY, text_color="white", font_size=9))

            day_card = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Row(day_title_row, spacing=6),
                        ft.Row([
                            ft.Container(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.BOLT_ROUNDED, color=cal_color, size=13),
                                    ft.Text(f"{cal} / {target_cal} kcal", color=cal_color, weight=ft.FontWeight.W_700, size=11.5),
                                ], spacing=3),
                                bgcolor=theme.SURFACE_VARIANT,
                                padding=ft.Padding(left=8, top=3, right=8, bottom=3),
                                border_radius=8,
                            ),
                            ft.IconButton(
                                ft.Icons.DELETE_OUTLINE_ROUNDED, 
                                icon_color=theme.DANGER_LIGHT, 
                                icon_size=17, 
                                tooltip="Eliminar día",
                                on_click=delete_day_click
                            )
                        ], spacing=2)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    
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
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                    ft.Container(height=2),
                    ft.Row([
                        ft.Row([
                            ft.Icon(ft.Icons.RESTAURANT_MENU_ROUNDED, size=13, color=theme.PRIMARY_LIGHT),
                            ft.Text("Toca para ver qué comiste", size=11, color=theme.PRIMARY_LIGHT, weight=ft.FontWeight.W_500),
                        ], spacing=4),
                        ft.Icon(ft.Icons.CHEVRON_RIGHT_ROUNDED, size=16, color=theme.PRIMARY_LIGHT)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ], spacing=6),
                padding=12,
                bgcolor=theme.SURFACE_CARD,
                border_radius=14,
                border=ft.border.all(1, theme.SURFACE_BORDER),
                margin=ft.Margin(0, 0, 0, 6),
                animate=theme.STANDARD_ANIMATION,
                on_click=lambda e, d_str=db_date_str: open_date_detail_dialog(d_str),
                ink=True
            )
            content_cols.append(day_card)

    return ft.Column(content_cols, expand=True, scroll=ft.ScrollMode.HIDDEN, spacing=4)

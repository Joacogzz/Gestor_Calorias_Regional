import flet as ft
import database as db
from ui import theme

ACTIVITY_FACTORS = {
    "Sedentario: poco o nada de ejercicio al día": 1.2,
    "Actividad ligera: ejercicio ligero o deporte 1-3 días a la semana": 1.375,
    "Actividad moderada: ejercicio moderado o deporte 3-5 días a la semana": 1.55,
    "Actividad intensa: ejercicio intenso o deporte 6-7 días a la semana": 1.725,
    "Actividad muy intensa: ejercicio muy intenso o trabajo físico y ejercicio diario": 1.9,
}

def get_profile_view(page: ft.Page, on_save_callback):
    profiles = db.get_profiles()
    active_profile = db.get_profile()
    
    # -------------------------------------------------------------
    # 1. SELECTOR DE PERFILES
    # -------------------------------------------------------------
    profile_options = [ft.dropdown.Option(key=str(p['id']), text=p['name']) for p in profiles]
    
    def on_profile_change(e):
        if profile_dropdown.value == "NEW":
            name_input.value = ""
            age_input.value = ""
            weight_input.value = ""
            height_input.value = ""
            gender_dropdown.value = "Hombre"
            activity_dropdown.value = "Actividad moderada: ejercicio moderado o deporte 3-5 días a la semana"
            goal_dropdown.value = "Mantenimiento"
            save_btn.visible = True
            macro_info.visible = False
        else:
            db.set_active_profile_id(int(profile_dropdown.value))
            if on_save_callback:
                on_save_callback()
            
        page.update()

    profile_dropdown = ft.Dropdown(
        label="Perfil Activo",
        options=[ft.dropdown.Option(key="NEW", text="+ Crear Nuevo Perfil")] + profile_options,
        value=str(active_profile['id']) if active_profile else "NEW",
        border_color=theme.SURFACE_BORDER,
        focused_border_color=theme.PRIMARY,
        color=theme.TEXT_PRIMARY,
        border_radius=14,
        filled=True,
        fill_color=theme.SURFACE_VARIANT,
        expand=True
    )
    profile_dropdown.on_select = on_profile_change
    
    # Referencias de Macros
    macro_cal = ft.Text(f"{active_profile['target_calories'] if active_profile else 0} kcal", size=15, weight=ft.FontWeight.W_800, color=theme.PRIMARY_LIGHT)
    macro_prot = ft.Text(f"{int(active_profile['target_protein']) if active_profile else 0}g", size=15, weight=ft.FontWeight.W_800, color=theme.COLOR_PROTEIN_LIGHT)
    macro_carbs = ft.Text(f"{int(active_profile['target_carbs']) if active_profile else 0}g", size=15, weight=ft.FontWeight.W_800, color=theme.COLOR_CARBS_LIGHT)
    macro_fat = ft.Text(f"{int(active_profile['target_fat']) if active_profile else 0}g", size=15, weight=ft.FontWeight.W_800, color=theme.COLOR_FAT_LIGHT)

    def auto_recalculate(e=None):
        if goal_dropdown.value == "Mantenimiento":
            modifier_input.visible = False
        else:
            modifier_input.visible = True

        try:
            w = float(weight_input.value)
            h = float(height_input.value)
            a = int(age_input.value)
            g = gender_dropdown.value
            goal = goal_dropdown.value
            
            # Fórmula científica Mifflin-St Jeor
            if g == "Hombre":
                bmr = 10 * w + 6.25 * h - 5 * a + 5
            else:
                bmr = 10 * w + 6.25 * h - 5 * a - 161
                
            factor = ACTIVITY_FACTORS.get(activity_dropdown.value, 1.55)
            tdee = bmr * factor
            
            try:
                mod = int(modifier_input.value)
            except:
                mod = 500
            
            if goal == "Déficit (Perder Grasa)":
                target_cal = int(tdee - mod)
            elif goal == "Superávit (Ganar Masa)":
                target_cal = int(tdee + mod)
            else:
                target_cal = int(tdee)
                
            target_prot = w * 2.0
            target_fat = w * 0.8
            carb_cals = target_cal - (target_prot * 4) - (target_fat * 9)
            target_carbs = max(0, carb_cals / 4.0)
            
            if e and e.control == weight_input:
                water_input.value = str(int(w * 35))
            
            try: water_g = int(water_input.value)
            except: water_g = 2000
            
            # Actualizar textos
            macro_cal.value = f"{target_cal} kcal"
            macro_prot.value = f"{int(target_prot)}g"
            macro_carbs.value = f"{int(target_carbs)}g"
            macro_fat.value = f"{int(target_fat)}g"
            
            # Auto guardar si no es nuevo
            if profile_dropdown.value != "NEW":
                db.update_profile(int(profile_dropdown.value), name_input.value, g, a, w, h, goal, target_cal, target_prot, target_carbs, target_fat, water_g, activity_dropdown.value)
            
            page.update()
        except ValueError:
            page.update()

    # -------------------------------------------------------------
    # 2. CAMPOS DEL FORMULARIO
    # -------------------------------------------------------------
    name_input = ft.TextField(
        **theme.get_input_style("Nombre o Alias", ft.Icons.PERSON_ROUNDED), 
        value=active_profile['name'] if active_profile else "", 
        on_change=auto_recalculate
    )
    
    gender_dropdown = ft.Dropdown(
        label="Sexo Biológico",
        options=[ft.dropdown.Option("Hombre"), ft.dropdown.Option("Mujer")],
        value=active_profile['gender'] if active_profile else "Hombre",
        border_color=theme.SURFACE_BORDER,
        focused_border_color=theme.PRIMARY,
        color=theme.TEXT_PRIMARY,
        border_radius=14,
        filled=True,
        fill_color=theme.SURFACE_VARIANT,
        expand=True
    )
    gender_dropdown.on_select = auto_recalculate
    
    age_input = ft.TextField(
        **theme.get_input_style("Edad", ft.Icons.CALENDAR_TODAY_ROUNDED), 
        value=str(active_profile['age']) if active_profile else "", 
        keyboard_type=ft.KeyboardType.NUMBER, 
        on_change=auto_recalculate,
        expand=True
    )
    weight_input = ft.TextField(
        **theme.get_input_style("Peso Actual (kg)", ft.Icons.SCALE_ROUNDED), 
        value=str(active_profile['weight']) if active_profile else "", 
        keyboard_type=ft.KeyboardType.NUMBER, 
        on_change=auto_recalculate,
        expand=True
    )
    height_input = ft.TextField(
        **theme.get_input_style("Altura (cm)", ft.Icons.HEIGHT_ROUNDED), 
        value=str(active_profile['height']) if active_profile else "", 
        keyboard_type=ft.KeyboardType.NUMBER, 
        on_change=auto_recalculate,
        expand=True
    )
    
    current_goal = active_profile['goal'] if active_profile else "Mantenimiento"
    
    mod_val = "500"
    if active_profile and current_goal != "Mantenimiento":
        try:
            w_val = float(active_profile.get('weight', 0))
            h_val = float(active_profile.get('height', 0))
            a_val = int(active_profile.get('age', 0))
            g_val = active_profile.get('gender', 'Hombre')
            if g_val == "Hombre":
                bmr_val = 10 * w_val + 6.25 * h_val - 5 * a_val + 5
            else:
                bmr_val = 10 * w_val + 6.25 * h_val - 5 * a_val - 161
            act_val = active_profile.get('activity_level', '')
            factor_val = ACTIVITY_FACTORS.get(act_val, 1.55)
            tdee_val = bmr_val * factor_val
            
            target_cal_val = int(active_profile.get('target_calories', tdee_val))
            mod_calc = abs(target_cal_val - int(tdee_val))
            if mod_calc > 0:
                mod_val = str(int(mod_calc))
        except Exception:
            mod_val = "500"

    current_activity = active_profile.get('activity_level', 'Actividad moderada: ejercicio moderado o deporte 3-5 días a la semana') if active_profile else "Actividad moderada: ejercicio moderado o deporte 3-5 días a la semana"
    if current_activity not in ACTIVITY_FACTORS:
        current_activity = "Actividad moderada: ejercicio moderado o deporte 3-5 días a la semana"

    activity_dropdown = ft.Dropdown(
        label="Nivel de Actividad Física",
        options=[
            ft.dropdown.Option("Sedentario: poco o nada de ejercicio al día"),
            ft.dropdown.Option("Actividad ligera: ejercicio ligero o deporte 1-3 días a la semana"),
            ft.dropdown.Option("Actividad moderada: ejercicio moderado o deporte 3-5 días a la semana"),
            ft.dropdown.Option("Actividad intensa: ejercicio intenso o deporte 6-7 días a la semana"),
            ft.dropdown.Option("Actividad muy intensa: ejercicio muy intenso o trabajo físico y ejercicio diario"),
        ],
        value=current_activity,
        border_color=theme.SURFACE_BORDER,
        focused_border_color=theme.PRIMARY,
        color=theme.TEXT_PRIMARY,
        border_radius=14,
        filled=True,
        fill_color=theme.SURFACE_VARIANT,
    )
    activity_dropdown.on_select = auto_recalculate

    goal_dropdown = ft.Dropdown(
        label="Objetivo Nutricional",
        options=[
            ft.dropdown.Option("Déficit (Perder Grasa)"),
            ft.dropdown.Option("Mantenimiento"),
            ft.dropdown.Option("Superávit (Ganar Masa)")
        ],
        value=current_goal,
        border_color=theme.SURFACE_BORDER,
        focused_border_color=theme.PRIMARY,
        color=theme.TEXT_PRIMARY,
        border_radius=14,
        filled=True,
        fill_color=theme.SURFACE_VARIANT,
    )
    goal_dropdown.on_select = auto_recalculate
    
    modifier_input = ft.TextField(
        **theme.get_input_style("Ajuste Calórico (+/- Kcal)", ft.Icons.TUNE_ROUNDED), 
        value=mod_val, 
        keyboard_type=ft.KeyboardType.NUMBER,
        visible=(current_goal != "Mantenimiento"),
        on_change=auto_recalculate
    )

    water_input = ft.TextField(
        **theme.get_input_style("Meta de Agua Diaria (ml)", ft.Icons.WATER_DROP_ROUNDED),
        value=str(active_profile.get('water_goal', 2000)) if active_profile else "2000",
        keyboard_type=ft.KeyboardType.NUMBER,
        on_change=auto_recalculate
    )

    def save_new_profile_click(e):
        try:
            w = float(weight_input.value)
            h = float(height_input.value)
            a = int(age_input.value)
            g = gender_dropdown.value
            goal = goal_dropdown.value
            try: water_g = int(water_input.value)
            except: water_g = 2000
            
            if g == "Hombre":
                bmr = 10 * w + 6.25 * h - 5 * a + 5
            else:
                bmr = 10 * w + 6.25 * h - 5 * a - 161
                
            factor = ACTIVITY_FACTORS.get(activity_dropdown.value, 1.55)
            tdee = bmr * factor
            try: mod = int(modifier_input.value)
            except: mod = 500
            
            if goal == "Déficit (Perder Grasa)":
                target_cal = int(tdee - mod)
            elif goal == "Superávit (Ganar Masa)":
                target_cal = int(tdee + mod)
            else:
                target_cal = int(tdee)
                
            target_prot = w * 2.0
            target_fat = w * 0.8
            carb_cals = target_cal - (target_prot * 4) - (target_fat * 9)
            target_carbs = max(0, carb_cals / 4.0)
                
            db.save_profile(name_input.value, g, a, w, h, goal, target_cal, target_prot, target_carbs, target_fat, water_g, activity_dropdown.value)
            
            page.snack_bar = theme.create_snackbar(ft.Text("¡Perfil creado exitosamente!"), bgcolor=theme.PRIMARY)
            page.snack_bar.open = True
            if on_save_callback:
                on_save_callback()
                
        except ValueError:
            page.snack_bar = theme.create_snackbar(ft.Text("Ingresa valores numéricos válidos."), bgcolor=theme.DANGER_BG)
            page.snack_bar.open = True
            page.update()

    save_btn = ft.ElevatedButton(
        "Guardar Perfil Nuevo", 
        icon=ft.Icons.CHECK_ROUNDED,
        on_click=save_new_profile_click, 
        style=theme.get_button_style(), 
        width=float('inf'), 
        visible=(profile_dropdown.value == "NEW")
    )

    def delete_profile_click(e):
        if active_profile:
            db.delete_profile(active_profile['id'])
            page.snack_bar = theme.create_snackbar(ft.Text("Perfil eliminado."), bgcolor=theme.SURFACE_CARD)
            page.snack_bar.open = True
            page.update()
            if on_save_callback:
                on_save_callback()

    delete_btn = ft.IconButton(
        ft.Icons.DELETE_OUTLINE_ROUNDED, 
        icon_color=theme.DANGER_LIGHT, 
        tooltip="Eliminar perfil actual",
        on_click=delete_profile_click
    ) if active_profile else ft.Container()
    
    profile_row = ft.Row([profile_dropdown, delete_btn], spacing=6)

    def toggle_theme(e):
        mode_str = "dark" if e.control.value else "light"
        db.set_theme_mode(mode_str)
        page.theme_mode = ft.ThemeMode.DARK if mode_str == "dark" else ft.ThemeMode.LIGHT
        page.bgcolor = theme.BG_OBSIDIAN if page.theme_mode == ft.ThemeMode.DARK else "#F8FAFC"
        page.update()

    theme_switch = ft.Switch(
        label="Modo Obsidiana / Oscuro", 
        value=page.theme_mode == ft.ThemeMode.DARK,
        on_change=toggle_theme,
        active_color=theme.PRIMARY
    )

    # Pastillas resumen de macros calculados
    macro_info = ft.Container(
        content=ft.Row([
            ft.Column([
                ft.Text("Calorías", color=theme.TEXT_SECONDARY, size=11), 
                macro_cal
            ], spacing=1),
            ft.Column([
                ft.Text("Proteínas", color=theme.TEXT_SECONDARY, size=11), 
                macro_prot
            ], spacing=1),
            ft.Column([
                ft.Text("Carbos", color=theme.TEXT_SECONDARY, size=11), 
                macro_carbs
            ], spacing=1),
            ft.Column([
                ft.Text("Grasas", color=theme.TEXT_SECONDARY, size=11), 
                macro_fat
            ], spacing=1),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=14,
        bgcolor=theme.SURFACE_VARIANT,
        border_radius=14,
        border=ft.border.all(1, theme.SURFACE_BORDER),
        visible=(profile_dropdown.value != "NEW")
    )

    card_content = ft.Column([
        profile_row,
        macro_info,
        name_input,
        ft.Row([gender_dropdown, age_input], spacing=10),
        ft.Row([weight_input, height_input], spacing=10),
        activity_dropdown,
        goal_dropdown,
        modifier_input,
        water_input,
        save_btn,
        ft.Divider(color=theme.SURFACE_BORDER, height=1),
        ft.Row([
            ft.Icon(ft.Icons.DARK_MODE_ROUNDED, color=theme.PRIMARY_LIGHT, size=20), 
            theme_switch
        ], alignment=ft.MainAxisAlignment.START, spacing=8)
    ], spacing=12)
    
    # -------------------------------------------------------------
    # 3. GRÁFICO HISTÓRICO DE PESO
    # -------------------------------------------------------------
    chart_container = ft.Container()
    if active_profile:
        logs = db.get_weight_logs()
        if len(logs) > 1:
            data_points = []
            min_w = logs[0]['weight']
            max_w = logs[0]['weight']
            
            for i, l in enumerate(logs):
                w = l['weight']
                data_points.append(ft.LineChartDataPoint(i, w))
                if w < min_w: min_w = w
                if w > max_w: max_w = w
                
            chart = ft.LineChart(
                data_series=[
                    ft.LineChartData(
                        data_points=data_points,
                        stroke_width=3.5,
                        color=theme.PRIMARY,
                        curved=True,
                        stroke_cap_round=True,
                    )
                ],
                border=ft.Border(
                    bottom=ft.BorderSide(1, theme.SURFACE_BORDER),
                    left=ft.BorderSide(1, theme.SURFACE_BORDER),
                ),
                min_y=min_w - 3,
                max_y=max_w + 3,
                min_x=0,
                max_x=len(logs)-1,
                tooltip_bgcolor=theme.SURFACE_CARD,
                expand=True,
            )
            
            chart_container = ft.Container(
                content=ft.Column([
                    ft.Row([
                        theme.subheader_text("Historial de Peso"),
                        theme.badge(f"{len(logs)} registros", icon=ft.Icons.TRENDING_UP_ROUNDED, bg_color=theme.SURFACE_VARIANT, text_color=theme.TEXT_SECONDARY, font_size=10)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Container(content=chart, height=180, padding=10)
                ], spacing=8),
                **theme.get_card_style(padding=16)
            )

    return ft.Column([
        theme.header_text("Configuración de Perfil"),
        ft.Container(
            content=card_content,
            **theme.get_card_style(padding=16)
        ),
        chart_container
    ], expand=True, scroll=ft.ScrollMode.AUTO, spacing=6)

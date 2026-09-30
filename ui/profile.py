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
    
    # --- SELECTOR DE PERFIL ---
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
        else:
            db.set_active_profile_id(int(profile_dropdown.value))
            # Recargar la vista con el perfil seleccionado
            
            # En vez de redirigir al dashboard, mejor reconstruimos la vista del perfil
            # Pero como solo tenemos un callback, redirigiremos al dashboard que forzará una recarga.
            on_save_callback()
            
        page.update()

    profile_dropdown = ft.Dropdown(
        label="Seleccionar Perfil",
        options=[ft.dropdown.Option(key="NEW", text="+ Crear Nuevo Perfil")] + profile_options,
        value=str(active_profile['id']) if active_profile else "NEW",
        border_color=theme.PRIMARY,
        color=theme.TEXT_PRIMARY,
        border_radius=10,
        filled=True,
        fill_color=theme.SURFACE_VARIANT,
    )
    profile_dropdown.on_select = on_profile_change
    
    # --- MACRO INFO REFS ---
    macro_cal = theme.normal_text(f"{active_profile['target_calories'] if active_profile else 0} kcal", weight=ft.FontWeight.BOLD)
    macro_prot = theme.normal_text(f"{int(active_profile['target_protein']) if active_profile else 0}g", weight=ft.FontWeight.BOLD)
    macro_carbs = theme.normal_text(f"{int(active_profile['target_carbs']) if active_profile else 0}g", weight=ft.FontWeight.BOLD)
    macro_fat = theme.normal_text(f"{int(active_profile['target_fat']) if active_profile else 0}g", weight=ft.FontWeight.BOLD)

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
            
            # Si el usuario modificó explícitamente el peso, actualizamos su meta de agua sugerida
            if e and e.control == weight_input:
                water_input.value = str(int(w * 35))
            
            try: water_g = int(water_input.value)
            except: water_g = 2000
            
            # Update labels
            macro_cal.value = f"{target_cal} kcal"
            macro_prot.value = f"{int(target_prot)}g"
            macro_carbs.value = f"{int(target_carbs)}g"
            macro_fat.value = f"{int(target_fat)}g"
            
            # Auto save if not NEW
            if profile_dropdown.value != "NEW":
                db.update_profile(int(profile_dropdown.value), name_input.value, g, a, w, h, goal, target_cal, target_prot, target_carbs, target_fat, water_g, activity_dropdown.value)
            
            page.update()
        except ValueError:
            # Ignorar mientras se escribe
            page.update()

    # --- FORMULARIO ---
    name_input = ft.TextField(**theme.get_input_style("Nombre", ft.Icons.PERSON), value=active_profile['name'] if active_profile else "", on_change=auto_recalculate)
    
    gender_dropdown = ft.Dropdown(
        label="Sexo",
        options=[ft.dropdown.Option("Hombre"), ft.dropdown.Option("Mujer")],
        value=active_profile['gender'] if active_profile else "Hombre",
        border_color=theme.PRIMARY,
        color=theme.TEXT_PRIMARY,
        border_radius=10,
        filled=True,
        fill_color=theme.SURFACE_VARIANT,
    )
    gender_dropdown.on_select = auto_recalculate
    
    age_input = ft.TextField(**theme.get_input_style("Edad", ft.Icons.CALENDAR_TODAY), value=str(active_profile['age']) if active_profile else "", keyboard_type=ft.KeyboardType.NUMBER, on_change=auto_recalculate)
    weight_input = ft.TextField(**theme.get_input_style("Peso (kg)", ft.Icons.SCALE), value=str(active_profile['weight']) if active_profile else "", keyboard_type=ft.KeyboardType.NUMBER, on_change=auto_recalculate)
    height_input = ft.TextField(**theme.get_input_style("Altura (cm)", ft.Icons.HEIGHT), value=str(active_profile['height']) if active_profile else "", keyboard_type=ft.KeyboardType.NUMBER, on_change=auto_recalculate)
    
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
            
            target_cal = int(active_profile.get('target_calories', tdee_val))
            mod_calc = abs(target_cal - int(tdee_val))
            if mod_calc > 0:
                mod_val = str(int(mod_calc))
        except Exception as e:
            print("ERROR IN MOD_VAL:", e)
            mod_val = "500"

    current_activity = active_profile.get('activity_level', 'Actividad moderada: ejercicio moderado o deporte 3-5 días a la semana') if active_profile else "Actividad moderada: ejercicio moderado o deporte 3-5 días a la semana"
    if current_activity not in ACTIVITY_FACTORS:
        current_activity = "Actividad moderada: ejercicio moderado o deporte 3-5 días a la semana"

    activity_dropdown = ft.Dropdown(
        label="Nivel de Actividad Física Diaria",
        options=[
            ft.dropdown.Option("Sedentario: poco o nada de ejercicio al día"),
            ft.dropdown.Option("Actividad ligera: ejercicio ligero o deporte 1-3 días a la semana"),
            ft.dropdown.Option("Actividad moderada: ejercicio moderado o deporte 3-5 días a la semana"),
            ft.dropdown.Option("Actividad intensa: ejercicio intenso o deporte 6-7 días a la semana"),
            ft.dropdown.Option("Actividad muy intensa: ejercicio muy intenso o trabajo físico y ejercicio diario"),
        ],
        value=current_activity,
        border_color=theme.PRIMARY,
        color=theme.TEXT_PRIMARY,
        border_radius=10,
        filled=True,
        fill_color=theme.SURFACE_VARIANT,
    )
    activity_dropdown.on_select = auto_recalculate

    goal_dropdown = ft.Dropdown(
        label="Objetivo",
        options=[
            ft.dropdown.Option("Déficit (Perder Grasa)"),
            ft.dropdown.Option("Mantenimiento"),
            ft.dropdown.Option("Superávit (Ganar Masa)")
        ],
        value=current_goal,
        border_color=theme.PRIMARY,
        color=theme.TEXT_PRIMARY,
        border_radius=10,
        filled=True,
        fill_color=theme.SURFACE_VARIANT,
    )
    goal_dropdown.on_select = auto_recalculate
    
    modifier_input = ft.TextField(
        **theme.get_input_style("Ajuste de Objetivo (Kcal)", ft.Icons.TUNE), 
        value=mod_val, 
        keyboard_type=ft.KeyboardType.NUMBER,
        visible=(current_goal != "Mantenimiento"),
        on_change=auto_recalculate
    )

    water_input = ft.TextField(
        **theme.get_input_style("Meta de Agua (ml)", ft.Icons.WATER_DROP),
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
            
            page.snack_bar = ft.SnackBar(ft.Text(f"Perfil creado exitosamente!"), bgcolor=theme.PRIMARY)
            page.snack_bar.open = True
            if on_save_callback:
                on_save_callback()
                
        except ValueError:
            page.snack_bar = ft.SnackBar(ft.Text("Ingresa valores numéricos válidos."), bgcolor=theme.DANGER)
            page.snack_bar.open = True
            page.update()

    save_btn = ft.ElevatedButton("Crear Perfil", on_click=save_new_profile_click, style=theme.get_button_style(), width=float('inf'), visible=(profile_dropdown.value == "NEW"))

    profile_dropdown.expand = True

    def delete_profile_click(e):
        if active_profile:
            db.delete_profile(active_profile['id'])
            page.snack_bar = ft.SnackBar(ft.Text("Perfil eliminado."), bgcolor=theme.SECONDARY)
            page.snack_bar.open = True
            page.update()
            if on_save_callback:
                on_save_callback()

    delete_btn = ft.IconButton(ft.Icons.DELETE, icon_color=theme.DANGER, on_click=delete_profile_click) if active_profile else ft.Container()
    profile_row = ft.Row([profile_dropdown, delete_btn])

    def toggle_theme(e):
        mode_str = "dark" if e.control.value else "light"
        db.set_theme_mode(mode_str)
        page.theme_mode = ft.ThemeMode.DARK if mode_str == "dark" else ft.ThemeMode.LIGHT
        page.bgcolor = "#000000" if page.theme_mode == ft.ThemeMode.DARK else "#FFFFFF"
        page.update()

    theme_switch = ft.Switch(
        label="Modo Oscuro", 
        value=page.theme_mode == ft.ThemeMode.DARK,
        on_change=toggle_theme,
        active_color=theme.PRIMARY
    )

    macro_info = ft.Container(
        content=ft.Row([
            ft.Column([theme.normal_text("Calorías", color=theme.TEXT_SECONDARY), macro_cal]),
            ft.Column([theme.normal_text("Proteínas", color=theme.TEXT_SECONDARY), macro_prot]),
            ft.Column([theme.normal_text("Carbos", color=theme.TEXT_SECONDARY), macro_carbs]),
            ft.Column([theme.normal_text("Grasas", color=theme.TEXT_SECONDARY), macro_fat]),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=15,
        bgcolor=theme.SURFACE_VARIANT,
        border_radius=16,
        visible=(profile_dropdown.value != "NEW") # Ocultar en perfil nuevo hasta crearlo
    )

    card_content = ft.Column([
        profile_row,
        ft.Divider(color=theme.TEXT_SECONDARY),
        macro_info,
        name_input,
        ft.Row([ft.Container(gender_dropdown, expand=1), ft.Container(age_input, expand=1)]),
        ft.Row([ft.Container(weight_input, expand=1), ft.Container(height_input, expand=1)]),
        activity_dropdown,
        goal_dropdown,
        modifier_input,
        water_input,
        save_btn,
        ft.Divider(color=theme.TEXT_SECONDARY),
        ft.Row([ft.Icon(ft.Icons.NIGHTLIGHT_ROUND), theme_switch], alignment=ft.MainAxisAlignment.START)
    ], spacing=15)
    
    # --- GRÁFICO HISTÓRICO DE PESO ---
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
                        stroke_width=4,
                        color=theme.PRIMARY,
                        curved=True,
                        stroke_cap_round=True,
                    )
                ],
                border=ft.Border(
                    bottom=ft.BorderSide(1, theme.TEXT_SECONDARY),
                    left=ft.BorderSide(1, theme.TEXT_SECONDARY),
                ),
                min_y=min_w - 5,
                max_y=max_w + 5,
                min_x=0,
                max_x=len(logs)-1,
                tooltip_bgcolor=theme.SURFACE,
                expand=True,
            )
            
            chart_container = ft.Container(
                content=ft.Column([
                    theme.subheader_text("Historial de Peso"),
                    ft.Container(content=chart, height=200, padding=10)
                ]),
                **theme.get_card_style()
            )

    return ft.Column([
        theme.header_text("Gestión de Perfil"),
        ft.Container(
            content=card_content,
            **theme.get_card_style()
        ),
        chart_container
    ], expand=True, scroll=ft.ScrollMode.AUTO)

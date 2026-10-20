import flet as ft
import database as db
from ui import theme

ACTIVITY_FACTORS = {
    "Sedentario (Poco o nada)": 1.2,
    "Ligero (1 a 3 días/sem)": 1.375,
    "Moderado (3 a 5 días/sem)": 1.55,
    "Intenso (6 a 7 días/sem)": 1.725,
    "Muy Intenso (Físico diario)": 1.9,
    # Compatibilidad con registros previos:
    "Sedentario: poco o nada de ejercicio al día": 1.2,
    "Actividad ligera: ejercicio ligero o deporte 1-3 días a la semana": 1.375,
    "Actividad moderada: ejercicio moderado o deporte 3-5 días a la semana": 1.55,
    "Actividad intensa: ejercicio intenso o deporte 6-7 días a la semana": 1.725,
    "Actividad muy intensa: ejercicio muy intenso o trabajo físico y ejercicio diario": 1.9,
}

WATER_ACTIVITY_ADDITIONS = {
    "Sedentario (Poco o nada)": 0,
    "Ligero (1 a 3 días/sem)": 350,
    "Moderado (3 a 5 días/sem)": 500,
    "Intenso (6 a 7 días/sem)": 750,
    "Muy Intenso (Físico diario)": 1000,
    # Compatibilidad con registros previos:
    "Sedentario: poco o nada de ejercicio al día": 0,
    "Actividad ligera: ejercicio ligero o deporte 1-3 días a la semana": 350,
    "Actividad moderada: ejercicio moderado o deporte 3-5 días a la semana": 500,
    "Actividad intensa: ejercicio intenso o deporte 6-7 días a la semana": 750,
    "Actividad muy intensa: ejercicio muy intenso o trabajo físico y ejercicio diario": 1000,
}

def get_setup_view(page: ft.Page, on_finish):
    name_input = ft.TextField(
        **theme.get_input_style("Tu Nombre o Alias", ft.Icons.PERSON_ROUNDED),
        expand=True
    )
    
    gender_dropdown = ft.Dropdown(
        label="Sexo Biológico",
        options=[ft.dropdown.Option("Hombre"), ft.dropdown.Option("Mujer")],
        value="Hombre",
        border_color=theme.SURFACE_BORDER,
        focused_border_color=theme.PRIMARY,
        color=theme.TEXT_PRIMARY,
        border_radius=14,
        filled=True,
        fill_color=theme.SURFACE_VARIANT,
        expand=True
    )
    
    age_input = ft.TextField(
        **theme.get_input_style("Edad", ft.Icons.CALENDAR_TODAY_ROUNDED), 
        keyboard_type=ft.KeyboardType.NUMBER,
        value="",
        expand=True
    )
    weight_input = ft.TextField(
        **theme.get_input_style("Peso (kg)", ft.Icons.SCALE_ROUNDED), 
        keyboard_type=ft.KeyboardType.NUMBER,
        value="",
        expand=True
    )
    height_input = ft.TextField(
        **theme.get_input_style("Altura (cm)", ft.Icons.HEIGHT_ROUNDED), 
        keyboard_type=ft.KeyboardType.NUMBER,
        value="",
        expand=True
    )

    activity_dropdown = ft.Dropdown(
        label="Nivel de Actividad Física",
        options=[
            ft.dropdown.Option("Sedentario (Poco o nada)"),
            ft.dropdown.Option("Ligero (1 a 3 días/sem)"),
            ft.dropdown.Option("Moderado (3 a 5 días/sem)"),
            ft.dropdown.Option("Intenso (6 a 7 días/sem)"),
            ft.dropdown.Option("Muy Intenso (Físico diario)"),
        ],
        value="Moderado (3 a 5 días/sem)",
        border_color=theme.SURFACE_BORDER,
        focused_border_color=theme.PRIMARY,
        color=theme.TEXT_PRIMARY,
        border_radius=14,
        filled=True,
        fill_color=theme.SURFACE_VARIANT,
    )
    
    goal_dropdown = ft.Dropdown(
        label="Objetivo Nutricional",
        options=[
            ft.dropdown.Option("Mantenimiento"),
            ft.dropdown.Option("Déficit (Perder Grasa)"),
            ft.dropdown.Option("Superávit (Ganar Masa)")
        ],
        value="Mantenimiento",
        border_color=theme.SURFACE_BORDER,
        focused_border_color=theme.PRIMARY,
        color=theme.TEXT_PRIMARY,
        border_radius=14,
        filled=True,
        fill_color=theme.SURFACE_VARIANT,
    )
    
    # Selector Dinámico de Agresividad (por defecto 300 kcal)
    modifier_input = ft.TextField(
        **theme.get_input_style("Ajuste Calórico (kcal)", ft.Icons.TUNE_ROUNDED),
        value="300",
        keyboard_type=ft.KeyboardType.NUMBER,
    )

    current_preset = "300"

    def set_aggressiveness_preset(val_str):
        nonlocal current_preset
        current_preset = val_str
        modifier_input.value = val_str
        update_preset_chips()
        recalculate_preview()

    chip_leve = ft.Container(
        content=ft.Text("Leve (300 kcal)", size=11, weight=ft.FontWeight.W_600, color=theme.PRIMARY_LIGHT),
        padding=ft.Padding(left=10, top=6, right=10, bottom=6),
        border_radius=12,
        bgcolor=theme.PRIMARY_BG,
        border=ft.border.all(1, theme.PRIMARY),
        on_click=lambda _: set_aggressiveness_preset("300"),
        animate=theme.STANDARD_ANIMATION,
    )
    chip_mod = ft.Container(
        content=ft.Text("Moderado (500 kcal)", size=11, weight=ft.FontWeight.W_600, color=theme.TEXT_PRIMARY),
        padding=ft.Padding(left=10, top=6, right=10, bottom=6),
        border_radius=12,
        bgcolor=theme.SURFACE_VARIANT,
        border=ft.border.all(1, theme.SURFACE_BORDER),
        on_click=lambda _: set_aggressiveness_preset("500"),
        animate=theme.STANDARD_ANIMATION,
    )
    chip_agr = ft.Container(
        content=ft.Text("Agresivo (700 kcal)", size=11, weight=ft.FontWeight.W_600, color=theme.TEXT_PRIMARY),
        padding=ft.Padding(left=10, top=6, right=10, bottom=6),
        border_radius=12,
        bgcolor=theme.SURFACE_VARIANT,
        border=ft.border.all(1, theme.SURFACE_BORDER),
        on_click=lambda _: set_aggressiveness_preset("700"),
        animate=theme.STANDARD_ANIMATION,
    )

    def update_preset_chips():
        for ch, v in [(chip_leve, "300"), (chip_mod, "500"), (chip_agr, "700")]:
            if current_preset == v:
                ch.bgcolor = theme.PRIMARY_BG
                ch.border = ft.border.all(1, theme.PRIMARY)
                ch.content.color = theme.PRIMARY_LIGHT
            else:
                ch.bgcolor = theme.SURFACE_VARIANT
                ch.border = ft.border.all(1, theme.SURFACE_BORDER)
                ch.content.color = theme.TEXT_PRIMARY

    aggressiveness_container = ft.Container(
        content=ft.Column([
            ft.Text("Ritmo de Ajuste Calórico", size=12, weight=ft.FontWeight.W_600, color=theme.TEXT_PRIMARY),
            ft.Row([chip_leve, chip_mod, chip_agr], spacing=6, wrap=True),
            modifier_input
        ], spacing=8),
        visible=False
    )

    # Vista previa en vivo del cálculo calórico y macros
    preview_cal = ft.Text("— kcal / día", size=17, weight=ft.FontWeight.W_800, color=theme.PRIMARY_LIGHT)
    preview_tdee = ft.Text("TDEE: —", size=11, weight=ft.FontWeight.W_600, color=theme.TEXT_SECONDARY)
    preview_macros = ft.Text("P: —  •  C: —  •  G: —", size=11, weight=ft.FontWeight.W_600, color=theme.TEXT_PRIMARY)
    preview_water = ft.Text("Agua: —", size=11, color=theme.COLOR_WATER_LIGHT)

    preview_card = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Row([
                    ft.Icon(ft.Icons.INSIGHTS_ROUNDED, size=15, color=theme.PRIMARY_LIGHT),
                    ft.Text("Meta Diaria", size=12, weight=ft.FontWeight.W_700, color=theme.TEXT_PRIMARY)
                ], spacing=6),
                ft.Container(
                    content=preview_tdee,
                    padding=ft.Padding(left=7, top=2, right=7, bottom=2),
                    border_radius=8,
                    bgcolor=theme.SURFACE_CARD,
                    border=ft.border.all(1, theme.SURFACE_BORDER)
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([
                preview_cal,
                ft.Row([
                    ft.Icon(ft.Icons.WATER_DROP_ROUNDED, size=13, color=theme.COLOR_WATER_LIGHT),
                    preview_water
                ], spacing=4)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            preview_macros
        ], spacing=6),
        bgcolor=theme.SURFACE_VARIANT,
        padding=12,
        border_radius=14,
        border=ft.border.all(1, theme.SURFACE_BORDER)
    )

    def calculate_plan():
        w = float(weight_input.value.strip())
        h = float(height_input.value.strip())
        a = int(age_input.value.strip())
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
            mod = 300
            
        if goal == "Déficit (Perder Grasa)":
            target_cal = max(1000, int(tdee - mod))
        elif goal == "Superávit (Ganar Masa)":
            target_cal = int(tdee + mod)
        else:
            target_cal = int(tdee)
            
        target_prot = w * 2.0
        target_fat = w * 0.8
        carb_cals = target_cal - (target_prot * 4) - (target_fat * 9)
        target_carbs = max(0, carb_cals / 4.0)
        water_add = WATER_ACTIVITY_ADDITIONS.get(activity_dropdown.value, 500)
        water_goal = int(w * 35 + water_add)
        
        return {
            'w': w, 'h': h, 'a': a, 'g': g, 'goal': goal,
            'tdee': int(tdee), 'target_cal': target_cal,
            'target_prot': target_prot, 'target_carbs': target_carbs,
            'target_fat': target_fat, 'water_goal': water_goal
        }

    def recalculate_preview(e=None):
        nonlocal current_preset
        goal = goal_dropdown.value
        if goal == "Mantenimiento":
            aggressiveness_container.visible = False
        else:
            aggressiveness_container.visible = True
            if not modifier_input.value or modifier_input.value == "0":
                modifier_input.value = "300"
                current_preset = "300"
                update_preset_chips()

        if e and e.control == modifier_input:
            if modifier_input.value in ["300", "500", "700"]:
                current_preset = modifier_input.value
            else:
                current_preset = "CUSTOM"
            update_preset_chips()

        has_data = bool(weight_input.value.strip() and height_input.value.strip() and age_input.value.strip())
        if not has_data:
            preview_cal.value = "— kcal / día"
            preview_tdee.value = "TDEE: —"
            preview_macros.value = "P: —  •  C: —  •  G: —"
            preview_water.value = "Agua: —"
        else:
            try:
                plan = calculate_plan()
                preview_cal.value = f"{plan['target_cal']} kcal / día"
                preview_tdee.value = f"TDEE: {plan['tdee']} kcal"
                preview_macros.value = f"P: {int(plan['target_prot'])}g  •  C: {int(plan['target_carbs'])}g  •  G: {int(plan['target_fat'])}g"
                preview_water.value = f"Agua: {plan['water_goal']} ml"
            except Exception:
                pass
        page.update()

    name_input.on_change = recalculate_preview
    gender_dropdown.on_change = recalculate_preview
    age_input.on_change = recalculate_preview
    weight_input.on_change = recalculate_preview
    height_input.on_change = recalculate_preview
    activity_dropdown.on_change = recalculate_preview
    goal_dropdown.on_change = recalculate_preview
    modifier_input.on_change = recalculate_preview

    def save_setup(e):
        if not (age_input.value.strip() and weight_input.value.strip() and height_input.value.strip()):
            page.snack_bar = theme.create_snackbar(
                content=ft.Text("Por favor, ingresa tu edad, peso y altura.", color="white"), 
                bgcolor=theme.DANGER_BG
            )
            page.snack_bar.open = True
            page.update()
            return

        try:
            plan = calculate_plan()
            db.save_profile(
                name_input.value.strip() or "Usuario",
                plan['g'],
                plan['a'],
                plan['w'],
                plan['h'],
                plan['goal'],
                plan['target_cal'],
                plan['target_prot'],
                plan['target_carbs'],
                plan['target_fat'],
                plan['water_goal'],
                activity_dropdown.value
            )
            
            profiles = db.get_profiles()
            if profiles:
                latest_id = profiles[-1]['id']
                db.set_active_profile_id(latest_id)
            
            on_finish()
                
        except ValueError:
            page.snack_bar = theme.create_snackbar(
                content=ft.Text("Por favor, completa correctamente los campos numéricos.", color="white"), 
                bgcolor=theme.DANGER_BG
            )
            page.snack_bar.open = True
            page.update()

    continue_btn = ft.ElevatedButton(
        "Finalizar y Entrar", 
        icon=ft.Icons.CHECK_CIRCLE_ROUNDED,
        on_click=save_setup, 
        style=theme.get_button_style(), 
        width=float('inf')
    )

    form_card = ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Image(
                    src="icon.png",
                    width=64,
                    height=64,
                    fit=ft.ImageFit.CONTAIN,
                    border_radius=16,
                ),
                alignment=ft.Alignment(0, 0),
            ),
            ft.Text("Crea tu Perfil", size=22, weight=ft.FontWeight.W_800, color=theme.TEXT_PRIMARY),
            ft.Text(
                "Ingresa tus datos para calibrar tu TDEE y macronutrientes ideales con rigor metabólico.", 
                color=theme.TEXT_SECONDARY, 
                size=12, 
                text_align=ft.TextAlign.CENTER
            ),
            ft.Container(height=4),
            name_input,
            ft.Row([gender_dropdown, age_input], spacing=10),
            ft.Row([weight_input, height_input], spacing=10),
            activity_dropdown,
            goal_dropdown,
            aggressiveness_container,
            preview_card,
            ft.Container(height=4),
            continue_btn,
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=11),
        **theme.get_card_style(padding=20),
        width=float('inf')
    )

    setup_container = ft.Container(
        content=ft.Column([
            form_card
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.HIDDEN),
        padding=16,
        expand=True,
        alignment=ft.Alignment(0, 0),
        opacity=0,
        animate_opacity=ft.Animation(600, "easeOut")
    )
    
    # Calcular vista previa inicial
    try:
        recalculate_preview()
    except Exception:
        pass

    return setup_container

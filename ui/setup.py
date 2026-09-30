import flet as ft
import database as db
from ui import theme

def get_setup_view(page: ft.Page, on_finish):
    
    name_input = ft.TextField(**theme.get_input_style("Tu Nombre", ft.Icons.PERSON))
    
    gender_dropdown = ft.Dropdown(
        label="Sexo",
        options=[ft.dropdown.Option("Hombre"), ft.dropdown.Option("Mujer")],
        value="Hombre",
        border_color=theme.PRIMARY,
        color=theme.TEXT_PRIMARY,
        border_radius=10,
        filled=True,
        fill_color=theme.SURFACE_VARIANT,
    )
    
    age_input = ft.TextField(**theme.get_input_style("Edad", ft.Icons.CALENDAR_TODAY), keyboard_type=ft.KeyboardType.NUMBER)
    weight_input = ft.TextField(**theme.get_input_style("Peso (kg)", ft.Icons.SCALE), keyboard_type=ft.KeyboardType.NUMBER)
    height_input = ft.TextField(**theme.get_input_style("Altura (cm)", ft.Icons.HEIGHT), keyboard_type=ft.KeyboardType.NUMBER)
    
    modifier_input = ft.TextField(
        **theme.get_input_style("Ajuste (Kcal)", ft.Icons.TUNE),
        value="500",
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    
    modifier_container = ft.Container(
        content=modifier_input,
        visible=False
    )
    
    def on_goal_change(e):
        if e.control.value == "Mantenimiento":
            modifier_container.visible = False
        else:
            modifier_container.visible = True
        page.update()
    
    goal_dropdown = ft.Dropdown(
        label="Tu Objetivo",
        options=[
            ft.dropdown.Option("Déficit (Perder Grasa)"),
            ft.dropdown.Option("Mantenimiento"),
            ft.dropdown.Option("Superávit (Ganar Masa)")
        ],
        value="Mantenimiento",
        border_color=theme.PRIMARY,
        color=theme.TEXT_PRIMARY,
        border_radius=10,
        filled=True,
        fill_color=theme.SURFACE_VARIANT,
    )
    goal_dropdown.on_select = on_goal_change
    
    activity_dropdown = ft.Dropdown(
        label="Nivel de Actividad Física Diaria",
        options=[
            ft.dropdown.Option("Sedentario: poco o nada de ejercicio al día"),
            ft.dropdown.Option("Actividad ligera: ejercicio ligero o deporte 1-3 días a la semana"),
            ft.dropdown.Option("Actividad moderada: ejercicio moderado o deporte 3-5 días a la semana"),
            ft.dropdown.Option("Actividad intensa: ejercicio intenso o deporte 6-7 días a la semana"),
            ft.dropdown.Option("Actividad muy intensa: ejercicio muy intenso o trabajo físico y ejercicio diario"),
        ],
        value="Actividad moderada: ejercicio moderado o deporte 3-5 días a la semana",
        border_color=theme.PRIMARY,
        color=theme.TEXT_PRIMARY,
        border_radius=10,
        filled=True,
        fill_color=theme.SURFACE_VARIANT,
    )

    # Hacer que los campos de las filas compartan el espacio equitativamente (50/50)
    gender_dropdown.expand = True
    age_input.expand = True
    weight_input.expand = True
    height_input.expand = True

    def save_setup(e):
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
                
            activity_factors = {
                "Sedentario: poco o nada de ejercicio al día": 1.2,
                "Actividad ligera: ejercicio ligero o deporte 1-3 días a la semana": 1.375,
                "Actividad moderada: ejercicio moderado o deporte 3-5 días a la semana": 1.55,
                "Actividad intensa: ejercicio intenso o deporte 6-7 días a la semana": 1.725,
                "Actividad muy intensa: ejercicio muy intenso o trabajo físico y ejercicio diario": 1.9,
            }
            factor = activity_factors.get(activity_dropdown.value, 1.55)
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
            
            water_goal = int(w * 35) # 35ml per kg of body weight
                
            db.save_profile(name_input.value, g, a, w, h, goal, target_cal, target_prot, target_carbs, target_fat, water_goal, activity_dropdown.value)
            
            # Recuperar el ID del perfil recién guardado
            profiles = db.get_profiles()
            if profiles:
                # El más reciente suele estar al final, o simplemente obtenemos el activo
                latest_id = profiles[-1]['id']
                db.set_active_profile_id(latest_id)
            
            on_finish()
                
        except ValueError:
            page.snack_bar = ft.SnackBar(ft.Text("Por favor, ingresa valores numéricos en Edad, Peso y Altura.", color="white"), bgcolor=theme.DANGER)
            page.snack_bar.open = True
            page.update()

    continue_btn = ft.ElevatedButton("Finalizar Configuración", on_click=save_setup, style=theme.get_button_style(), width=float('inf'))

    form_content = ft.Column([
        ft.Icon(ft.Icons.PERSON_ADD, size=80, color=theme.PRIMARY),
        ft.Text("Crea tu Perfil", size=26, weight=ft.FontWeight.BOLD, color=theme.TEXT_PRIMARY),
        ft.Text("Necesitamos algunos datos para calcular tus metas metabólicas con precisión.", color=theme.TEXT_SECONDARY, size=14, text_align=ft.TextAlign.CENTER),
        ft.Container(height=10),
        name_input,
        ft.Row([gender_dropdown, age_input], spacing=15),
        ft.Row([weight_input, height_input], spacing=15),
        activity_dropdown,
        goal_dropdown,
        modifier_container,
        ft.Container(height=10),
        continue_btn,
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15, width=400) # Formulario contenido y centrado

    setup_container = ft.Container(
        content=form_content,
        padding=30,
        expand=True,
        alignment=ft.Alignment(0, 0),
        opacity=0,
        animate_opacity=ft.Animation(800, "easeOut")
    )
    
    return setup_container

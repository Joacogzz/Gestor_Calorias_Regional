import flet as ft
import database as db
from ui import theme

def get_diary_view(page: ft.Page, navigate_back, scroll_target=None):
    search_input = ft.TextField(
        **theme.get_input_style("Buscar alimento (ej. chipa, mandioca, pollo)", ft.Icons.SEARCH_ROUNDED),
        expand=True
    )
    
    current_filter = "ALL" # ALL, REGIONAL, FAVORITES, RECIPES
    results_list = ft.ListView(expand=True, spacing=8)
    diary_list = ft.ListView(expand=True, spacing=10)
    
    # -------------------------------------------------------------
    # 1. RENDERIZADO DEL DIARIO DE HOY (AGRUPADO POR COMIDAS)
    # -------------------------------------------------------------
    def render_diary():
        entries = db.get_diary_entries()
        diary_list.controls.clear()
        
        if not entries:
            diary_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.NO_FOOD_ROUNDED, size=36, color=theme.TEXT_MUTED),
                        ft.Text("Aún no has registrado alimentos hoy.", color=theme.TEXT_SECONDARY, size=13),
                        ft.Text("Utiliza el catálogo o buscador superior para agregar tu consumo.", color=theme.TEXT_MUTED, size=11),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                    padding=20,
                    alignment=ft.Alignment(0, 0)
                )
            )
            page.update()
            return
            
        grouped = {
            "Desayuno": {"icon": ft.Icons.WB_SUNNY_ROUNDED, "color": theme.COLOR_CARBS, "items": []},
            "Almuerzo": {"icon": ft.Icons.SUNNY, "color": theme.PRIMARY, "items": []},
            "Cena": {"icon": ft.Icons.NIGHTLIGHT_ROUNDED, "color": theme.COLOR_PROTEIN, "items": []},
            "Snack": {"icon": ft.Icons.COOKIE_ROUNDED, "color": theme.SECONDARY, "items": []}
        }
        
        for e in entries:
            m = e.get('meal_type', 'Snack')
            if m not in grouped:
                grouped[m] = {"icon": ft.Icons.RESTAURANT_ROUNDED, "color": theme.PRIMARY, "items": []}
            grouped[m]["items"].append(e)
            
        for meal_name, data in grouped.items():
            items = data["items"]
            if not items:
                continue
            meal_cals = sum(i['calories'] for i in items)
            
            # Cabecera de grupo de comida
            diary_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Row([
                            ft.Icon(data["icon"], size=16, color=data["color"]),
                            ft.Text(meal_name, size=14, weight=ft.FontWeight.W_700, color=theme.TEXT_PRIMARY),
                        ], spacing=6),
                        theme.badge(f"{int(meal_cals)} kcal", icon=ft.Icons.BOLT_ROUNDED, bg_color=theme.SURFACE_VARIANT, text_color=theme.PRIMARY_LIGHT, font_size=10)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.Padding(left=4, top=6, right=4, bottom=2)
                )
            )
            
            # Tarjetas de alimentos consumidos (Layout de 2 niveles desahogado)
            for e in items:
                food_name_lower = e['food_name'].lower()
                is_portion_unit = "porción" in food_name_lower or "porciones" in food_name_lower
                is_liquid = any(w in food_name_lower for w in ['aceite', 'leche', 'yogur', 'salsa', 'jugo', 'agua', 'miel', 'crema'])
                
                if is_portion_unit:
                    amount_str = f"{e['amount_g'] / 100.0:g} porción"
                elif is_liquid:
                    amount_str = f"{e['amount_g']:g} ml"
                else:
                    amount_str = f"{e['amount_g']:g} g"
                
                diary_list.controls.append(
                    ft.Container(
                        content=ft.Column([
                            # Nivel 1: Título y acciones
                            ft.Row([
                                ft.Text(e['food_name'], size=13, weight=ft.FontWeight.W_600, color=theme.TEXT_PRIMARY, expand=True),
                                ft.Row([
                                    ft.IconButton(
                                        ft.Icons.EDIT_ROUNDED, 
                                        icon_size=16, 
                                        icon_color=theme.PRIMARY_LIGHT, 
                                        tooltip="Modificar cantidad",
                                        on_click=lambda ev, entry=e: open_edit_dialog(entry)
                                    ),
                                    ft.IconButton(
                                        ft.Icons.DELETE_OUTLINE_ROUNDED, 
                                        icon_size=16, 
                                        icon_color=theme.DANGER_LIGHT, 
                                        tooltip="Eliminar",
                                        on_click=lambda ev, eid=e['id']: delete_entry(eid)
                                    )
                                ], spacing=0)
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                            
                            # Nivel 2: Métricas sin amontonamiento
                            ft.Row([
                                ft.Container(
                                    content=ft.Text(amount_str, size=11, color=theme.TEXT_SECONDARY, weight=ft.FontWeight.W_500),
                                    bgcolor=theme.SURFACE_CARD,
                                    padding=ft.Padding(left=6, top=2, right=6, bottom=2),
                                    border_radius=6,
                                ),
                                ft.Text(f"{int(e['calories'])} kcal", size=11, weight=ft.FontWeight.W_700, color=theme.PRIMARY_LIGHT),
                                ft.Text("•", size=10, color=theme.TEXT_MUTED),
                                ft.Text(f"P: {int(e['protein'])}g", size=10, color=theme.COLOR_PROTEIN_LIGHT, weight=ft.FontWeight.W_600),
                                ft.Text(f"C: {int(e['carbs'])}g", size=10, color=theme.COLOR_CARBS_LIGHT, weight=ft.FontWeight.W_600),
                                ft.Text(f"G: {int(e['fat'])}g", size=10, color=theme.COLOR_FAT_LIGHT, weight=ft.FontWeight.W_600),
                            ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER)
                        ], spacing=3),
                        padding=ft.Padding(left=12, top=8, right=8, bottom=8),
                        bgcolor=theme.SURFACE_VARIANT,
                        border_radius=12,
                        border=ft.border.all(1, theme.SURFACE_BORDER),
                        animate=theme.STANDARD_ANIMATION,
                    )
                )
        diary_list.controls.append(ft.Container(height=24))
        page.update()

    def delete_entry(entry_id):
        db.delete_diary_entry(entry_id)
        render_diary()
        page.snack_bar = theme.create_snackbar(
            content=ft.Row([
                ft.Icon(ft.Icons.DELETE_SWEEP_ROUNDED, color=theme.DANGER_LIGHT, size=18),
                ft.Text("Alimento eliminado del registro.", size=13, color=theme.TEXT_PRIMARY)
            ], spacing=8),
            bgcolor=theme.SURFACE_CARD,
            duration=2500
        )
        page.snack_bar.open = True
        page.update()

    catalog_count_badge = ft.Text("46 disponibles", size=11, color=theme.TEXT_MUTED)

    # -------------------------------------------------------------
    # 2. BÚSQUEDA Y FILTRADO CON CATÁLOGO COMPLETO
    # -------------------------------------------------------------
    def search_click(e=None):
        query = (search_input.value or "").strip()
        results = db.search_foods(query=query, limit=100, filter_type=current_filter)
            
        results_list.controls.clear()
        
        if query:
            catalog_count_badge.value = f"{len(results)} encontrados"
        else:
            catalog_count_badge.value = f"{len(results)} disponibles"
        
        if not results:
            results_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.SEARCH_OFF_ROUNDED, size=32, color=theme.TEXT_MUTED),
                        ft.Text("No se encontraron alimentos.", color=theme.TEXT_SECONDARY, size=12),
                        ft.ElevatedButton(
                            "Crear Alimento Personalizado", 
                            icon=ft.Icons.ADD_ROUNDED, 
                            on_click=open_custom_food_dialog, 
                            style=theme.get_button_style()
                        )
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6),
                    padding=16,
                    alignment=ft.Alignment(0, 0)
                )
            )
            page.update()
            return
            
        for f in results:
            fav_icon = ft.Icons.STAR_ROUNDED if f['is_favorite'] else ft.Icons.STAR_BORDER_ROUNDED
            fav_color = theme.COLOR_CARBS if f['is_favorite'] else theme.TEXT_MUTED
            is_regional = f.get('is_regional', 0) == 1
            is_recipe = f.get('is_recipe', 0) == 1
            
            # Badges distintivos
            badges_row = []
            if is_regional:
                badges_row.append(theme.regional_badge())
            elif is_recipe:
                badges_row.append(theme.recipe_badge())
                
            # Tarjeta de 2 niveles: evita colisión entre macros y botón "Agregar"
            results_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        # Nivel 1: Nombre + Badges a la izquierda, Favorito y Agregar a la derecha
                        ft.Row([
                            ft.Row([
                                ft.Text(f['name'], size=13.5, weight=ft.FontWeight.W_700, color=theme.TEXT_PRIMARY),
                            ] + badges_row, spacing=6, wrap=True, expand=True),
                            ft.Row([
                                ft.IconButton(
                                    fav_icon, 
                                    icon_color=fav_color, 
                                    icon_size=20,
                                    tooltip="Favorito",
                                    on_click=lambda ev, fid=f['id'], fav=f['is_favorite']: toggle_fav(fid, fav)
                                ),
                                ft.Container(
                                    content=ft.Row([
                                        ft.Icon(ft.Icons.ADD_ROUNDED, size=14, color="#FFFFFF"),
                                        ft.Text("Agregar", size=11, weight=ft.FontWeight.W_700, color="#FFFFFF")
                                    ], spacing=3, alignment=ft.MainAxisAlignment.CENTER),
                                    bgcolor=theme.PRIMARY,
                                    border_radius=8,
                                    padding=ft.Padding(left=8, top=6, right=10, bottom=6),
                                    on_click=lambda ev, f_data=f: open_add_dialog(f_data),
                                    animate=theme.STANDARD_ANIMATION,
                                )
                            ], spacing=2)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        
                        # Nivel 2: Calorías y Macronutrientes con ancho completo garantizado
                        ft.Row([
                            ft.Container(
                                content=ft.Text(f"{int(f['calories_per_100g'])} kcal / 100g", size=11, weight=ft.FontWeight.W_700, color=theme.PRIMARY_LIGHT),
                                bgcolor=theme.PRIMARY_BG,
                                padding=ft.Padding(left=6, top=2, right=6, bottom=2),
                                border_radius=6,
                            ),
                            ft.Text("•", size=10, color=theme.TEXT_MUTED),
                            ft.Text(f"P: {int(f['protein_per_100g'])}g", size=11, color=theme.COLOR_PROTEIN_LIGHT, weight=ft.FontWeight.W_600),
                            ft.Text(f"C: {int(f['carbs_per_100g'])}g", size=11, color=theme.COLOR_CARBS_LIGHT, weight=ft.FontWeight.W_600),
                            ft.Text(f"G: {int(f['fat_per_100g'])}g", size=11, color=theme.COLOR_FAT_LIGHT, weight=ft.FontWeight.W_600),
                        ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER)
                    ], spacing=6),
                    padding=ft.Padding(left=12, top=10, right=10, bottom=10),
                    bgcolor=theme.SURFACE_VARIANT,
                    border_radius=12,
                    border=ft.border.all(1, theme.SURFACE_BORDER_ACTIVE if is_regional else theme.SURFACE_BORDER),
                    animate=theme.STANDARD_ANIMATION,
                )
            )
        results_list.controls.append(ft.Container(height=24))
        page.update()

    def toggle_fav(food_id, is_favorite):
        db.toggle_favorite(food_id, 0 if is_favorite else 1)
        search_click(None)

    def set_filter(f_name):
        nonlocal current_filter
        current_filter = f_name
        update_filter_chips()
        search_click(None)

    # Botones tipo chips para filtrado rápido
    btn_all = ft.Container(
        content=ft.Text("Todos", size=11, weight=ft.FontWeight.W_600, color=theme.TEXT_PRIMARY),
        bgcolor=theme.PRIMARY_BG,
        padding=ft.Padding(left=12, top=6, right=12, bottom=6),
        border_radius=20,
        border=ft.border.all(1, theme.PRIMARY),
        on_click=lambda _: set_filter("ALL"),
        animate=theme.STANDARD_ANIMATION,
    )
    
    btn_regional = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.LOCATION_ON_ROUNDED, size=12, color=theme.PRIMARY_LIGHT),
            ft.Text("Regionales", size=11, weight=ft.FontWeight.W_600, color=theme.TEXT_PRIMARY)
        ], spacing=4),
        bgcolor=theme.SURFACE_VARIANT,
        padding=ft.Padding(left=12, top=6, right=12, bottom=6),
        border_radius=20,
        border=ft.border.all(1, theme.SURFACE_BORDER),
        on_click=lambda _: set_filter("REGIONAL"),
        animate=theme.STANDARD_ANIMATION,
    )

    btn_basic = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.RESTAURANT_ROUNDED, size=12, color=theme.COLOR_PROTEIN_LIGHT),
            ft.Text("Básicos", size=11, weight=ft.FontWeight.W_600, color=theme.TEXT_PRIMARY)
        ], spacing=4),
        bgcolor=theme.SURFACE_VARIANT,
        padding=ft.Padding(left=12, top=6, right=12, bottom=6),
        border_radius=20,
        border=ft.border.all(1, theme.SURFACE_BORDER),
        on_click=lambda _: set_filter("BASIC"),
        animate=theme.STANDARD_ANIMATION,
    )

    btn_fav = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.STAR_ROUNDED, size=12, color=theme.COLOR_CARBS_LIGHT),
            ft.Text("Favoritos", size=11, weight=ft.FontWeight.W_600, color=theme.TEXT_PRIMARY)
        ], spacing=4),
        bgcolor=theme.SURFACE_VARIANT,
        padding=ft.Padding(left=12, top=6, right=12, bottom=6),
        border_radius=20,
        border=ft.border.all(1, theme.SURFACE_BORDER),
        on_click=lambda _: set_filter("FAVORITES"),
        animate=theme.STANDARD_ANIMATION,
    )

    btn_rec = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.MENU_BOOK_ROUNDED, size=12, color="#F472B6"),
            ft.Text("Recetas", size=11, weight=ft.FontWeight.W_600, color=theme.TEXT_PRIMARY)
        ], spacing=4),
        bgcolor=theme.SURFACE_VARIANT,
        padding=ft.Padding(left=12, top=6, right=12, bottom=6),
        border_radius=20,
        border=ft.border.all(1, theme.SURFACE_BORDER),
        on_click=lambda _: set_filter("RECIPES"),
        animate=theme.STANDARD_ANIMATION,
    )

    def update_filter_chips():
        for b, name in [(btn_all, "ALL"), (btn_regional, "REGIONAL"), (btn_basic, "BASIC"), (btn_fav, "FAVORITES"), (btn_rec, "RECIPES")]:
            if current_filter == name:
                b.bgcolor = theme.PRIMARY_BG
                b.border = ft.border.all(1, theme.PRIMARY)
            else:
                b.bgcolor = theme.SURFACE_VARIANT
                b.border = ft.border.all(1, theme.SURFACE_BORDER)
        page.update()

    filter_chips_row = ft.Row([btn_all, btn_regional, btn_basic, btn_fav, btn_rec], spacing=8, scroll=ft.ScrollMode.HIDDEN)

    # -------------------------------------------------------------
    # 3. DIÁLOGO CREAR ALIMENTO MANUAL
    # -------------------------------------------------------------
    def open_custom_food_dialog(e):
        name_input = ft.TextField(**theme.get_input_style("Nombre del Alimento", ft.Icons.FASTFOOD_ROUNDED))
        cal_input = ft.TextField(**theme.get_input_style("Kcal (por 100g)", ft.Icons.LOCAL_FIRE_DEPARTMENT_ROUNDED), keyboard_type=ft.KeyboardType.NUMBER)
        prot_input = ft.TextField(**theme.get_input_style("Proteínas (g)", ft.Icons.FITNESS_CENTER_ROUNDED), keyboard_type=ft.KeyboardType.NUMBER)
        carb_input = ft.TextField(**theme.get_input_style("Carbohidratos (g)", ft.Icons.GRAIN_ROUNDED), keyboard_type=ft.KeyboardType.NUMBER)
        fat_input = ft.TextField(**theme.get_input_style("Grasas (g)", ft.Icons.OPACITY_ROUNDED), keyboard_type=ft.KeyboardType.NUMBER)
        
        def save_custom(ev):
            try:
                db.add_custom_food(
                    name_input.value,
                    float(cal_input.value),
                    float(prot_input.value),
                    float(carb_input.value),
                    float(fat_input.value)
                )
                dlg.open = False
                search_input.value = name_input.value
                search_click(None)
                page.snack_bar = theme.create_snackbar(
                    content=ft.Text(f"Alimento '{name_input.value}' creado correctamente."),
                    bgcolor=theme.SURFACE_CARD
                )
                page.snack_bar.open = True
                page.update()
            except ValueError:
                cal_input.error_text = "Ingresa números válidos"
                page.update()

        def close_dlg(ev=None):
            dlg.open = False
            page.update()
            
        dlg = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.Icons.ADD_CIRCLE_OUTLINE_ROUNDED, color=theme.PRIMARY),
                ft.Text("Nuevo Alimento", size=18, weight=ft.FontWeight.W_700, color=theme.TEXT_PRIMARY)
            ], spacing=8),
            content=ft.Column([
                name_input, cal_input, prot_input, carb_input, fat_input
            ], tight=True, spacing=10),
            actions=[
                ft.TextButton("Cancelar", on_click=close_dlg),
                ft.ElevatedButton("Guardar Alimento", on_click=save_custom, style=theme.get_button_style()),
            ],
            bgcolor=theme.SURFACE_CARD,
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    # -------------------------------------------------------------
    # 4. DIÁLOGO AGREGAR / EDITAR ALIMENTO CON PREVISUALIZACIÓN VIVA
    # -------------------------------------------------------------
    def open_add_dialog(f_data, edit_entry=None):
        is_recipe = f_data.get('is_recipe', 0) == 1
        is_liquid = any(word in f_data['name'].lower() for word in ['aceite', 'leche', 'yogur', 'salsa', 'jugo', 'agua', 'miel', 'crema']) and not is_recipe
        unit = "ml" if is_liquid else "g"
        
        if is_recipe:
            base_measure = "Porciones"
            options = [ft.dropdown.Option("Porciones")]
            icon = ft.Icons.PIE_CHART_ROUNDED
            default_val = str(edit_entry['amount_g'] / 100.0) if edit_entry else "1"
        else:
            base_measure = "Mililitros" if is_liquid else "Gramos"
            options = [
                ft.dropdown.Option(base_measure),
                ft.dropdown.Option(f"Porción (~100{unit})"),
                ft.dropdown.Option(f"Cucharada (~15{unit})"),
                ft.dropdown.Option(f"Taza (~200{unit})")
            ]
            icon = ft.Icons.WATER_DROP_ROUNDED if is_liquid else ft.Icons.SCALE_ROUNDED
            default_val = str(edit_entry['amount_g']) if edit_entry else "100"
            
        amount_input = ft.TextField(
            **theme.get_input_style("Cantidad", icon), 
            keyboard_type=ft.KeyboardType.NUMBER, 
            value=default_val
        )
        
        measure_dropdown = ft.Dropdown(
            label="Medida",
            options=options,
            value=base_measure,
            border_color=theme.SURFACE_BORDER,
            focused_border_color=theme.PRIMARY,
            color=theme.TEXT_PRIMARY,
            border_radius=14,
            filled=True,
            fill_color=theme.SURFACE_VARIANT,
        )
        
        meal_dropdown = ft.Dropdown(
            label="Momento de Consumo",
            options=[
                ft.dropdown.Option("Desayuno"),
                ft.dropdown.Option("Almuerzo"),
                ft.dropdown.Option("Cena"),
                ft.dropdown.Option("Snack")
            ],
            value=edit_entry.get('meal_type', 'Almuerzo') if edit_entry else 'Almuerzo',
            border_color=theme.SURFACE_BORDER,
            focused_border_color=theme.PRIMARY,
            color=theme.TEXT_PRIMARY,
            border_radius=14,
            filled=True,
            fill_color=theme.SURFACE_VARIANT,
        )

        preview_cals = ft.Text("0 kcal", size=12, weight=ft.FontWeight.W_700, color=theme.PRIMARY_LIGHT)
        preview_macros = ft.Text("P: 0g • C: 0g • G: 0g", size=11, color=theme.TEXT_SECONDARY)

        def recalculate_preview(ev=None):
            try:
                val = float(amount_input.value)
                m = measure_dropdown.value
                if is_recipe:
                    g = val * 100
                else:
                    g = val
                    if m.startswith("Porción"): g = val * 100
                    if m.startswith("Cucharada"): g = val * 15
                    if m.startswith("Taza"): g = val * 200
                factor = g / 100.0
                c = int(f_data['calories_per_100g'] * factor)
                p = int(f_data['protein_per_100g'] * factor)
                cb = int(f_data['carbs_per_100g'] * factor)
                ft_val = int(f_data['fat_per_100g'] * factor)
                preview_cals.value = f"{c} kcal"
                preview_macros.value = f"P: {p}g • C: {cb}g • G: {ft_val}g"
            except:
                preview_cals.value = "—"
                preview_macros.value = ""
            page.update()

        amount_input.on_change = recalculate_preview
        measure_dropdown.on_change = recalculate_preview
        recalculate_preview()
        
        def confirm_add(e):
            try:
                val = float(amount_input.value)
                if val <= 0:
                    amount_input.error_text = "Ingresa una cantidad mayor a 0"
                    page.update()
                    return
                m = measure_dropdown.value
                
                if is_recipe:
                    g = val * 100
                else:
                    g = val
                    if m.startswith("Porción"): g = val * 100
                    if m.startswith("Cucharada"): g = val * 15
                    if m.startswith("Taza"): g = val * 200
                
                factor = g / 100.0
                cal = f_data['calories_per_100g'] * factor
                prot = f_data['protein_per_100g'] * factor
                carb = f_data['carbs_per_100g'] * factor
                fat = f_data['fat_per_100g'] * factor
                
                if edit_entry:
                    db.update_diary_entry(edit_entry['id'], g, cal, prot, carb, fat, meal_dropdown.value)
                    msg = f"Registro de {f_data['name']} actualizado."
                else:
                    db.add_diary_entry(f_data['id'], f_data['name'], g, cal, prot, carb, fat, meal_dropdown.value)
                    msg = f"¡{f_data['name']} agregado al diario!"
                    
                dlg.open = False
                render_diary()
                page.snack_bar = theme.create_snackbar(
                    content=ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, color=theme.PRIMARY_LIGHT, size=18),
                        ft.Text(msg, size=13, color=theme.TEXT_PRIMARY)
                    ], spacing=8),
                    bgcolor=theme.SURFACE_CARD,
                    duration=2500
                )
                page.snack_bar.open = True
                page.update()
            except ValueError:
                amount_input.error_text = "Ingresa un número válido"
                page.update()

        def close_dlg(ev=None):
            dlg.open = False
            page.update()
            
        dlg = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.Icons.RESTAURANT_ROUNDED, color=theme.PRIMARY_LIGHT, size=20),
                ft.Text(f"{'Modificar' if edit_entry else 'Registrar'} {f_data['name']}", size=16, weight=ft.FontWeight.W_700, color=theme.TEXT_PRIMARY)
            ], spacing=8),
            content=ft.Container(
                content=ft.Column([
                    amount_input,
                    measure_dropdown,
                    meal_dropdown,
                    ft.Container(
                        content=ft.Row([
                            ft.Row([
                                ft.Icon(ft.Icons.LOCAL_FIRE_DEPARTMENT_ROUNDED, size=15, color=theme.PRIMARY_LIGHT),
                                preview_cals
                            ], spacing=4),
                            preview_macros
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        bgcolor=theme.SURFACE_VARIANT,
                        padding=ft.Padding(left=12, top=10, right=12, bottom=10),
                        border_radius=10,
                        border=ft.border.all(1, theme.SURFACE_BORDER),
                        height=44
                    )
                ], tight=True, spacing=12),
                width=320
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=close_dlg),
                ft.ElevatedButton("Confirmar", on_click=confirm_add, style=theme.get_button_style()),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=theme.SURFACE_CARD,
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def open_edit_dialog(entry):
        results = db.search_foods(entry['food_name'], limit=5)
        if results:
            open_add_dialog(results[0], edit_entry=entry)
        else:
            page.snack_bar = theme.create_snackbar(ft.Text("Alimento original no encontrado."), bgcolor=theme.DANGER_BG)
            page.snack_bar.open = True
            page.update()

    search_input.on_change = search_click
    search_input.on_submit = search_click
    
    # Carga inicial inmediata de los 20 alimentos más relevantes
    search_click(None)
    render_diary()

    # -------------------------------------------------------------
    # 5. WIDGET DE HIDRATACIÓN (REGISTRO EN DIARIO)
    # -------------------------------------------------------------
    profile = db.get_profile() or {}
    water_target = profile.get('water_goal', 2000)
    water_ml = db.get_water_today()
    water_progress = min(water_ml / water_target, 1.0) if water_target > 0 else 0
    water_pct = int(water_progress * 100)

    water_ml_text = ft.Text(f"{water_ml}", size=16, weight=ft.FontWeight.W_800, color=theme.TEXT_PRIMARY)
    water_badge_text = ft.Text(f"{water_pct}%", size=11, weight=ft.FontWeight.W_700, color=theme.COLOR_WATER_LIGHT)
    water_progress_bar = ft.ProgressBar(
        value=water_progress, 
        color=theme.COLOR_WATER, 
        bgcolor=theme.SURFACE_VARIANT, 
        height=8, 
        border_radius=5
    )

    water_input = ft.TextField(
        hint_text="Cantidad en ml (ej: 250)",
        keyboard_type=ft.KeyboardType.NUMBER,
        border_radius=12,
        filled=True,
        fill_color=theme.SURFACE_VARIANT,
        border_color=theme.SURFACE_BORDER,
        focused_border_color=theme.COLOR_WATER,
        color=theme.TEXT_PRIMARY,
        content_padding=ft.Padding(left=12, top=10, right=12, bottom=10),
        dense=True,
        expand=True,
    )

    def update_water_ui():
        nonlocal water_ml, water_progress, water_pct
        water_ml = db.get_water_today()
        water_progress = min(water_ml / water_target, 1.0) if water_target > 0 else 0
        water_pct = int(water_progress * 100)
        water_ml_text.value = f"{water_ml}"
        water_badge_text.value = f"{water_pct}%"
        water_progress_bar.value = water_progress
        water_card.update()

    def submit_water(e=None):
        try:
            val = int(water_input.value.strip())
            if val > 0:
                db.add_water(val)
                water_input.value = ""
                update_water_ui()
                page.snack_bar = theme.create_snackbar(
                    content=ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, color=theme.COLOR_WATER_LIGHT, size=16),
                        ft.Text(f"+{val} ml de agua registrados.", size=12, color=theme.TEXT_PRIMARY)
                    ], spacing=6),
                    bgcolor=theme.SURFACE_CARD,
                    duration=2000
                )
                page.snack_bar.open = True
                page.update()
        except Exception:
            pass

    def subtract_water(e=None):
        try:
            raw = water_input.value.strip()
            removed_val = 0
            if raw:
                val = int(raw)
                if val > 0:
                    if water_ml - val < 0:
                        db.add_water(-water_ml)
                    else:
                        db.add_water(-val)
                    removed_val = val
                    water_input.value = ""
            else:
                deleted = db.delete_last_water_entry()
                if deleted > 0:
                    removed_val = deleted

            update_water_ui()
            if removed_val > 0:
                page.snack_bar = theme.create_snackbar(
                    content=ft.Row([
                        ft.Icon(ft.Icons.REMOVE_CIRCLE_OUTLINE_ROUNDED, color=theme.DANGER_LIGHT, size=16),
                        ft.Text(f"Se restaron {removed_val} ml de agua.", size=12, color=theme.TEXT_PRIMARY)
                    ], spacing=6),
                    bgcolor=theme.SURFACE_CARD,
                    duration=2000
                )
                page.snack_bar.open = True
                page.update()
        except Exception:
            pass

    water_input.on_submit = submit_water

    water_card = ft.Container(
        key="water_card",
        content=ft.Column([
            ft.Row([
                ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.Icons.WATER_DROP_ROUNDED, color=theme.COLOR_WATER_LIGHT, size=20),
                        bgcolor=theme.COLOR_WATER_BG,
                        border_radius=10,
                        padding=8,
                        border=ft.border.all(1, theme.with_opacity(0.3, theme.COLOR_WATER_LIGHT))
                    ),
                    ft.Column([
                        ft.Row([
                            theme.subheader_text("Hidratación"),
                            ft.Container(
                                content=water_badge_text,
                                bgcolor=theme.COLOR_WATER_BG,
                                padding=ft.Padding(left=6, top=2, right=6, bottom=2),
                                border_radius=6,
                            )
                        ], spacing=6),
                        ft.Row([
                            water_ml_text,
                            ft.Text(f"/ {water_target} ml", size=12, color=theme.TEXT_SECONDARY)
                        ], spacing=4)
                    ], spacing=2)
                ], spacing=10),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=4),
            water_progress_bar,
            ft.Container(height=8),
            ft.Row([
                water_input,
                ft.ElevatedButton(
                    "Registrar",
                    icon=ft.Icons.ADD_ROUNDED,
                    on_click=submit_water,
                    style=ft.ButtonStyle(
                        color="white",
                        bgcolor=theme.COLOR_WATER,
                        shape=ft.RoundedRectangleBorder(radius=12),
                        padding=ft.Padding(left=12, top=10, right=12, bottom=10)
                    )
                ),
                ft.IconButton(
                    ft.Icons.REMOVE_ROUNDED,
                    icon_color=theme.DANGER_LIGHT,
                    bgcolor=theme.SURFACE_VARIANT,
                    tooltip="Restar último registro o cantidad escrita",
                    on_click=subtract_water,
                )
            ], spacing=6)
        ]),
        **theme.get_card_style(padding=14)
    )

    # -------------------------------------------------------------
    # 6. CONTENEDOR PRINCIPAL
    # -------------------------------------------------------------
    header_bar = ft.Row([
        ft.IconButton(ft.Icons.ARROW_BACK_ROUNDED, on_click=lambda _: navigate_back(), icon_color=theme.PRIMARY),
        theme.header_text("Diario Nutricional")
    ], spacing=4)

    search_card = ft.Container(
        content=ft.Column([
            ft.Row([
                theme.subheader_text("Catálogo y Búsqueda"),
                catalog_count_badge,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([
                search_input, 
                ft.IconButton(
                    ft.Icons.SEARCH_ROUNDED, 
                    on_click=search_click, 
                    icon_color="#FFFFFF",
                    bgcolor=theme.PRIMARY,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12))
                )
            ], spacing=6),
            theme.fade_scroll_horizontal(filter_chips_row),
            ft.Container(content=results_list, height=270)
        ], spacing=8),
        **theme.get_card_style(padding=14)
    )

    diary_card = ft.Container(
        content=ft.Column([
            ft.Row([
                theme.subheader_text("Registros de Hoy"),
                ft.Icon(ft.Icons.CALENDAR_TODAY_ROUNDED, size=16, color=theme.TEXT_SECONDARY)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(content=diary_list, height=220)
        ], spacing=8),
        **theme.get_card_style(padding=14)
    )

    main_column = ft.Column([
        header_bar,
        search_card,
        water_card,
        diary_card
    ], expand=True, spacing=6, scroll=ft.ScrollMode.HIDDEN)

    if scroll_target == "hydration":
        import threading, time
        def do_scroll():
            time.sleep(0.01)
            try:
                main_column.scroll_to(key="water_card", duration=0)
            except Exception:
                pass
            time.sleep(0.04)
            try:
                main_column.scroll_to(key="water_card", duration=0)
            except Exception:
                pass
        threading.Thread(target=do_scroll, daemon=True).start()

    return main_column

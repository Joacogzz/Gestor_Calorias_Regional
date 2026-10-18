import flet as ft
import database as db
from ui import theme

def get_recipes_view(page: ft.Page):
    recipe_name_input = ft.TextField(
        **theme.get_input_style("Nombre de la Receta (ej. Guiso Misionero)", ft.Icons.RESTAURANT_MENU_ROUNDED),
        expand=True
    )
    portions_input = ft.TextField(
        **theme.get_input_style("Porciones", ft.Icons.PIE_CHART_ROUNDED), 
        value="1", 
        keyboard_type=ft.KeyboardType.NUMBER,
        width=120
    )
    
    search_input = ft.TextField(
        **theme.get_input_style("Buscar ingrediente para la receta", ft.Icons.SEARCH_ROUNDED), 
        expand=True
    )
    results_list = ft.ListView(height=160, spacing=6)
    ingredients_list = ft.ListView(height=170, spacing=8)
    my_recipes_list = ft.ListView(height=240, spacing=8)
    
    # Estado de la receta en construcción
    current_ingredients = []

    # -------------------------------------------------------------
    # 1. RESUMEN EN 2 COLUMNAS (TOTAL VS PORCIÓN CON MERMA)
    # -------------------------------------------------------------
    total_cal_val = ft.Text("0 kcal", size=16, weight=ft.FontWeight.W_800, color=theme.TEXT_PRIMARY)
    total_macros_val = ft.Text("P: 0g | C: 0g | G: 0g", size=11, color=theme.TEXT_SECONDARY)
    
    portion_cal_val = ft.Text("0 kcal", size=18, weight=ft.FontWeight.W_800, color=theme.PRIMARY_LIGHT)
    portion_macros_val = ft.Text("P: 0g | C: 0g | G: 0g", size=11, color=theme.PRIMARY_LIGHT)

    def update_totals(e=None):
        total_cal = 0
        total_prot = 0
        total_carb = 0
        total_fat = 0
        
        for ing in current_ingredients:
            # Los macros aportados por el ingrediente crudo se mantienen
            raw_factor = ing['amount_g'] / 100.0
            total_cal += ing['food']['calories_per_100g'] * raw_factor
            total_prot += ing['food']['protein_per_100g'] * raw_factor
            total_carb += ing['food']['carbs_per_100g'] * raw_factor
            total_fat += ing['food']['fat_per_100g'] * raw_factor
            
        try:
            p = float(portions_input.value)
            if p <= 0: p = 1
        except:
            p = 1
            
        total_cal_val.value = f"{int(total_cal)} kcal"
        total_macros_val.value = f"P: {int(total_prot)}g • C: {int(total_carb)}g • G: {int(total_fat)}g"
        
        portion_cal_val.value = f"{int(total_cal / p)} kcal"
        portion_macros_val.value = f"P: {int(total_prot / p)}g • C: {int(total_carb / p)}g • G: {int(total_fat / p)}g"
        page.update()

    portions_input.on_change = update_totals

    summary_two_columns = ft.Container(
        content=ft.Row([
            # Columna 1: Total Receta
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.ALL_INBOX_ROUNDED, size=14, color=theme.TEXT_SECONDARY),
                        ft.Text("Total Preparación", size=12, weight=ft.FontWeight.W_600, color=theme.TEXT_SECONDARY)
                    ], spacing=4),
                    total_cal_val,
                    total_macros_val,
                ], spacing=2),
                bgcolor=theme.SURFACE_VARIANT,
                padding=12,
                border_radius=14,
                border=ft.border.all(1, theme.SURFACE_BORDER),
                expand=True
            ),
            # Columna 2: Por Porción
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.ROOM_SERVICE_ROUNDED, size=14, color=theme.PRIMARY_LIGHT),
                        ft.Text("Por Porción", size=12, weight=ft.FontWeight.W_700, color=theme.PRIMARY_LIGHT)
                    ], spacing=4),
                    portion_cal_val,
                    portion_macros_val,
                ], spacing=2),
                bgcolor=theme.PRIMARY_BG,
                padding=12,
                border_radius=14,
                border=ft.border.all(1, theme.with_opacity(0.4, theme.PRIMARY)),
                expand=True
            )
        ], spacing=10),
        margin=ft.Margin(top=6, left=0, right=0, bottom=6)
    )

    # -------------------------------------------------------------
    # 2. LISTA DE INGREDIENTES CON DETALLE DE MERMA
    # -------------------------------------------------------------
    def render_ingredients():
        ingredients_list.controls.clear()
        if not current_ingredients:
            ingredients_list.controls.append(
                ft.Container(
                    content=ft.Text("No has añadido ingredientes todavía.", color=theme.TEXT_MUTED, size=12),
                    alignment=ft.Alignment(0, 0),
                    padding=16
                )
            )
        for i, ing in enumerate(current_ingredients):
            food_name = ing['food']['name']
            is_liquid = any(word in food_name.lower() for word in ['aceite', 'leche', 'yogur', 'salsa', 'jugo', 'agua', 'miel', 'crema'])
            unit = "ml" if is_liquid else "g"
            has_merma = ing.get('apply_cooking_factor', False)
            raw_g = ing['amount_g']
            cooked_g = raw_g * 0.75 if has_merma else raw_g
            
            c_factor = raw_g / 100.0
            ing_cal = int(ing['food']['calories_per_100g'] * c_factor)
            
            # Badge de merma
            merma_pill = theme.badge("Merma -25%", icon=ft.Icons.LOCAL_FIRE_DEPARTMENT_ROUNDED, bg_color=theme.COLOR_FAT_BG, text_color=theme.COLOR_FAT_LIGHT, font_size=10) if has_merma else ft.Container()
            
            ingredients_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Row([
                                ft.Text(food_name, size=13, weight=ft.FontWeight.W_600, color=theme.TEXT_PRIMARY),
                                merma_pill
                            ], spacing=6),
                            ft.Row([
                                ft.Text(f"{raw_g:g}{unit} crudo", size=11, color=theme.TEXT_SECONDARY),
                                ft.Text(f"→ {cooked_g:g}{unit} cocido" if has_merma else "", size=11, color=theme.COLOR_FAT_LIGHT if has_merma else theme.TEXT_MUTED),
                                ft.Text("•", size=10, color=theme.TEXT_MUTED),
                                ft.Text(f"{ing_cal} kcal", size=11, weight=ft.FontWeight.W_700, color=theme.PRIMARY_LIGHT),
                            ], spacing=4)
                        ], expand=True, spacing=2),
                        ft.IconButton(
                            ft.Icons.DELETE_OUTLINE_ROUNDED, 
                            icon_color=theme.DANGER_LIGHT, 
                            icon_size=20,
                            tooltip="Quitar ingrediente",
                            on_click=lambda ev, idx=i: remove_ingredient(idx)
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.Padding(left=12, top=8, right=8, bottom=8),
                    bgcolor=theme.SURFACE_VARIANT,
                    border_radius=12,
                    border=ft.border.all(1, theme.SURFACE_BORDER)
                )
            )
        update_totals()

    def remove_ingredient(idx):
        current_ingredients.pop(idx)
        render_ingredients()

    # -------------------------------------------------------------
    # 3. BÚSQUEDA DE INGREDIENTES
    # -------------------------------------------------------------
    def search_click(e=None):
        query = search_input.value or ""
        results = db.search_foods(query)
        results_list.controls.clear()
        
        if not results:
            results_list.controls.append(
                ft.Container(
                    content=ft.Text("No se encontraron ingredientes.", color=theme.TEXT_MUTED, size=12),
                    alignment=ft.Alignment(0, 0),
                    padding=10
                )
            )
            page.update()
            return
            
        for f in results:
            is_reg = f.get('is_regional', 0) == 1
            results_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Row([
                                ft.Text(f['name'], size=13, weight=ft.FontWeight.W_600, color=theme.TEXT_PRIMARY),
                                theme.regional_badge() if is_reg else ft.Container()
                            ], spacing=6),
                            ft.Text(f"{f['calories_per_100g']} kcal / 100g", size=11, color=theme.TEXT_MUTED),
                        ], expand=True, spacing=1),
                        ft.IconButton(
                            ft.Icons.ADD_CIRCLE_OUTLINE_ROUNDED, 
                            icon_color=theme.PRIMARY_LIGHT, 
                            icon_size=24,
                            tooltip="Añadir a la receta",
                            on_click=lambda ev, f_data=f: open_add_dialog(f_data)
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    on_click=lambda ev, f_data=f: open_add_dialog(f_data),
                    padding=ft.Padding(left=10, top=6, right=6, bottom=6),
                    border_radius=10,
                    bgcolor=theme.SURFACE_VARIANT,
                    border=ft.border.all(1, theme.SURFACE_BORDER),
                    animate=theme.STANDARD_ANIMATION,
                )
            )
        page.update()

    def open_add_dialog(f_data):
        is_liquid = any(word in f_data['name'].lower() for word in ['aceite', 'leche', 'yogur', 'salsa', 'jugo', 'agua', 'miel', 'crema'])
        unit = "ml" if is_liquid else "g"
        icon = ft.Icons.WATER_DROP_ROUNDED if is_liquid else ft.Icons.SCALE_ROUNDED
        
        amount_input = ft.TextField(
            **theme.get_input_style(f"Cantidad en Crudo ({unit})", icon), 
            keyboard_type=ft.KeyboardType.NUMBER,
            value="100"
        )
        cooking_factor_cb = ft.Checkbox(
            label="Aplicar merma por cocción (-25% peso)", 
            value=False, 
            fill_color=theme.PRIMARY,
            label_style=ft.TextStyle(color=theme.TEXT_PRIMARY, size=12)
        )
        
        def confirm_add(e):
            try:
                g = float(amount_input.value)
                current_ingredients.append({
                    'food': f_data, 
                    'amount_g': g, 
                    'apply_cooking_factor': cooking_factor_cb.value
                })
                dlg.open = False
                page.update()
                render_ingredients()
            except ValueError:
                amount_input.error_text = "Ingresa un número válido"
                page.update()

        def close_dlg(ev=None):
            dlg.open = False
            page.update()
            
        dlg = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.Icons.ADD_ROUNDED, color=theme.PRIMARY_LIGHT),
                ft.Text(f"Añadir {f_data['name']}", size=16, weight=ft.FontWeight.W_700, color=theme.TEXT_PRIMARY)
            ], spacing=8),
            content=ft.Column([
                amount_input, 
                ft.Container(
                    content=ft.Column([
                        cooking_factor_cb,
                        ft.Text("Útil para carnes y verduras que evaporan agua al freír o hervir.", size=10, color=theme.TEXT_MUTED)
                    ], spacing=2),
                    bgcolor=theme.SURFACE_VARIANT,
                    padding=10,
                    border_radius=10
                )
            ], tight=True, spacing=10),
            actions=[
                ft.TextButton("Cancelar", on_click=close_dlg),
                ft.ElevatedButton("Agregar a Receta", on_click=confirm_add, style=theme.get_button_style()),
            ],
            bgcolor=theme.SURFACE_CARD
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def save_recipe_click(e):
        if not recipe_name_input.value:
            page.snack_bar = theme.create_snackbar(ft.Text("Ingresa un nombre para tu receta"), bgcolor=theme.DANGER_BG)
            page.snack_bar.open = True
            page.update()
            return
            
        if not current_ingredients:
            page.snack_bar = theme.create_snackbar(ft.Text("Agrega al menos un ingrediente a la receta"), bgcolor=theme.DANGER_BG)
            page.snack_bar.open = True
            page.update()
            return

        total_cal, total_prot, total_carb, total_fat = 0, 0, 0, 0
        for ing in current_ingredients:
            factor = ing['amount_g'] / 100.0
            total_cal += ing['food']['calories_per_100g'] * factor
            total_prot += ing['food']['protein_per_100g'] * factor
            total_carb += ing['food']['carbs_per_100g'] * factor
            total_fat += ing['food']['fat_per_100g'] * factor
            
        try:
            p = float(portions_input.value)
            if p <= 0: p = 1
        except:
            p = 1
            
        name_suffix = f" (1 de {int(p)} porciones)" if p > 1 else " (1 porción)"
        db.save_recipe(
            recipe_name_input.value + name_suffix, 
            total_cal / p, 
            total_prot / p, 
            total_carb / p, 
            total_fat / p
        )
        
        page.snack_bar = theme.create_snackbar(
            content=ft.Row([
                ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, color=theme.PRIMARY_LIGHT, size=18),
                ft.Text(f"¡Receta '{recipe_name_input.value}' guardada con éxito!", size=13, color=theme.TEXT_PRIMARY)
            ], spacing=8),
            bgcolor=theme.SURFACE_CARD,
            duration=3000
        )
        page.snack_bar.open = True
        page.update()
        
        # Resetear formulario
        recipe_name_input.value = ""
        portions_input.value = "1"
        current_ingredients.clear()
        render_ingredients()
        render_my_recipes()

    # -------------------------------------------------------------
    # 4. MIS RECETAS CREADAS
    # -------------------------------------------------------------
    def render_my_recipes():
        my_recipes_list.controls.clear()
        recipes = db.get_recipes()
        if not recipes:
            my_recipes_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.BOOK_ONLINE_ROUNDED, size=36, color=theme.TEXT_MUTED),
                        ft.Text("Aún no has creado recetas.", color=theme.TEXT_SECONDARY, size=13),
                        ft.Text("Crea una con ingredientes arriba y calcula sus porciones automáticamente.", color=theme.TEXT_MUTED, size=11),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                    padding=20,
                    alignment=ft.Alignment(0, 0)
                )
            )
            page.update()
            return
            
        for r in recipes:
            my_recipes_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Row([
                                ft.Text(r['name'], size=13.5, weight=ft.FontWeight.W_700, color=theme.TEXT_PRIMARY),
                                theme.recipe_badge()
                            ], spacing=6),
                            ft.Row([
                                ft.Text(f"{int(r['calories_per_100g'])} kcal / porción", size=12, weight=ft.FontWeight.W_700, color=theme.PRIMARY_LIGHT),
                                ft.Text("•", size=10, color=theme.TEXT_MUTED),
                                ft.Text(f"P: {int(r['protein_per_100g'])}g", size=11, color=theme.COLOR_PROTEIN_LIGHT),
                                ft.Text(f"C: {int(r['carbs_per_100g'])}g", size=11, color=theme.COLOR_CARBS_LIGHT),
                                ft.Text(f"G: {int(r['fat_per_100g'])}g", size=11, color=theme.COLOR_FAT_LIGHT),
                            ], spacing=4)
                        ], expand=True, spacing=2),
                        ft.IconButton(
                            ft.Icons.DELETE_OUTLINE_ROUNDED, 
                            icon_color=theme.DANGER_LIGHT, 
                            icon_size=20,
                            tooltip="Eliminar receta",
                            on_click=lambda ev, rid=r['id']: delete_recipe_click(rid)
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.Padding(left=14, top=10, right=10, bottom=10),
                    bgcolor=theme.SURFACE_VARIANT,
                    border_radius=14,
                    border=ft.border.all(1, theme.SURFACE_BORDER)
                )
            )
        page.update()
        
    def delete_recipe_click(recipe_id):
        db.delete_recipe(recipe_id)
        render_my_recipes()
        page.snack_bar = theme.create_snackbar(ft.Text("Receta eliminada del catálogo."), bgcolor=theme.SURFACE_CARD)
        page.snack_bar.open = True
        page.update()

    render_my_recipes()
    search_input.on_change = search_click
    search_input.on_submit = search_click
    search_input.on_focus = search_click

    # Banner informativo de merma
    merma_info_card = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED, color=theme.SECONDARY, size=18),
            ft.Text("Cálculo de Merma: Al cocinarse, carnes y vegetales pierden peso por evaporación concentrando sus calorías por cada 100g.", size=11, color=theme.TEXT_SECONDARY, expand=True)
        ], spacing=8),
        bgcolor=theme.SURFACE_VARIANT,
        padding=10,
        border_radius=12,
        border=ft.border.all(1, theme.SURFACE_BORDER),
        margin=ft.Margin(0, 4, 0, 8)
    )

    recipes_content = ft.Column([
        ft.Container(
            content=ft.Column([
                theme.subheader_text("Información de la Receta"),
                ft.Row([recipe_name_input, portions_input], spacing=8),
                merma_info_card,
                theme.subheader_text("Buscar Ingredientes"),
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
                ft.Container(content=results_list, height=130),
                theme.subheader_text("Ingredientes Agregados"),
                ft.Container(content=ingredients_list, height=140),
                summary_two_columns,
                ft.ElevatedButton(
                    "Guardar Receta en Catálogo", 
                    icon=ft.Icons.SAVE_ROUNDED,
                    on_click=save_recipe_click, 
                    style=theme.get_button_style(), 
                    width=float('inf')
                )
            ], spacing=10),
            **theme.get_card_style(padding=16)
        ),
        ft.Container(height=8),
        ft.Container(
            content=ft.Column([
                ft.Row([
                    theme.subheader_text("Mis Recetas Creadas"),
                    theme.badge("Catálogo propio", icon=ft.Icons.BOOKMARK_ROUNDED, bg_color=theme.SURFACE_VARIANT, text_color=theme.TEXT_SECONDARY, font_size=10)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(content=my_recipes_list, height=200)
            ], spacing=8),
            **theme.get_card_style(padding=16)
        )
    ], expand=True, scroll=ft.ScrollMode.AUTO)

    # -------------------------------------------------------------
    # 5. PESTAÑA: MIS ALIMENTOS MANUALES (CRUD)
    # -------------------------------------------------------------
    custom_foods_list = ft.ListView(expand=True, spacing=10)

    def render_custom_foods():
        custom_foods_list.controls.clear()
        foods = db.get_custom_foods()
        if not foods:
            custom_foods_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.EGG_OUTLINED, size=36, color=theme.TEXT_MUTED),
                        ft.Text("No has creado alimentos manuales.", color=theme.TEXT_SECONDARY, size=13),
                        ft.Text("Registra marcas o preparaciones caseras específicas.", color=theme.TEXT_MUTED, size=11),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                    padding=20,
                    alignment=ft.Alignment(0, 0)
                )
            )
            page.update()
            return
            
        for f in foods:
            custom_foods_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text(f['name'], size=13.5, weight=ft.FontWeight.W_700, color=theme.TEXT_PRIMARY),
                            ft.Row([
                                ft.Text(f"{f['calories_per_100g']} kcal", size=12, weight=ft.FontWeight.W_700, color=theme.PRIMARY_LIGHT),
                                ft.Text("•", size=10, color=theme.TEXT_MUTED),
                                ft.Text(f"P: {int(f['protein_per_100g'])}g", size=11, color=theme.COLOR_PROTEIN_LIGHT),
                                ft.Text(f"C: {int(f['carbs_per_100g'])}g", size=11, color=theme.COLOR_CARBS_LIGHT),
                                ft.Text(f"G: {int(f['fat_per_100g'])}g", size=11, color=theme.COLOR_FAT_LIGHT),
                            ], spacing=4)
                        ], expand=True, spacing=2),
                        ft.IconButton(
                            ft.Icons.EDIT_ROUNDED, 
                            icon_color=theme.PRIMARY_LIGHT, 
                            icon_size=20,
                            tooltip="Editar",
                            on_click=lambda ev, f_data=f: open_edit_food_dialog(f_data)
                        ),
                        ft.IconButton(
                            ft.Icons.DELETE_OUTLINE_ROUNDED, 
                            icon_color=theme.DANGER_LIGHT, 
                            icon_size=20,
                            tooltip="Eliminar",
                            on_click=lambda ev, fid=f['id']: delete_food_click(fid)
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.Padding(left=14, top=10, right=10, bottom=10),
                    bgcolor=theme.SURFACE_VARIANT,
                    border_radius=14,
                    border=ft.border.all(1, theme.SURFACE_BORDER)
                )
            )
        page.update()

    def delete_food_click(food_id):
        db.delete_custom_food(food_id)
        render_custom_foods()
        page.snack_bar = theme.create_snackbar(ft.Text("Alimento eliminado."), bgcolor=theme.SURFACE_CARD)
        page.snack_bar.open = True
        page.update()

    def open_edit_food_dialog(f_data=None):
        name_input = ft.TextField(**theme.get_input_style("Nombre", ft.Icons.FASTFOOD_ROUNDED), value=f_data['name'] if f_data else "")
        cal_input = ft.TextField(**theme.get_input_style("Kcal (por 100g)", ft.Icons.LOCAL_FIRE_DEPARTMENT_ROUNDED), keyboard_type=ft.KeyboardType.NUMBER, value=str(f_data['calories_per_100g']) if f_data else "")
        prot_input = ft.TextField(**theme.get_input_style("Proteínas (g)", ft.Icons.FITNESS_CENTER_ROUNDED), keyboard_type=ft.KeyboardType.NUMBER, value=str(f_data['protein_per_100g']) if f_data else "")
        carb_input = ft.TextField(**theme.get_input_style("Carbohidratos (g)", ft.Icons.GRAIN_ROUNDED), keyboard_type=ft.KeyboardType.NUMBER, value=str(f_data['carbs_per_100g']) if f_data else "")
        fat_input = ft.TextField(**theme.get_input_style("Grasas (g)", ft.Icons.OPACITY_ROUNDED), keyboard_type=ft.KeyboardType.NUMBER, value=str(f_data['fat_per_100g']) if f_data else "")
        
        def save_custom(ev):
            try:
                if f_data:
                    db.update_custom_food(f_data['id'], name_input.value, float(cal_input.value), float(prot_input.value), float(carb_input.value), float(fat_input.value))
                    msg = "Alimento actualizado con éxito."
                else:
                    db.add_custom_food(name_input.value, float(cal_input.value), float(prot_input.value), float(carb_input.value), float(fat_input.value))
                    msg = "Alimento creado con éxito."
                dlg.open = False
                render_custom_foods()
                page.snack_bar = theme.create_snackbar(ft.Text(msg), bgcolor=theme.SURFACE_CARD)
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
                ft.Icon(ft.Icons.EDIT_NOTE_ROUNDED, color=theme.PRIMARY_LIGHT),
                ft.Text("Editar Alimento" if f_data else "Crear Alimento", size=16, weight=ft.FontWeight.W_700, color=theme.TEXT_PRIMARY)
            ], spacing=8),
            content=ft.Column([name_input, cal_input, prot_input, carb_input, fat_input], tight=True, spacing=10),
            actions=[
                ft.TextButton("Cancelar", on_click=close_dlg),
                ft.ElevatedButton("Guardar", on_click=save_custom, style=theme.get_button_style()),
            ],
            bgcolor=theme.SURFACE_CARD,
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    foods_content = ft.Column([
        ft.ElevatedButton(
            "Crear Alimento Nuevo", 
            icon=ft.Icons.ADD_ROUNDED, 
            on_click=lambda _: open_edit_food_dialog(), 
            style=theme.get_button_style(), 
            width=float('inf')
        ),
        ft.Container(height=8),
        ft.Container(
            content=custom_foods_list,
            **theme.get_card_style(padding=16),
            expand=True
        )
    ], expand=True, scroll=ft.ScrollMode.AUTO)

    render_custom_foods()

    # -------------------------------------------------------------
    # 6. SELECTOR SEGMENTADO DE PESTAÑAS (TABS)
    # -------------------------------------------------------------
    content_container = ft.Container(content=recipes_content, expand=True)

    def change_tab(target):
        if target == "Recetas":
            content_container.content = recipes_content
            tab_recetas.bgcolor = theme.PRIMARY
            tab_recetas_text.color = "#FFFFFF"
            tab_alimentos.bgcolor = "transparent"
            tab_alimentos_text.color = theme.TEXT_SECONDARY
        else:
            content_container.content = foods_content
            tab_alimentos.bgcolor = theme.PRIMARY
            tab_alimentos_text.color = "#FFFFFF"
            tab_recetas.bgcolor = "transparent"
            tab_recetas_text.color = theme.TEXT_SECONDARY
        page.update()

    tab_recetas_text = ft.Text("Gestor de Recetas", size=12, weight=ft.FontWeight.W_700, color="#FFFFFF")
    tab_alimentos_text = ft.Text("Mis Alimentos", size=12, weight=ft.FontWeight.W_600, color=theme.TEXT_SECONDARY)

    tab_recetas = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.RESTAURANT_MENU_ROUNDED, size=15, color="#FFFFFF"),
            tab_recetas_text
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=6),
        bgcolor=theme.PRIMARY,
        padding=ft.Padding(left=14, top=10, right=14, bottom=10),
        border_radius=12,
        expand=True,
        on_click=lambda _: change_tab("Recetas"),
        animate=theme.STANDARD_ANIMATION,
    )

    tab_alimentos = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.EGG_ROUNDED, size=15, color=theme.TEXT_SECONDARY),
            tab_alimentos_text
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=6),
        bgcolor="transparent",
        padding=ft.Padding(left=14, top=10, right=14, bottom=10),
        border_radius=12,
        expand=True,
        on_click=lambda _: change_tab("Alimentos"),
        animate=theme.STANDARD_ANIMATION,
    )

    tab_bar = ft.Container(
        content=ft.Row([tab_recetas, tab_alimentos], spacing=4),
        bgcolor=theme.SURFACE_CARD,
        padding=4,
        border_radius=16,
        border=ft.border.all(1, theme.SURFACE_BORDER)
    )

    return ft.Column([
        tab_bar,
        ft.Container(height=4),
        content_container
    ], expand=True, spacing=4)

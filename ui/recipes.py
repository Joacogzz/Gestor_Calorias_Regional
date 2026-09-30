import flet as ft
import database as db
from ui import theme

def get_recipes_view(page: ft.Page):
    recipe_name_input = ft.TextField(**theme.get_input_style("Nombre de la Receta", ft.Icons.RESTAURANT_MENU))
    portions_input = ft.TextField(**theme.get_input_style("Porciones", ft.Icons.PIE_CHART), value="1", keyboard_type=ft.KeyboardType.NUMBER)
    
    search_input = ft.TextField(**theme.get_input_style("Buscar Ingrediente", ft.Icons.SEARCH), expand=True)
    results_list = ft.ListView(height=150, spacing=5)
    ingredients_list = ft.ListView(height=150, spacing=5)
    my_recipes_list = ft.ListView(height=200, spacing=10)
    
    # Estado de la receta
    current_ingredients = []

    def update_totals():
        total_cal = 0
        total_prot = 0
        total_carb = 0
        total_fat = 0
        
        for ing in current_ingredients:
            g = ing['amount_g']
            if ing.get('apply_cooking_factor', False):
                g = g * 0.75 # Pierde 25% de peso
            factor = g / 100.0
            # Los macros absolutos no se pierden (o se asume que se concentran), 
            # pero aquí el factor es sobre el peso original para calcular totales.
            # En realidad, si se cocina, los macros totales aportados por la carne cruda son los mismos, 
            # pero el peso final de la receta es menor.
            # Factor debe basarse en el peso crudo para los macros absolutos,
            # PERO el peso de la receta disminuye, lo que aumenta la densidad.
            
            # Corrección: Los macros aportados por 100g de carne cruda se mantienen.
            # La merma afecta al peso final de la receta.
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
            
        totals_text.value = f"Totales: {int(total_cal)} kcal | Prot: {int(total_prot)}g | Carb: {int(total_carb)}g | Grasa: {int(total_fat)}g"
        per_portion_text.value = f"Por Porción: {int(total_cal/p)} kcal | Prot: {int(total_prot/p)}g | Carb: {int(total_carb/p)}g | Grasa: {int(total_fat/p)}g"
        page.update()

    totals_text = theme.normal_text("Totales: 0 kcal", weight=ft.FontWeight.BOLD)
    per_portion_text = theme.normal_text("Por Porción: 0 kcal", color=theme.PRIMARY, weight=ft.FontWeight.BOLD)

    def render_ingredients():
        ingredients_list.controls.clear()
        for i, ing in enumerate(current_ingredients):
            is_liquid = any(word in ing['food']['name'].lower() for word in ['aceite', 'leche', 'yogur', 'salsa', 'jugo', 'agua', 'miel', 'crema'])
            unit = "ml" if is_liquid else "g"
            label = f"{ing['amount_g']}{unit} de {ing['food']['name']}"
            if ing.get('apply_cooking_factor', False):
                label += " (Con merma)"
            ingredients_list.controls.append(
                ft.Row([
                    theme.normal_text(label, expand=True),
                    ft.IconButton(ft.Icons.DELETE, icon_color=theme.DANGER, on_click=lambda ev, idx=i: remove_ingredient(idx))
                ])
            )
        update_totals()

    def remove_ingredient(idx):
        current_ingredients.pop(idx)
        render_ingredients()

    def search_click(e):
        query = search_input.value
        results = db.search_foods(query)
        results_list.controls.clear()
        for f in results:
            results_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        theme.normal_text(f['name'], expand=True),
                        ft.IconButton(ft.Icons.ADD, icon_color=theme.PRIMARY, on_click=lambda ev, f_data=f: open_add_dialog(f_data))
                    ]),
                    on_click=lambda ev, f_data=f: open_add_dialog(f_data),
                    ink=True,
                    padding=5,
                    border_radius=5
                )
            )
        page.update()

    def open_add_dialog(f_data):
        is_liquid = any(word in f_data['name'].lower() for word in ['aceite', 'leche', 'yogur', 'salsa', 'jugo', 'agua', 'miel', 'crema'])
        unit = "ml" if is_liquid else "g"
        icon = ft.Icons.WATER_DROP if is_liquid else ft.Icons.SCALE
        amount_input = ft.TextField(**theme.get_input_style(f"Cantidad ({unit})", icon), keyboard_type=ft.KeyboardType.NUMBER)
        cooking_factor_cb = ft.Checkbox(label="Aplicar merma por cocción (-25% peso)", value=False, fill_color=theme.PRIMARY)
        
        def confirm_add(e):
            try:
                g = float(amount_input.value)
                current_ingredients.append({'food': f_data, 'amount_g': g, 'apply_cooking_factor': cooking_factor_cb.value})
                dlg.open = False
                page.update()
                render_ingredients()
            except ValueError:
                amount_input.error_text = "Inválido"
                page.update()

        def close_dlg(ev=None):
            dlg.open = False
            page.update()
            
        dlg = ft.AlertDialog(
            title=ft.Text(f"Agregar {f_data['name']}"),
            content=ft.Column([amount_input, cooking_factor_cb], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=close_dlg),
                ft.TextButton("Agregar", on_click=confirm_add),
            ],
            bgcolor=theme.SURFACE
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def save_recipe_click(e):
        if not recipe_name_input.value:
            page.snack_bar = ft.SnackBar(ft.Text("Ingresa un nombre para la receta"), bgcolor=theme.DANGER)
            page.snack_bar = ft.SnackBar(ft.Text("Ingresa un nombre para la receta"), bgcolor=theme.DANGER)
            page.snack_bar.open = True
            page.update()
            return
            
        if not current_ingredients:
            page.snack_bar = ft.SnackBar(ft.Text("Agrega al menos un ingrediente"), bgcolor=theme.DANGER)
            page.snack_bar = ft.SnackBar(ft.Text("Agrega al menos un ingrediente"), bgcolor=theme.DANGER)
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
        
        page.snack_bar = ft.SnackBar(ft.Text("Receta guardada con éxito!"), bgcolor=theme.PRIMARY)
        page.snack_bar.open = True
        page.update()
        
        # Reset form
        recipe_name_input.value = ""
        portions_input.value = "1"
        current_ingredients.clear()
        render_ingredients()
        render_my_recipes()

    def render_my_recipes():
        my_recipes_list.controls.clear()
        recipes = db.get_recipes()
        if not recipes:
            my_recipes_list.controls.append(theme.normal_text("No has creado recetas aún.", color=theme.TEXT_SECONDARY))
        for r in recipes:
            my_recipes_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Column([
                            theme.normal_text(r['name'], weight=ft.FontWeight.BOLD),
                            theme.normal_text(f"{r['calories_per_100g']} kcal | P:{int(r['protein_per_100g'])}g C:{int(r['carbs_per_100g'])}g G:{int(r['fat_per_100g'])}g", size=12, color=theme.TEXT_SECONDARY)
                        ], expand=True),
                        ft.IconButton(ft.Icons.DELETE, icon_color=theme.DANGER, on_click=lambda ev, rid=r['id']: delete_recipe_click(rid))
                    ]),
                    padding=10,
                    bgcolor=theme.SURFACE,
                    border_radius=10
                )
            )
        page.update()
        
    def delete_recipe_click(recipe_id):
        db.delete_recipe(recipe_id)
        render_my_recipes()
        page.snack_bar = ft.SnackBar(ft.Text("Receta eliminada."), bgcolor=theme.SECONDARY)
        page.snack_bar.open = True
        page.update()
        
    render_my_recipes()
    search_input.on_change = search_click
    search_input.on_submit = search_click
    search_input.on_focus = search_click

    recipes_content = ft.Column([
        theme.header_text("Crear Receta"),
        ft.Container(
            content=ft.Column([
                recipe_name_input,
                portions_input,
                ft.Divider(color=theme.TEXT_SECONDARY),
                theme.subheader_text("Ingredientes"),
                ft.Row([search_input, ft.IconButton(ft.Icons.SEARCH, on_click=search_click, icon_color=theme.PRIMARY)]),
                ft.Container(content=results_list, border=ft.Border(top=ft.BorderSide(1, theme.TEXT_SECONDARY), right=ft.BorderSide(1, theme.TEXT_SECONDARY), bottom=ft.BorderSide(1, theme.TEXT_SECONDARY), left=ft.BorderSide(1, theme.TEXT_SECONDARY)), border_radius=10, padding=5),
                ft.Divider(color=theme.TEXT_SECONDARY),
                theme.subheader_text("Ingredientes Agregados"),
                ft.Container(content=ingredients_list, border=ft.Border(top=ft.BorderSide(1, theme.PRIMARY), right=ft.BorderSide(1, theme.PRIMARY), bottom=ft.BorderSide(1, theme.PRIMARY), left=ft.BorderSide(1, theme.PRIMARY)), border_radius=10, padding=5, bgcolor="#2C2C2C"),
                ft.Container(height=10),
                totals_text,
                per_portion_text,
                ft.Container(height=10),
                ft.ElevatedButton("Guardar Receta", on_click=save_recipe_click, style=theme.get_button_style(), width=float('inf'))
            ]),
            **theme.get_card_style()
        ),
        ft.Container(height=20),
        theme.header_text("Mis Recetas Creadas"),
        ft.Container(
            content=my_recipes_list,
            **theme.get_card_style()
        )
    ], expand=True, scroll=ft.ScrollMode.AUTO)

    # --- CUSTOM FOODS CRUD ---
    custom_foods_list = ft.ListView(expand=True, spacing=10)

    def render_custom_foods():
        custom_foods_list.controls.clear()
        foods = db.get_custom_foods()
        if not foods:
            custom_foods_list.controls.append(theme.normal_text("No has creado alimentos manuales.", color=theme.TEXT_SECONDARY))
        for f in foods:
            custom_foods_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Column([
                            theme.normal_text(f['name'], weight=ft.FontWeight.BOLD),
                            theme.normal_text(f"{f['calories_per_100g']} kcal | P:{int(f['protein_per_100g'])}g C:{int(f['carbs_per_100g'])}g G:{int(f['fat_per_100g'])}g", size=12, color=theme.TEXT_SECONDARY)
                        ], expand=True),
                        ft.IconButton(ft.Icons.EDIT, icon_color=theme.PRIMARY, on_click=lambda ev, f_data=f: open_edit_food_dialog(f_data)),
                        ft.IconButton(ft.Icons.DELETE, icon_color=theme.DANGER, on_click=lambda ev, fid=f['id']: delete_food_click(fid))
                    ]),
                    padding=10,
                    bgcolor=theme.SURFACE,
                    border_radius=10
                )
            )
        page.update()

    def delete_food_click(food_id):
        db.delete_custom_food(food_id)
        render_custom_foods()
        page.snack_bar = ft.SnackBar(ft.Text("Alimento eliminado."), bgcolor=theme.SECONDARY)
        page.snack_bar.open = True
        page.update()

    def open_edit_food_dialog(f_data=None):
        name_input = ft.TextField(**theme.get_input_style("Nombre", ft.Icons.FASTFOOD), value=f_data['name'] if f_data else "")
        cal_input = ft.TextField(**theme.get_input_style("Kcal (por 100g)"), keyboard_type=ft.KeyboardType.NUMBER, value=str(f_data['calories_per_100g']) if f_data else "")
        prot_input = ft.TextField(**theme.get_input_style("Prot (g)"), keyboard_type=ft.KeyboardType.NUMBER, value=str(f_data['protein_per_100g']) if f_data else "")
        carb_input = ft.TextField(**theme.get_input_style("Carbos (g)"), keyboard_type=ft.KeyboardType.NUMBER, value=str(f_data['carbs_per_100g']) if f_data else "")
        fat_input = ft.TextField(**theme.get_input_style("Grasas (g)"), keyboard_type=ft.KeyboardType.NUMBER, value=str(f_data['fat_per_100g']) if f_data else "")
        
        def save_custom(ev):
            try:
                if f_data:
                    db.update_custom_food(f_data['id'], name_input.value, float(cal_input.value), float(prot_input.value), float(carb_input.value), float(fat_input.value))
                    msg = "Alimento actualizado!"
                else:
                    db.add_custom_food(name_input.value, float(cal_input.value), float(prot_input.value), float(carb_input.value), float(fat_input.value))
                    msg = "Alimento creado!"
                dlg.open = False
                render_custom_foods()
                page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor=theme.PRIMARY)
                page.snack_bar.open = True
                page.update()
            except ValueError:
                cal_input.error_text = "Inválido"
                page.update()

        def close_dlg(ev=None):
            dlg.open = False
            page.update()
            
        dlg = ft.AlertDialog(
            title=ft.Text("Editar Alimento" if f_data else "Crear Alimento"),
            content=ft.Column([name_input, cal_input, prot_input, carb_input, fat_input], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=close_dlg),
                ft.TextButton("Guardar", on_click=save_custom),
            ],
            bgcolor=theme.SURFACE,
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    foods_content = ft.Column([
        theme.header_text("Mis Alimentos"),
        ft.ElevatedButton("Crear Alimento Nuevo", icon=ft.Icons.ADD, on_click=lambda _: open_edit_food_dialog(), style=theme.get_button_style(), width=float('inf')),
        ft.Container(height=10),
        ft.Container(
            content=custom_foods_list,
            **theme.get_card_style(),
            expand=True
        )
    ], expand=True, scroll=ft.ScrollMode.AUTO)

    render_custom_foods()

    # --- CUSTOM TABS SWITCHER ---
    content_container = ft.Container(content=recipes_content, expand=True)

    def change_tab(e):
        if e.control.data == "Recetas":
            content_container.content = recipes_content
            btn_recetas.style = theme.get_button_style()
            btn_alimentos.style = ft.ButtonStyle(bgcolor=theme.SURFACE_VARIANT, color=theme.TEXT_PRIMARY)
        else:
            content_container.content = foods_content
            btn_alimentos.style = theme.get_button_style()
            btn_recetas.style = ft.ButtonStyle(bgcolor=theme.SURFACE_VARIANT, color=theme.TEXT_PRIMARY)
        page.update()

    btn_recetas = ft.ElevatedButton("Mis Recetas", data="Recetas", on_click=change_tab, style=theme.get_button_style(), expand=True)
    btn_alimentos = ft.ElevatedButton("Mis Alimentos", data="Alimentos", on_click=change_tab, style=ft.ButtonStyle(bgcolor=theme.SURFACE_VARIANT, color=theme.TEXT_PRIMARY), expand=True)

    return ft.Column([
        ft.Row([btn_recetas, btn_alimentos], alignment=ft.MainAxisAlignment.CENTER),
        ft.Container(height=10),
        content_container
    ], expand=True)

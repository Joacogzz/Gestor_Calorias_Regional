import flet as ft
import database as db
from ui import theme

def get_diary_view(page: ft.Page, navigate_back):
    search_input = ft.TextField(**theme.get_input_style("Buscar alimento (ej. mandioca)", ft.Icons.SEARCH), expand=True)
    results_list = ft.ListView(expand=True, spacing=10)
    diary_list = ft.ListView(expand=True, spacing=10)
    
    def render_diary():
        entries = db.get_diary_entries()
        diary_list.controls.clear()
        if not entries:
            diary_list.controls.append(theme.normal_text("Aún no has registrado alimentos hoy.", color=theme.TEXT_SECONDARY))
        grouped = {"Desayuno": [], "Almuerzo": [], "Cena": [], "Snack": []}
        for e in entries:
            m = e.get('meal_type', 'Snack')
            if m not in grouped: grouped[m] = []
            grouped[m].append(e)
            
        for meal_name, items in grouped.items():
            if not items: continue
            meal_cals = sum(i['calories'] for i in items)
            
            diary_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        theme.subheader_text(meal_name),
                        theme.normal_text(f"{int(meal_cals)} kcal", color=theme.PRIMARY, weight=ft.FontWeight.BOLD)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=10
                )
            )
            
            for e in items:
                amount_str = f"{e['amount_g'] / 100.0:g} porción(es)" if "porción" in e['food_name'].lower() or "porciones" in e['food_name'].lower() else f"{e['amount_g']:g}{'ml' if any(w in e['food_name'].lower() for w in ['aceite', 'leche', 'yogur', 'salsa', 'jugo', 'agua', 'miel', 'crema']) else 'g'}"
                diary_list.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Column([
                                theme.normal_text(e['food_name'], weight=ft.FontWeight.BOLD),
                                theme.normal_text(f"{amount_str} - {int(e['calories'])} kcal", size=12, color=theme.TEXT_SECONDARY)
                            ], expand=True),
                            ft.IconButton(ft.Icons.EDIT, icon_color=theme.PRIMARY, on_click=lambda ev, entry=e: open_edit_dialog(entry)),
                            ft.IconButton(ft.Icons.DELETE, icon_color=theme.DANGER, on_click=lambda ev, eid=e['id']: delete_entry(eid))
                        ]),
                        padding=10,
                        bgcolor=theme.SURFACE,
                        border_radius=10
                    )
                )
        page.update()

    def delete_entry(entry_id):
        db.delete_diary_entry(entry_id)
        render_diary()
        page.snack_bar = ft.SnackBar(ft.Text("Registro eliminado."), bgcolor=theme.SECONDARY)
        page.snack_bar.open = True
        page.update()

    def search_click(e):
        query = search_input.value
        results = db.search_foods(query)
        results_list.controls.clear()
        
        if not results:
            results_list.controls.append(
                ft.Column([
                    theme.normal_text("No se encontraron alimentos.", color=theme.SECONDARY),
                    ft.ElevatedButton("Crear Alimento Nuevo", icon=ft.Icons.ADD, on_click=open_custom_food_dialog, style=theme.get_button_style())
                ])
            )
            
        for f in results:
            fav_icon = ft.Icons.STAR if f['is_favorite'] else ft.Icons.STAR_BORDER
            fav_color = theme.SECONDARY if f['is_favorite'] else theme.TEXT_SECONDARY
            
            results_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Row([
                                theme.normal_text(f['name'], weight=ft.FontWeight.BOLD),
                                ft.Icon(ft.Icons.VERIFIED, color=theme.PRIMARY, size=16) if f['is_regional'] else ft.Container()
                            ]),
                            theme.normal_text(f"{f['calories_per_100g']} kcal / 100g", size=12, color=theme.TEXT_SECONDARY)
                        ], expand=True),
                        ft.IconButton(fav_icon, icon_color=fav_color, on_click=lambda ev, fid=f['id'], fav=f['is_favorite']: toggle_fav(fid, fav)),
                        ft.ElevatedButton("Agregar", on_click=lambda ev, f_data=f: open_add_dialog(f_data), style=theme.get_button_style())
                    ]),
                    padding=10,
                    bgcolor=theme.SURFACE,
                    border_radius=10
                )
            )
        page.update()

    def toggle_fav(food_id, is_favorite):
        db.toggle_favorite(food_id, 0 if is_favorite else 1)
        search_click(None)

    def open_custom_food_dialog(e):
        name_input = ft.TextField(**theme.get_input_style("Nombre", ft.Icons.FASTFOOD))
        cal_input = ft.TextField(**theme.get_input_style("Kcal (por 100g)"), keyboard_type=ft.KeyboardType.NUMBER)
        prot_input = ft.TextField(**theme.get_input_style("Prot (g)"), keyboard_type=ft.KeyboardType.NUMBER)
        carb_input = ft.TextField(**theme.get_input_style("Carbos (g)"), keyboard_type=ft.KeyboardType.NUMBER)
        fat_input = ft.TextField(**theme.get_input_style("Grasas (g)"), keyboard_type=ft.KeyboardType.NUMBER)
        
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
            except ValueError:
                cal_input.error_text = "Inválido"
                page.update()

        def close_dlg(ev=None):
            dlg.open = False
            page.update()
            
        dlg = ft.AlertDialog(
            title=ft.Text("Crear Alimento Manual"),
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

    def open_add_dialog(f_data, edit_entry=None):
        is_recipe = f_data.get('is_recipe', 0) == 1
        is_liquid = any(word in f_data['name'].lower() for word in ['aceite', 'leche', 'yogur', 'salsa', 'jugo', 'agua', 'miel', 'crema']) and not is_recipe
        unit = "ml" if is_liquid else "g"
        
        if is_recipe:
            base_measure = "Porciones"
            options = [ft.dropdown.Option("Porciones")]
            icon = ft.Icons.PIE_CHART
            default_val = str(edit_entry['amount_g'] / 100.0) if edit_entry else "1"
        else:
            base_measure = "Mililitros" if is_liquid else "Gramos"
            options = [
                ft.dropdown.Option(base_measure),
                ft.dropdown.Option(f"Porción (~100{unit})"),
                ft.dropdown.Option(f"Cucharada (~15{unit})"),
                ft.dropdown.Option(f"Taza (~200{unit})")
            ]
            icon = ft.Icons.WATER_DROP if is_liquid else ft.Icons.SCALE
            default_val = str(edit_entry['amount_g']) if edit_entry else ""
            
        amount_input = ft.TextField(**theme.get_input_style("Cantidad", icon), keyboard_type=ft.KeyboardType.NUMBER, value=default_val)
        measure_dropdown = ft.Dropdown(
            options=options,
            value=base_measure,
            border_color=theme.PRIMARY,
            color=theme.TEXT_PRIMARY,
            border_radius=10,
            filled=True,
            fill_color=theme.SURFACE_VARIANT,
        )
        
        meal_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("Desayuno"),
                ft.dropdown.Option("Almuerzo"),
                ft.dropdown.Option("Cena"),
                ft.dropdown.Option("Snack")
            ],
            value=edit_entry.get('meal_type', 'Snack') if edit_entry else 'Snack',
            border_color=theme.PRIMARY,
            color=theme.TEXT_PRIMARY,
            border_radius=10,
            filled=True,
            fill_color=theme.SURFACE_VARIANT,
        )
        
        def confirm_add(e):
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
                
                cal = f_data['calories_per_100g'] * factor
                prot = f_data['protein_per_100g'] * factor
                carb = f_data['carbs_per_100g'] * factor
                fat = f_data['fat_per_100g'] * factor
                
                if edit_entry:
                    db.update_diary_entry(edit_entry['id'], g, cal, prot, carb, fat, meal_dropdown.value)
                    msg = "Registro actualizado!"
                else:
                    db.add_diary_entry(f_data['id'], f_data['name'], g, cal, prot, carb, fat, meal_dropdown.value)
                    msg = f"{f_data['name']} agregado al diario!"
                    
                dlg.open = False
                render_diary()
                page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor=theme.PRIMARY)
                page.snack_bar.open = True
                page.update()
            except ValueError:
                amount_input.error_text = "Ingresa un valor válido"
                page.update()

        def close_dlg(ev=None):
            dlg.open = False
            page.update()
            
        dlg = ft.AlertDialog(
            title=ft.Text(f"{'Editar' if edit_entry else 'Agregar'} {f_data['name']}"),
            content=ft.Column([amount_input, measure_dropdown, meal_dropdown], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=close_dlg),
                ft.TextButton("Confirmar", on_click=confirm_add),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=theme.SURFACE,
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def open_edit_dialog(entry):
        # Buscar el alimento original para recalcular
        results = db.search_foods(entry['food_name'])
        if results:
            open_add_dialog(results[0], edit_entry=entry)
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Alimento original no encontrado para editar."), bgcolor=theme.DANGER)
            page.snack_bar.open = True
            page.update()

    search_input.on_change = search_click
    search_input.on_submit = search_click
    search_input.on_focus = search_click
    render_diary()
    
    async def initial_search(e=None):
        import asyncio
        await asyncio.sleep(0.1)
        search_click(None)
    page.run_task(initial_search)

    return ft.Column([
        ft.Row([
            ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: navigate_back()),
            theme.header_text("Diario de Consumo")
        ]),
        ft.Container(
            content=ft.Column([
                theme.subheader_text("Buscar Alimentos"),
                ft.Row([search_input, ft.IconButton(ft.Icons.SEARCH, on_click=search_click, icon_color=theme.PRIMARY)]),
                ft.Container(content=results_list, height=250)
            ]),
            **theme.get_card_style()
        ),
        ft.Container(
            content=ft.Column([
                theme.subheader_text("Consumo de Hoy"),
                ft.Container(content=diary_list, height=250)
            ]),
            **theme.get_card_style(),
            expand=True
        )
    ], expand=True)

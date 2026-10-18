import flet as ft
import database as db
from ui import theme, dashboard, profile, diary, recipes, history, setup
import platform

# Fix para el ícono de la barra de tareas en Windows
if platform.system() == "Windows":
    import ctypes
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("com.gestor.calorias.regional")
    except Exception:
        pass

def main(page: ft.Page):
    # Inicializar Base de Datos
    db.init_db()
    
    # Configuración principal de la ventana
    page.title = "Gestor de Calorías Regional"
    page.window_icon = "icon.png"
    theme_pref = db.get_theme_mode()
    page.theme_mode = ft.ThemeMode.DARK if theme_pref == "dark" else ft.ThemeMode.LIGHT
    
    # Configuración de tamaño móvil refinado (proporción smartphone 380x720 para encajar en cualquier monitor)
    try:
        page.window.width = 380
        page.window.height = 720
        page.window.min_width = 340
        page.window.min_height = 580
        page.window.resizable = True
        page.window.center()
    except Exception:
        page.window_width = 380
        page.window_height = 720
        page.window_min_width = 340
        page.window_min_height = 580
        page.window_resizable = True

    page.padding = 0
    page.fonts = {
        "Inter": "https://raw.githubusercontent.com/rsms/inter/master/docs/font-files/Inter-Regular.woff2"
    }
    page.theme = ft.Theme(
        color_scheme_seed=theme.PRIMARY,
        font_family="Inter",
        visual_density=ft.VisualDensity.STANDARD,
    )
    # Fondo en tono Deep Obsidian evitando el negro plano puro
    page.bgcolor = theme.BG_OBSIDIAN if page.theme_mode == ft.ThemeMode.DARK else "#F8FAFC"

    # Encabezado superior premium
    header_title = ft.Text("Gestor Regional", size=18, weight=ft.FontWeight.W_700, color=theme.TEXT_PRIMARY)
    header_subtitle = ft.Text("Salud & Nutrición", size=11, color=theme.TEXT_SECONDARY)
    
    header_avatar = ft.Container(
        content=ft.Icon(ft.Icons.PERSON_ROUNDED, size=18, color=theme.PRIMARY_LIGHT),
        width=36,
        height=36,
        border_radius=18,
        bgcolor=theme.PRIMARY_BG,
        border=ft.border.all(1, theme.with_opacity(0.4, theme.PRIMARY_LIGHT)),
        alignment=ft.Alignment(0, 0),
        on_click=lambda _: show_profile(),
        tooltip="Mi Perfil"
    )

    top_app_bar = ft.Container(
        content=ft.Row([
            ft.Row([
                ft.Container(
                    content=ft.Icon(ft.Icons.SPA_ROUNDED, size=20, color=theme.PRIMARY),
                    width=38,
                    height=38,
                    border_radius=12,
                    bgcolor=theme.SURFACE_VARIANT,
                    border=ft.border.all(1, theme.SURFACE_BORDER),
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Column([
                    header_title,
                    header_subtitle
                ], spacing=1, alignment=ft.MainAxisAlignment.CENTER),
            ], spacing=10),
            ft.Row([
                theme.badge("Regional", icon=ft.Icons.LOCATION_ON_ROUNDED, bg_color="#064E3B", text_color=theme.PRIMARY_LIGHT),
                header_avatar
            ], spacing=8)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=ft.Padding(left=18, top=12, right=18, bottom=12),
        bgcolor=theme.SURFACE,
        border=ft.Border(bottom=ft.BorderSide(1, theme.SURFACE_BORDER)),
    )

    # Área de contenido animada fluida
    content_area = ft.AnimatedSwitcher(
        content=ft.Container(),
        transition=ft.AnimatedSwitcherTransition.FADE,
        duration=200,
        reverse_duration=150,
        switch_in_curve=ft.AnimationCurve.EASE_OUT,
        switch_out_curve=ft.AnimationCurve.EASE_IN,
    )
    
    # Contenedor principal con padding consistente
    main_container = ft.Container(
        content=content_area,
        expand=True,
        padding=ft.Padding(left=16, top=14, right=16, bottom=14)
    )

    def change_route(e):
        route = e.control.selected_index
        if route == 0:
            show_dashboard()
        elif route == 1:
            show_diary()
        elif route == 2:
            show_recipes()
        elif route == 3:
            show_history()
        elif route == 4:
            show_profile()

    # Barra de navegación inferior estilizada
    bottom_nav = ft.NavigationBar(
        bgcolor=theme.SURFACE,
        selected_index=0,
        on_change=change_route,
        indicator_color=theme.with_opacity(0.18, theme.PRIMARY),
        elevation=8,
        border=ft.Border(top=ft.BorderSide(1, theme.SURFACE_BORDER)),
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.DASHBOARD_OUTLINED, 
                selected_icon=ft.Icons.DASHBOARD_ROUNDED, 
                label="Inicio"
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.AUTO_STORIES_OUTLINED, 
                selected_icon=ft.Icons.AUTO_STORIES_ROUNDED, 
                label="Diario"
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.RESTAURANT_MENU_OUTLINED, 
                selected_icon=ft.Icons.RESTAURANT_MENU_ROUNDED, 
                label="Recetas"
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.INSIGHTS_OUTLINED, 
                selected_icon=ft.Icons.INSIGHTS_ROUNDED, 
                label="Historial"
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.PERSON_OUTLINE_ROUNDED, 
                selected_icon=ft.Icons.PERSON_ROUNDED, 
                label="Perfil"
            ),
        ]
    )

    def update_header_info():
        prof = db.get_profile()
        if prof and 'name' in prof:
            header_subtitle.value = f"Hola, {prof['name']} 👋"
        else:
            header_subtitle.value = "Salud & Nutrición"

    def show_dashboard():
        update_header_info()
        content_area.content = dashboard.get_dashboard_view(page, show_diary, show_dashboard)
        bottom_nav.selected_index = 0
        page.update()

    def show_diary():
        update_header_info()
        content_area.content = diary.get_diary_view(page, show_dashboard)
        bottom_nav.selected_index = 1
        page.update()

    def show_recipes():
        update_header_info()
        content_area.content = recipes.get_recipes_view(page)
        bottom_nav.selected_index = 2
        page.update()

    def show_history():
        update_header_info()
        content_area.content = history.get_history_view(page, show_history)
        bottom_nav.selected_index = 3
        page.update()

    def show_profile():
        update_header_info()
        content_area.content = profile.get_profile_view(page, show_dashboard)
        bottom_nav.selected_index = 4
        page.update()

    # Layout principal de la aplicación
    main_layout = ft.Container(
        content=ft.Column([
            top_app_bar,
            main_container,
            bottom_nav
        ], expand=True, spacing=0),
        expand=True,
        visible=False,
        opacity=0,
        animate_opacity=ft.Animation(500, "easeOut")
    )
    
    # ---------------------------------------------
    # PANTALLAS DE INICIO (SPLASH & ONBOARDING)
    # ---------------------------------------------
    
    def show_onboarding():
        setup_view = None

        def finish_setup():
            nonlocal setup_view
            setup_view.visible = False
            main_layout.visible = True
            show_dashboard() 
            page.update()
            async def animate_main(e=None):
                import asyncio
                await asyncio.sleep(0.1)
                main_layout.opacity = 1
                page.update()
                try:
                    page.window.width += 1
                    page.update()
                    page.window.width -= 1
                    page.update()
                except Exception:
                    pass
            page.run_task(animate_main)

        def start_app(e):
            nonlocal setup_view
            onboarding_view.visible = False
            
            setup_view = setup.get_setup_view(page, finish_setup)
            page.add(setup_view)
            page.update()
            
            async def animate_setup(e=None):
                import asyncio
                await asyncio.sleep(0.1)
                setup_view.opacity = 1
                page.update()
                try:
                    page.window.width += 1
                    page.update()
                    page.window.width -= 1
                    page.update()
                except Exception:
                    pass
            page.run_task(animate_setup)
            
        onboarding_view = ft.Container(
            content=ft.Column([
                ft.Container(height=15),
                # Glowing Hero Icon
                ft.Container(
                    content=ft.Icon(ft.Icons.SPA_ROUNDED, size=52, color=theme.PRIMARY_LIGHT),
                    width=96,
                    height=96,
                    border_radius=48,
                    bgcolor=theme.PRIMARY_BG,
                    border=ft.border.all(2, theme.PRIMARY),
                    alignment=ft.Alignment(0, 0),
                    shadow=ft.BoxShadow(
                        blur_radius=25,
                        color=theme.with_opacity(0.35, theme.PRIMARY),
                        offset=ft.Offset(0, 6)
                    ),
                    animate=theme.STANDARD_ANIMATION,
                ),
                ft.Container(height=12),
                ft.Text("Gestor de Calorías", size=24, weight=ft.FontWeight.W_800, color=theme.TEXT_PRIMARY, text_align=ft.TextAlign.CENTER),
                ft.Container(
                    content=theme.badge("Edición Gastronomía Regional", icon=ft.Icons.VERIFIED_ROUNDED, bg_color="#064E3B", text_color=theme.PRIMARY_LIGHT, font_size=11),
                    margin=ft.Margin(0, 2, 0, 4)
                ),
                ft.Text(
                    "Control nutricional de alta precisión para alimentos del Litoral y tradicionales. Fórmulas científicas Mifflin-St Jeor.", 
                    color=theme.TEXT_SECONDARY, size=12, text_align=ft.TextAlign.CENTER
                ),
                ft.Container(height=10),
                # Feature Cards Preview
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, size=14, color=theme.PRIMARY),
                            ft.Text("Catálogo: Chipa, Mbeyú, Reviro, Mandioca", size=11, color=theme.TEXT_PRIMARY)
                        ], spacing=6),
                        ft.Row([
                            ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, size=14, color=theme.COLOR_PROTEIN_LIGHT),
                            ft.Text("Desglose visual de macronutrientes", size=11, color=theme.TEXT_PRIMARY)
                        ], spacing=6),
                        ft.Row([
                            ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, size=14, color=theme.COLOR_WATER_LIGHT),
                            ft.Text("Registro rápido de hidratación (+250 ml)", size=11, color=theme.TEXT_PRIMARY)
                        ], spacing=6),
                    ], spacing=7),
                    bgcolor=theme.SURFACE,
                    padding=12,
                    border_radius=14,
                    border=ft.border.all(1, theme.SURFACE_BORDER)
                ),
                ft.Container(height=12),
                ft.ElevatedButton(
                    "Comenzar Ahora", 
                    icon=ft.Icons.ARROW_FORWARD_ROUNDED,
                    on_click=start_app, 
                    style=theme.get_button_style(), 
                    width=float('inf')
                ),
                ft.Container(height=10),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO),
            padding=ft.Padding(left=18, top=10, right=18, bottom=10),
            expand=True,
            alignment=ft.Alignment(0, 0),
            opacity=0,
            animate_opacity=ft.Animation(600, "easeOut")
        )
        page.add(onboarding_view, main_layout)
        page.update()
        
        async def animate_in(e=None):
            import asyncio
            await asyncio.sleep(0.2)
            onboarding_view.opacity = 1
            page.update()
            try:
                page.window.width += 1
                page.update()
                page.window.width -= 1
                page.update()
            except Exception:
                pass
            
        page.run_task(animate_in)

    # Verificar si existe perfil
    active_profile = db.get_profile()
    if active_profile:
        page.add(main_layout)
        main_layout.visible = True
        show_dashboard()
        page.update()
        
        async def animate_main(e=None):
            import asyncio
            await asyncio.sleep(0.2)
            main_layout.opacity = 1
            page.update()
            try:
                page.window.width += 1
                page.update()
                page.window.width -= 1
                page.update()
            except Exception:
                pass
            
        page.run_task(animate_main)
        
        # Saludo no bloqueante estilizado
        user_name = active_profile.get('name', 'Usuario')
        page.snack_bar = theme.create_snackbar(
            content=ft.Row([
                ft.Icon(ft.Icons.WAVING_HAND_ROUNDED, color=theme.PRIMARY_LIGHT, size=20),
                ft.Text(f"¡Bienvenido de nuevo, {user_name}!", size=13, weight=ft.FontWeight.W_600, color=theme.TEXT_PRIMARY)
            ], spacing=10),
            bgcolor=theme.SURFACE_CARD,
            duration=3000
        )
        page.snack_bar.open = True
        page.update()
    else:
        show_onboarding()

if __name__ == '__main__':
    try:
        ft.run(main, assets_dir="assets")
    except AttributeError:
        ft.app(target=main, assets_dir="assets")

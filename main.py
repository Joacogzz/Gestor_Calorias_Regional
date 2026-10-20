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
    page.theme_mode = ft.ThemeMode.DARK
    
    # Configuración de localización e idioma en español
    page.locale_configuration = ft.LocaleConfiguration(
        supported_locales=[
            ft.Locale("es", "ES"),
            ft.Locale("es", "AR"),
            ft.Locale("es"),
        ],
        current_locale=ft.Locale("es", "ES"),
    )
    
    # Proporción refinada (380x720 para encajar en cualquier monitor)
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
    scrollbar_cfg = ft.ScrollbarTheme(
        thumb_visibility=False,
        track_visibility=False,
        thickness=0,
        radius=0,
        interactive=False,
    )
    page.theme = ft.Theme(
        color_scheme_seed=theme.PRIMARY,
        font_family="Inter",
        visual_density=ft.VisualDensity.STANDARD,
        scrollbar_theme=scrollbar_cfg,
    )
    page.dark_theme = ft.Theme(
        color_scheme_seed=theme.PRIMARY,
        font_family="Inter",
        visual_density=ft.VisualDensity.STANDARD,
        scrollbar_theme=scrollbar_cfg,
    )
    # Fondo en tono Deep Obsidian evitando el negro plano puro
    page.bgcolor = theme.BG_OBSIDIAN

    # Área de contenido animada fluida
    content_area = ft.AnimatedSwitcher(
        content=ft.Container(),
        transition=ft.AnimatedSwitcherTransition.FADE,
        duration=150,
        reverse_duration=120,
        switch_in_curve=ft.AnimationCurve.EASE_OUT,
        switch_out_curve=ft.AnimationCurve.EASE_IN,
    )
    
    # Contenedor principal sin barras redundantes para maximizar espacio vertical
    main_container = ft.Container(
        content=content_area,
        expand=True,
        padding=ft.Padding(left=16, top=14, right=16, bottom=8)
    )

    # Caché en memoria para transiciones de pestaña instantáneas (60 fps)
    cached_views = {}

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

    def show_dashboard():
        content_area.content = dashboard.get_dashboard_view(page, show_diary, show_dashboard)
        bottom_nav.selected_index = 0
        page.update()

    def show_diary(scroll_target=None):
        view = diary.get_diary_view(page, show_dashboard, scroll_target=scroll_target)
        content_area.content = view
        bottom_nav.selected_index = 1
        page.update()
        if scroll_target == "hydration":
            try:
                view.scroll_to(key="water_card", duration=0)
            except Exception:
                pass

    def show_recipes():
        if "recipes" not in cached_views:
            cached_views["recipes"] = recipes.get_recipes_view(page)
        content_area.content = cached_views["recipes"]
        bottom_nav.selected_index = 2
        page.update()

    def show_history():
        content_area.content = history.get_history_view(page, show_history)
        bottom_nav.selected_index = 3
        page.update()

    def show_profile():
        content_area.content = profile.get_profile_view(page, show_dashboard)
        bottom_nav.selected_index = 4
        page.update()

    # Layout principal de la aplicación sin barra superior duplicada
    main_layout = ft.Container(
        content=ft.Column([
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
                ft.Container(height=36),
                # Logotipo Real de la Aplicación
                ft.Container(
                    content=ft.Image(
                        src="icon.png",
                        width=96,
                        height=96,
                        fit=ft.ImageFit.CONTAIN,
                        border_radius=22,
                    ),
                    border_radius=22,
                    shadow=ft.BoxShadow(
                        blur_radius=28,
                        color=theme.with_opacity(0.35, theme.PRIMARY),
                        offset=ft.Offset(0, 6)
                    ),
                    animate=theme.STANDARD_ANIMATION,
                ),
                ft.Container(height=18),
                ft.Text("Gestor de Calorías Regional", size=23, weight=ft.FontWeight.W_800, color=theme.TEXT_PRIMARY, text_align=ft.TextAlign.CENTER),
                ft.Container(height=8),
                ft.Text(
                    "Control nutricional simple y preciso, adaptado a tus hábitos y a los platos tradicionales de nuestra región.", 
                    color=theme.TEXT_SECONDARY, size=13, text_align=ft.TextAlign.CENTER
                ),
                ft.Container(height=28),
                ft.ElevatedButton(
                    "Comenzar Ahora", 
                    icon=ft.Icons.ARROW_FORWARD_ROUNDED,
                    on_click=start_app, 
                    style=theme.get_button_style(), 
                    width=float('inf')
                ),
                ft.Container(height=12),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.HIDDEN),
            padding=ft.Padding(left=24, top=20, right=24, bottom=20),
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
        
        # Saludo no bloqueante sobrio
        user_name = active_profile.get('name', 'Usuario')
        page.snack_bar = theme.create_snackbar(
            content=ft.Row([
                ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, color=theme.PRIMARY_LIGHT, size=18),
                ft.Text(f"Bienvenido de nuevo, {user_name}", size=13, weight=ft.FontWeight.W_600, color=theme.TEXT_PRIMARY)
            ], spacing=8),
            bgcolor=theme.SURFACE_CARD,
            duration=2500
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

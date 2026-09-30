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
    # Configuración de tamaño móvil / celular (390 x 844, centrado y fijo)
    try:
        page.window.width = 390
        page.window.height = 844
        page.window.resizable = False
        page.window.center()
    except Exception:
        page.window_width = 390
        page.window_height = 844
        page.window_resizable = False
    page.padding = 0
    page.fonts = {
        "Inter": "https://raw.githubusercontent.com/rsms/inter/master/docs/font-files/Inter-Regular.woff2"
    }
    page.theme = ft.Theme(color_scheme_seed="#007AFF", font_family="Inter")
    # Forzar fondo puro negro o puro blanco según estilo iOS
    page.bgcolor = "#000000" if page.theme_mode == ft.ThemeMode.DARK else "#FFFFFF"

    # Área de contenido animada
    content_area = ft.AnimatedSwitcher(
        content=ft.Container(),
        transition=ft.AnimatedSwitcherTransition.FADE,
        duration=150,
        reverse_duration=150,
        switch_in_curve=ft.AnimationCurve.EASE_OUT,
        switch_out_curve=ft.AnimationCurve.EASE_IN,
    )
    
    # Contenedor principal con fondo (para dar espacio al switcher)
    main_container = ft.Container(
        content=content_area,
        expand=True,
        padding=20
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

    bottom_nav = ft.NavigationBar(
        bgcolor=theme.SURFACE,
        selected_index=0,
        on_change=change_route,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.DASHBOARD_OUTLINED, selected_icon=ft.Icons.DASHBOARD, label="Inicio"),
            ft.NavigationBarDestination(icon=ft.Icons.BOOK_OUTLINED, selected_icon=ft.Icons.BOOK, label="Diario"),
            ft.NavigationBarDestination(icon=ft.Icons.RESTAURANT_MENU_OUTLINED, selected_icon=ft.Icons.RESTAURANT_MENU, label="Recetas"),
            ft.NavigationBarDestination(icon=ft.Icons.CALENDAR_MONTH_OUTLINED, selected_icon=ft.Icons.CALENDAR_MONTH, label="Historial"),
            ft.NavigationBarDestination(icon=ft.Icons.PERSON_OUTLINE, selected_icon=ft.Icons.PERSON, label="Perfil"),
        ]
    )

    def show_dashboard():
        content_area.content = dashboard.get_dashboard_view(page, show_diary, show_dashboard)
        bottom_nav.selected_index = 0
        page.update()

    def show_diary():
        content_area.content = diary.get_diary_view(page, show_dashboard)
        bottom_nav.selected_index = 1
        page.update()

    def show_recipes():
        content_area.content = recipes.get_recipes_view(page)
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

    # Layout principal que se inyectará después de la bienvenida
    main_layout = ft.Container(
        content=ft.Column([
            main_container,
            bottom_nav
        ], expand=True, spacing=0),
        expand=True,
        visible=False,
        opacity=0,
        animate_opacity=ft.Animation(800, "easeOut")
    )
    
    # ---------------------------------------------
    # PANTALLAS DE INICIO (SPLASH & ONBOARDING)
    # ---------------------------------------------
    
    def show_onboarding():
        # Referencias de vistas
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
                # Hack para forzar el repintado
                page.window_width += 1
                page.update()
                page.window_width -= 1
                page.update()
            page.run_task(animate_main)

        def start_app(e):
            nonlocal setup_view
            onboarding_view.visible = False
            
            # Crear y añadir la vista de Setup
            setup_view = setup.get_setup_view(page, finish_setup)
            page.add(setup_view)
            page.update()
            
            async def animate_setup(e=None):
                import asyncio
                await asyncio.sleep(0.1)
                setup_view.opacity = 1
                page.update()
                # Hack para forzar el repintado
                page.window_width += 1
                page.update()
                page.window_width -= 1
                page.update()
            page.run_task(animate_setup)
            
        onboarding_view = ft.Container(
            content=ft.Column([
                ft.Container(height=80),
                ft.Icon(ft.Icons.RESTAURANT_MENU, size=120, color=theme.PRIMARY),
                ft.Container(height=30),
                ft.Text("Gestor de Calorías Regional", size=28, weight=ft.FontWeight.BOLD, color=theme.TEXT_PRIMARY, text_align=ft.TextAlign.CENTER),
                ft.Container(height=10),
                ft.Text(
                    "Tu asistente nutricional inteligente. Registra tus comidas, alcanza tus metas científicas y visualiza tu progreso en una interfaz premium.", 
                    color=theme.TEXT_SECONDARY, size=14, text_align=ft.TextAlign.CENTER
                ),
                ft.Container(expand=True),
                ft.ElevatedButton("Comenzar Ahora", on_click=start_app, style=theme.get_button_style(), width=float('inf')),
                ft.Container(height=40),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=30,
            expand=True,
            alignment=ft.Alignment(0, 0),
            opacity=0,
            animate_opacity=ft.Animation(800, "easeOut")
        )
        page.add(onboarding_view, main_layout)
        page.update()
        
        async def animate_in(e=None):
            import asyncio
            await asyncio.sleep(0.3) # Dar tiempo a que el motor renderice el estado invisible primero
            onboarding_view.opacity = 1
            page.update()
            # Hack para forzar el repintado en Windows WebView2
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
            await asyncio.sleep(0.3)
            main_layout.opacity = 1
            page.update()
            # Hack para forzar el repintado en Windows WebView2
            try:
                page.window.width += 1
                page.update()
                page.window.width -= 1
                page.update()
            except Exception:
                pass
            
        page.run_task(animate_main)
        
        # Saludo no bloqueante y premium
        page.snack_bar = ft.SnackBar(
            ft.Text(f"¡Hola de nuevo, {active_profile['name']}! 👋", size=16, weight=ft.FontWeight.BOLD),
            bgcolor=theme.PRIMARY,
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

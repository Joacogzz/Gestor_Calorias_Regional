import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

# Register native Calibri fonts from Windows
pdfmetrics.registerFont(TTFont('Calibri', 'C:/Windows/Fonts/calibri.ttf'))
pdfmetrics.registerFont(TTFont('Calibri-Bold', 'C:/Windows/Fonts/calibrib.ttf'))
pdfmetrics.registerFont(TTFont('Calibri-Italic', 'C:/Windows/Fonts/calibrii.ttf'))
pdfmetrics.registerFont(TTFont('Calibri-BoldItalic', 'C:/Windows/Fonts/calibriz.ttf'))

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        
        # Header (Top 2.5cm area) - Todo en negro formal
        self.setFont("Calibri", 10)
        self.setFillColor(colors.black)
        
        header_text = [
            "ANALISTA EN SISTEMAS",
            "Ciclo Lectivo 2026",
            "Gestor de Calorías Regional"
        ]
        y_pos = 29.7 * cm - 1.2 * cm
        for line in header_text:
            self.drawCentredString(21.0 * cm / 2.0, y_pos, line)
            y_pos -= 12
            
        # Linea divisoria superior en negro
        self.setStrokeColor(colors.black)
        self.setLineWidth(0.5)
        self.line(3.0 * cm, 29.7 * cm - 2.2 * cm, 21.0 * cm - 1.5 * cm, 29.7 * cm - 2.2 * cm)
        
        # Footer en negro
        footer_y = 1.3 * cm
        self.line(3.0 * cm, footer_y + 12, 21.0 * cm - 1.5 * cm, footer_y + 12)
        
        self.setFont("Calibri", 10)
        self.drawString(3.0 * cm, footer_y, "Gómez, Axel Joaquín")
        self.drawRightString(21.0 * cm - 1.5 * cm, footer_y, str(self._pageNumber))
        
        self.restoreState()

def build_pdf(filename):
    # Margins: Left 3cm, Right 1.5cm, Top 2.3cm, Bottom 2.0cm
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=3.0 * cm,
        rightMargin=1.5 * cm,
        topMargin=2.3 * cm,
        bottomMargin=2.0 * cm
    )

    title_style = ParagraphStyle(
        'DocTitle',
        fontName='Calibri-Bold',
        fontSize=14,
        leading=17,
        textColor=colors.black,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'DocBody',
        fontName='Calibri',
        fontSize=9,
        leading=12,
        textColor=colors.black,
        spaceAfter=6,
        alignment=4 # Justificado
    )
    
    body_italic = ParagraphStyle(
        'DocBodyItalic',
        fontName='Calibri-Italic',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.black,
        spaceAfter=6
    )
    
    repo_box_style = ParagraphStyle(
        'RepoBox',
        fontName='Calibri-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.black
    )
    
    repo_url_style = ParagraphStyle(
        'RepoUrl',
        fontName='Calibri',
        fontSize=9,
        leading=12,
        textColor=colors.black
    )

    table_header_style = ParagraphStyle(
        'TH',
        fontName='Calibri-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.black,
        alignment=1 # Centrado
    )
    
    cell_req = ParagraphStyle('CR', fontName='Calibri-Bold', fontSize=7.5, leading=9.5, alignment=1, textColor=colors.black)
    cell_desc = ParagraphStyle('CD', fontName='Calibri', fontSize=7.5, leading=9.5, textColor=colors.black)
    cell_arch = ParagraphStyle('CA', fontName='Calibri', fontSize=7, leading=9, textColor=colors.black)
    cell_func = ParagraphStyle('CF', fontName='Calibri', fontSize=7, leading=9, textColor=colors.black)
    cell_status = ParagraphStyle('CS', fontName='Calibri-Bold', fontSize=7.5, leading=9.5, textColor=colors.black, alignment=1)
    cell_obs = ParagraphStyle('CO', fontName='Calibri', fontSize=7, leading=8.5, textColor=colors.black)

    story = []

    # Titulo seccion 6.3
    story.append(Paragraph("6.3. Tabla de Trazabilidad y Estado de Avance", title_style))
    story.append(Paragraph(
        "A continuación se presenta la tabla de trazabilidad que vincula la totalidad de los requerimientos funcionales definidos en el punto 5.7 con los componentes de software implementados a la fecha en la arquitectura del proyecto. Se consigna el estado real de avance de cada ítem, detallando los archivos fuente y métodos específicos que dan soporte a su funcionamiento.",
        body_style
    ))
    story.append(Spacer(1, 4))

    # Tabla de Trazabilidad (Monocromo)
    col_widths = [1.2 * cm, 4.0 * cm, 2.4 * cm, 2.6 * cm, 2.3 * cm, 4.0 * cm]
    
    table_data = [
        [
            Paragraph("Req.", table_header_style),
            Paragraph("Descripción (5.7)", table_header_style),
            Paragraph("Archivo / Módulo", table_header_style),
            Paragraph("Función / Pantalla", table_header_style),
            Paragraph("Estado", table_header_style),
            Paragraph("Observación", table_header_style)
        ],
        [
            Paragraph("R1", cell_req),
            Paragraph("El usuario debe poder crear y seleccionar un perfil local.", cell_desc),
            Paragraph("ui/profile.py<br/>ui/setup.py<br/>database.py", cell_arch),
            Paragraph("get_profile_view()<br/>on_profile_change()<br/>save_profile()", cell_func),
            Paragraph("Implementado", cell_status),
            Paragraph("—", cell_obs)
        ],
        [
            Paragraph("R2", cell_req),
            Paragraph("El usuario debe poder configurar su perfil biométrico y metas.", cell_desc),
            Paragraph("ui/profile.py<br/>ui/setup.py<br/>database.py", cell_arch),
            Paragraph("auto_recalculate()<br/>update_profile()<br/>save_profile()", cell_func),
            Paragraph("Implementado", cell_status),
            Paragraph("—", cell_obs)
        ],
        [
            Paragraph("R3", cell_req),
            Paragraph("El usuario debe poder buscar alimentos regionales en el sistema.", cell_desc),
            Paragraph("ui/diary.py<br/>database.py", cell_arch),
            Paragraph("search_foods()<br/>open_food_picker()", cell_func),
            Paragraph("Implementado", cell_status),
            Paragraph("—", cell_obs)
        ],
        [
            Paragraph("R4", cell_req),
            Paragraph("El usuario debe poder registrar los alimentos consumidos en el día.", cell_desc),
            Paragraph("ui/diary.py<br/>database.py", cell_arch),
            Paragraph("add_diary_entry()<br/>open_add_dialog()", cell_func),
            Paragraph("Implementado", cell_status),
            Paragraph("—", cell_obs)
        ],
        [
            Paragraph("R5", cell_req),
            Paragraph("El sistema debe calcular automáticamente las calorías consumidas.", cell_desc),
            Paragraph("ui/dashboard.py<br/>ui/diary.py", cell_arch),
            Paragraph("get_dashboard_view()<br/>open_add_dialog()", cell_func),
            Paragraph("Implementado", cell_status),
            Paragraph("—", cell_obs)
        ],
        [
            Paragraph("R6", cell_req),
            Paragraph("El sistema debe calcular el desglose de macronutrientes.", cell_desc),
            Paragraph("ui/dashboard.py<br/>ui/diary.py", cell_arch),
            Paragraph("macro_card()<br/>get_dashboard_view()", cell_func),
            Paragraph("Implementado", cell_status),
            Paragraph("—", cell_obs)
        ],
        [
            Paragraph("R7", cell_req),
            Paragraph("El usuario debe poder ingresar el gramaje exacto o en medidas caseras.", cell_desc),
            Paragraph("ui/diary.py", cell_arch),
            Paragraph("open_add_dialog()<br/>unit selector", cell_func),
            Paragraph("Implementado", cell_status),
            Paragraph("—", cell_obs)
        ],
        [
            Paragraph("R8", cell_req),
            Paragraph("El usuario debe poder crear y guardar recetas propias.", cell_desc),
            Paragraph("ui/recipes.py<br/>database.py", cell_arch),
            Paragraph("save_recipe_dialog()<br/>save_recipe()", cell_func),
            Paragraph("Implementado", cell_status),
            Paragraph("—", cell_obs)
        ],
        [
            Paragraph("R9", cell_req),
            Paragraph("El usuario debe poder marcar alimentos de consumo frecuente como 'Favoritos'.", cell_desc),
            Paragraph("database.py<br/>ui/diary.py", cell_arch),
            Paragraph("toggle_favorite()<br/>search_foods()", cell_func),
            Paragraph("Implementado", cell_status),
            Paragraph("—", cell_obs)
        ],
        [
            Paragraph("R10", cell_req),
            Paragraph("El usuario debe poder editar o eliminar registros de alimentos del diario.", cell_desc),
            Paragraph("ui/diary.py<br/>database.py", cell_arch),
            Paragraph("edit_entry()<br/>delete_diary_entry()", cell_func),
            Paragraph("Implementado", cell_status),
            Paragraph("—", cell_obs)
        ],
        [
            Paragraph("R11", cell_req),
            Paragraph("El sistema debe calcular la variación de peso de los alimentos por cocción.", cell_desc),
            Paragraph("ui/recipes.py", cell_arch),
            Paragraph("create_recipe_view()<br/>calculate_macros()", cell_func),
            Paragraph("Parcial", cell_status),
            Paragraph("Aplica factor de merma y distribución por porciones en la receta total, pero aún no discrimina coeficientes específicos por tipo de ingrediente.", cell_obs)
        ],
        [
            Paragraph("R12", cell_req),
            Paragraph("El usuario debe poder ver un historial gráfico con su progreso de peso.", cell_desc),
            Paragraph("ui/profile.py<br/>database.py", cell_arch),
            Paragraph("get_weight_logs()<br/>ft.LineChart", cell_func),
            Paragraph("Implementado", cell_status),
            Paragraph("—", cell_obs)
        ],
        [
            Paragraph("R13", cell_req),
            Paragraph("El usuario debe poder registrar su consumo diario de agua.", cell_desc),
            Paragraph("ui/dashboard.py<br/>ui/history.py<br/>database.py", cell_arch),
            Paragraph("add_water()<br/>get_water_today()<br/>water_card", cell_func),
            Paragraph("Implementado", cell_status),
            Paragraph("—", cell_obs)
        ],
        [
            Paragraph("R14", cell_req),
            Paragraph("El sistema debe mostrar alertas visuales cuando el usuario supere su límite.", cell_desc),
            Paragraph("ui/dashboard.py<br/>ui/history.py", cell_arch),
            Paragraph("get_dashboard_view()<br/>theme.DANGER trigger", cell_func),
            Paragraph("Implementado", cell_status),
            Paragraph("—", cell_obs)
        ],
    ]

    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E5E5E5")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#333333")),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9F9F9")]),
        ('TOPPADDING', (0, 0), (-1, -1), 2.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.2),
        ('LEFTPADDING', (0, 0), (-1, -1), 3.5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3.5),
    ]))
    story.append(t)
    story.append(Spacer(1, 6))

    # Repositorio (Monocromo)
    repo_data = [
        [
            Paragraph("Enlace al repositorio del proyecto (GitHub):", repo_box_style),
            Paragraph("<u>https://github.com/Joacogzz/Gestor_Calorias_Regional</u>", repo_url_style)
        ]
    ]
    repo_table = Table(repo_data, colWidths=[6.5 * cm, 10.0 * cm])
    repo_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F2F2F2")),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(repo_table)

    # Salto de pagina exacto para seccion 2
    story.append(PageBreak())

    # Seccion 2: Indice de la carpeta y estado de avance (Monocromo)
    story.append(Paragraph("Estado de Avance General de la Carpeta de Proyecto", title_style))
    story.append(Paragraph(
        "A continuación se presenta el índice estructurado del proyecto según el esquema reglamentario de la cátedra, consignando para cada apartado el estado en el que se encuentra a la fecha (Terminado, En desarrollo o Sin iniciar), sirviendo como relevamiento de la marcha del trabajo.",
        body_style
    ))
    story.append(Spacer(1, 4))

    idx_widths = [1.8 * cm, 9.7 * cm, 3.0 * cm, 2.0 * cm]
    
    idx_th = ParagraphStyle('ITH', fontName='Calibri-Bold', fontSize=8.5, leading=11, textColor=colors.black, alignment=1)
    idx_c_num = ParagraphStyle('ICN', fontName='Calibri-Bold', fontSize=8, leading=10, alignment=1, textColor=colors.black)
    idx_c_item = ParagraphStyle('ICI', fontName='Calibri', fontSize=8, leading=10, textColor=colors.black)
    idx_c_item_bold = ParagraphStyle('ICIB', fontName='Calibri-Bold', fontSize=8, leading=10, textColor=colors.black)
    idx_st = ParagraphStyle('IST', fontName='Calibri-Bold', fontSize=8, leading=10, textColor=colors.black, alignment=1)
    idx_pct = ParagraphStyle('IPCT', fontName='Calibri', fontSize=8, leading=10, alignment=1, textColor=colors.black)

    index_table_data = [
        [
            Paragraph("Punto", idx_th),
            Paragraph("Sección / Apartado", idx_th),
            Paragraph("Estado de Avance", idx_th),
            Paragraph("% Estimado", idx_th)
        ],
        [Paragraph("1.", idx_c_num), Paragraph("Carátula institucional", idx_c_item_bold), Paragraph("Terminado", idx_st), Paragraph("100%", idx_pct)],
        [Paragraph("2.", idx_c_num), Paragraph("Índice general", idx_c_item_bold), Paragraph("Terminado", idx_st), Paragraph("100%", idx_pct)],
        [Paragraph("3.", idx_c_num), Paragraph("Título del sistema", idx_c_item_bold), Paragraph("Terminado", idx_st), Paragraph("100%", idx_pct)],
        [Paragraph("4.", idx_c_num), Paragraph("Resumen del sistema (Abstract)", idx_c_item_bold), Paragraph("Terminado", idx_st), Paragraph("100%", idx_pct)],
        [Paragraph("5.", idx_c_num), Paragraph("Análisis", idx_c_item_bold), Paragraph("Terminado", idx_st), Paragraph("100%", idx_pct)],
        [Paragraph("5.1.", idx_c_num), Paragraph("&nbsp;&nbsp;Introducción y problemática", idx_c_item), Paragraph("Terminado", idx_st), Paragraph("100%", idx_pct)],
        [Paragraph("5.2.", idx_c_num), Paragraph("&nbsp;&nbsp;Descripción general del sistema", idx_c_item), Paragraph("Terminado", idx_st), Paragraph("100%", idx_pct)],
        [Paragraph("5.3.", idx_c_num), Paragraph("&nbsp;&nbsp;Justificación técnica y operativa", idx_c_item), Paragraph("Terminado", idx_st), Paragraph("100%", idx_pct)],
        [Paragraph("5.4.", idx_c_num), Paragraph("&nbsp;&nbsp;Objetivos generales", idx_c_item), Paragraph("Terminado", idx_st), Paragraph("100%", idx_pct)],
        [Paragraph("5.5.", idx_c_num), Paragraph("&nbsp;&nbsp;Objetivos específicos", idx_c_item), Paragraph("Terminado", idx_st), Paragraph("100%", idx_pct)],
        [Paragraph("5.6.", idx_c_num), Paragraph("&nbsp;&nbsp;Límites del sistema (Alcance)", idx_c_item), Paragraph("Terminado", idx_st), Paragraph("100%", idx_pct)],
        [Paragraph("5.7.", idx_c_num), Paragraph("&nbsp;&nbsp;Requerimientos del sistema y Casos de uso", idx_c_item), Paragraph("Terminado", idx_st), Paragraph("100%", idx_pct)],
        [Paragraph("5.8.", idx_c_num), Paragraph("&nbsp;&nbsp;Estudio de factibilidad (Técnica, Operativa, Económica)", idx_c_item), Paragraph("Terminado", idx_st), Paragraph("100%", idx_pct)],
        [Paragraph("5.9.", idx_c_num), Paragraph("&nbsp;&nbsp;Cronograma (Diagrama de Gantt)", idx_c_item), Paragraph("Terminado", idx_st), Paragraph("100%", idx_pct)],
        [Paragraph("5.10.", idx_c_num), Paragraph("&nbsp;&nbsp;Presupuesto de recursos", idx_c_item), Paragraph("Terminado", idx_st), Paragraph("100%", idx_pct)],
        [Paragraph("6.", idx_c_num), Paragraph("Diseño", idx_c_item_bold), Paragraph("En desarrollo", idx_st), Paragraph("80%", idx_pct)],
        [Paragraph("6.1.", idx_c_num), Paragraph("&nbsp;&nbsp;Reglas de negocio del sistema", idx_c_item), Paragraph("En desarrollo", idx_st), Paragraph("75%", idx_pct)],
        [Paragraph("6.2.", idx_c_num), Paragraph("&nbsp;&nbsp;Herramientas de modelado de datos (DFD)", idx_c_item), Paragraph("En desarrollo", idx_st), Paragraph("60%", idx_pct)],
        [Paragraph("6.3.", idx_c_num), Paragraph("&nbsp;&nbsp;Base de datos (DER, trazabilidad y mapa canónico)", idx_c_item), Paragraph("En desarrollo", idx_st), Paragraph("85%", idx_pct)],
        [Paragraph("6.4.", idx_c_num), Paragraph("&nbsp;&nbsp;Frontend / Prototipo (Móvil Flet)", idx_c_item), Paragraph("En desarrollo", idx_st), Paragraph("90%", idx_pct)],
        [Paragraph("7.", idx_c_num), Paragraph("Conclusión sobre el proyecto", idx_c_item_bold), Paragraph("Terminado", idx_st), Paragraph("100%", idx_pct)],
        [Paragraph("8.", idx_c_num), Paragraph("Bibliografía (Normas APA)", idx_c_item_bold), Paragraph("Terminado", idx_st), Paragraph("100%", idx_pct)],
        [Paragraph("9.", idx_c_num), Paragraph("Glosario de palabras técnicas", idx_c_item_bold), Paragraph("Terminado", idx_st), Paragraph("100%", idx_pct)],
    ]

    t_idx = Table(index_table_data, colWidths=idx_widths, repeatRows=1)
    t_idx.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E5E5E5")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#333333")),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9F9F9")]),
        ('TOPPADDING', (0, 0), (-1, -1), 2.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.2),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_idx)
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "<b>Nota explicativa:</b> Los apartados del Capítulo 5 (Análisis), la conclusión preliminar, la bibliografía y el glosario se encuentran completamente redactados y consolidados. El Capítulo 6 (Diseño) se encuentra en su etapa final de desarrollo: el modelo entidad-relación de la base de datos está implementado en SQLite, el prototipo móvil en Flet está 100% operativo en su lógica de negocio y la presente tabla de trazabilidad releva el estado de los requerimientos para la entrega definitiva de octubre.",
        body_italic
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF generado con éxito: {filename}")

if __name__ == '__main__':
    out_pdf = r"C:\Users\Joaquín\Documents\Facultad\Practica profesional\Gestor de calorias regional\Tabla_de_Trazabilidad_Punto_6.3_Gomez_Axel_Joaquin.pdf"
    build_pdf(out_pdf)

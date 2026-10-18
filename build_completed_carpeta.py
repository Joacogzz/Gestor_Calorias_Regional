import os
import shutil
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def style_table(table):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        f'<w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        f'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        f'<w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="333333"/>'
        f'<w:insideV w:val="single" w:sz="4" w:space="0" w:color="333333"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def add_p(target_p, text="", bold=False, italic=False, size_pt=12, 
          align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=6, 
          first_line_indent=1.27):
    p = target_p.insert_paragraph_before()
    p.alignment = align
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    if first_line_indent > 0:
        p.paragraph_format.first_line_indent = Inches(first_line_indent / 2.54)
    else:
        p.paragraph_format.first_line_indent = 0
    if text:
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(size_pt)
        r.bold = bold
        r.italic = italic
        r.font.color.rgb = RGBColor(0, 0, 0)
    return p

def add_heading_1(target_p, text):
    return add_p(target_p, text, bold=True, size_pt=16, 
                 align=WD_ALIGN_PARAGRAPH.LEFT, space_before=14, space_after=8, first_line_indent=0)

def add_heading_2(target_p, text):
    return add_p(target_p, text, bold=True, size_pt=14, 
                 align=WD_ALIGN_PARAGRAPH.LEFT, space_before=12, space_after=6, first_line_indent=0)

def add_heading_3(target_p, text):
    return add_p(target_p, text, bold=True, size_pt=12.5, 
                 align=WD_ALIGN_PARAGRAPH.LEFT, space_before=8, space_after=4, first_line_indent=0)

def add_bullet(target_p, prefix="", text=""):
    p = target_p.insert_paragraph_before()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.left_indent = Inches(1.27 / 2.54)
    p.paragraph_format.first_line_indent = Inches(-0.63 / 2.54)
    
    r_sym = p.add_run("• ")
    r_sym.font.name = "Calibri"
    r_sym.font.size = Pt(12)
    r_sym.font.color.rgb = RGBColor(0, 0, 0)
    
    if prefix:
        r_pre = p.add_run(prefix + " ")
        r_pre.font.name = "Calibri"
        r_pre.font.size = Pt(12)
        r_pre.bold = True
        r_pre.font.color.rgb = RGBColor(0, 0, 0)
    
    if text:
        r_txt = p.add_run(text)
        r_txt.font.name = "Calibri"
        r_txt.font.size = Pt(12)
        r_txt.font.color.rgb = RGBColor(0, 0, 0)
    return p

def add_image_box(target_p, doc, img_path, width_in_inches, caption=""):
    p_img = target_p.insert_paragraph_before()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(10)
    p_img.paragraph_format.space_after = Pt(4)
    p_img.paragraph_format.first_line_indent = 0
    run_img = p_img.add_run()
    run_img.add_picture(img_path, width=Inches(width_in_inches))
    
    if caption:
        p_cap = target_p.insert_paragraph_before()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(2)
        p_cap.paragraph_format.space_after = Pt(10)
        p_cap.paragraph_format.first_line_indent = 0
        run_cap = p_cap.add_run(caption)
        run_cap.font.name = "Calibri"
        run_cap.font.size = Pt(10)
        run_cap.italic = True
        run_cap.font.color.rgb = RGBColor(0, 0, 0)

def add_two_screenshots_card(target_p, doc, img_path1, cap1, img_path2, cap2, img_width_inches=2.20):
    table = doc.add_table(rows=2, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="none"/>'
        f'<w:left w:val="none"/>'
        f'<w:bottom w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:insideH w:val="none"/>'
        f'<w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)
    
    # Prevent row splitting across pages
    for row in table.rows:
        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

    col_w = Inches(3.35)
    for row in table.rows:
        for cell in row.cells:
            cell.width = col_w

    # Row 0: Images
    row_img = table.rows[0]
    for c_idx, img_path in enumerate([img_path1, img_path2]):
        cell = row_img.cells[c_idx]
        set_cell_margins(cell, top=60, bottom=40, left=20, right=20)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.first_line_indent = 0
        run = p.add_run()
        run.add_picture(img_path, width=Inches(img_width_inches))

    # Row 1: Captions
    row_cap = table.rows[1]
    for c_idx, cap in enumerate([cap1, cap2]):
        cell = row_cap.cells[c_idx]
        set_cell_margins(cell, top=20, bottom=60, left=20, right=20)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.first_line_indent = 0
        run = p.add_run(cap)
        run.font.name = "Calibri"
        run.font.size = Pt(9.5)
        run.italic = True
        run.font.color.rgb = RGBColor(0, 0, 0)

    target_p._element.addprevious(table._element)
    
    p_sp = target_p.insert_paragraph_before()
    p_sp.paragraph_format.space_before = Pt(0)
    p_sp.paragraph_format.space_after = Pt(6)
    p_sp.paragraph_format.first_line_indent = 0
    return table

def add_custom_table(target_p, doc, headers, rows_data, col_widths=None, header_bg="000000", header_text_color="FFFFFF"):
    num_rows = len(rows_data) + 1
    num_cols = len(headers)
    table = doc.add_table(rows=num_rows, cols=num_cols)
    style_table(table)
    
    # Header row
    hdr_cells = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].text = h
        set_cell_background(hdr_cells[i], header_bg)
        set_cell_margins(hdr_cells[i], top=100, bottom=100, left=120, right=120)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        for r in p.runs:
            r.font.name = "Calibri"
            r.font.size = Pt(9.5)
            r.bold = True
            r.font.color.rgb = RGBColor(255, 255, 255) if header_text_color == "FFFFFF" else RGBColor(0, 0, 0)
            
    # Body rows
    for r_idx, row_values in enumerate(rows_data):
        row_cells = table.rows[r_idx + 1].cells
        bg_fill = "F9F9F9" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row_values):
            row_cells[c_idx].text = str(val)
            if bg_fill != "FFFFFF":
                set_cell_background(row_cells[c_idx], bg_fill)
            set_cell_margins(row_cells[c_idx], top=80, bottom=80, left=120, right=120)
            p = row_cells[c_idx].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0, 2, 3] and len(headers) <= 6 else WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            for r in p.runs:
                r.font.name = "Calibri"
                r.font.size = Pt(9)
                r.font.color.rgb = RGBColor(0, 0, 0)
                if c_idx == 0:
                    r.bold = True
                    
    # Column widths
    if col_widths:
        for row in table.rows:
            for idx, w in enumerate(col_widths):
                row.cells[idx].width = Inches(w)
                
    target_p._element.addprevious(table._element)
    
    p_sp = target_p.insert_paragraph_before()
    p_sp.paragraph_format.space_before = Pt(0)
    p_sp.paragraph_format.space_after = Pt(8)
    p_sp.paragraph_format.first_line_indent = 0
    return table

def add_repo_box(target_p, doc, repo_url):
    table = doc.add_table(rows=1, cols=1)
    style_table(table)
    cell = table.cell(0, 0)
    set_cell_background(cell, "F2F2F2")
    set_cell_margins(cell, top=140, bottom=140, left=180, right=180)
    
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.first_line_indent = 0
    r1 = p.add_run("Enlace al Repositorio del Proyecto (Código Fuente en GitHub): ")
    r1.font.name = "Calibri"
    r1.font.size = Pt(10)
    r1.bold = True
    r1.font.color.rgb = RGBColor(0, 0, 0)
    
    r2 = p.add_run(repo_url)
    r2.font.name = "Calibri"
    r2.font.size = Pt(10)
    r2.underline = True
    r2.font.color.rgb = RGBColor(0, 0, 0)
    
    target_p._element.addprevious(table._element)
    
    p_sp = target_p.insert_paragraph_before()
    p_sp.paragraph_format.space_before = Pt(0)
    p_sp.paragraph_format.space_after = Pt(8)
    p_sp.paragraph_format.first_line_indent = 0

def complete_project_folder(toc_page_dict=None):
    base_docx = r"C:\Users\Joaquín\Documents\Facultad\Practica profesional\Gestor de calorias regional\Carpeta\Carpeta (Gómez Axel Joaquín).docx"
    target_docx = r"C:\Users\Joaquín\Documents\Facultad\Practica profesional\Gestor de calorias regional\Carpeta\Carpeta final (Gómez Axel Joaquín).docx"
    downloads_docx = r"C:\Users\Joaquín\Downloads\Carpeta\Carpeta final (Gómez Axel Joaquín).docx"
    
    project_logo_path = r"C:\Users\Joaquín\Documents\Facultad\Practica profesional\Gestor de calorias regional\Logo Gestor de Calorias Regional.png"
    er_img_path = r"C:\Users\Joaquín\Documents\Facultad\Practica profesional\Gestor de calorias regional\Carpeta\diagrama_er_base_datos.png"
    dfd_img_path = r"C:\Users\Joaquín\Documents\Facultad\Practica profesional\Gestor de calorias regional\Carpeta\diagrama_dfd_proyecto.png"
    
    capturas_dir = r"C:\Users\Joaquín\Documents\Facultad\Practica profesional\Gestor de calorias regional\Carpeta\capturas"
    if not os.path.exists(capturas_dir):
        capturas_dir = r"C:\Users\Joaquín\Downloads\Carpeta\capturas"
        
    img_bienvenida = os.path.join(capturas_dir, "1.PantallaBienvenida.jpg")
    img_perfil_setup = os.path.join(capturas_dir, "2.CrearPerfil.jpg")
    img_dashboard = os.path.join(capturas_dir, "3.Dashboard.jpg")
    img_diario = os.path.join(capturas_dir, "4.Diario.jpg")
    img_recetas = os.path.join(capturas_dir, "5.Recetas.jpg")
    img_alimentos = os.path.join(capturas_dir, "7.Alimentos.jpg")
    img_historial = os.path.join(capturas_dir, "8.Historial.jpg")
    img_perfil = os.path.join(capturas_dir, "9.Perfil.jpg")
    
    print("Loading base document...")
    doc = Document(base_docx)
    
    # Set symmetric margins: 2.0 cm left, 2.0 cm right, 2.5 cm top, 2.5 cm bottom
    print("Configuring symmetric margins (2.0 cm left, 2.0 cm right)...")
    for s in doc.sections:
        s.left_margin = Inches(2.0 / 2.54)
        s.right_margin = Inches(2.0 / 2.54)
        s.top_margin = Inches(2.5 / 2.54)
        s.bottom_margin = Inches(2.5 / 2.54)
    
    # -------------------------------------------------------------------------
    # 1. Update Header in Section 1 (from ANÁLISIS DE SISTEMAS to ANALISTA EN SISTEMAS)
    # -------------------------------------------------------------------------
    print("Updating headers...")
    sec1 = doc.sections[1]
    for p in sec1.header.paragraphs:
        if "ANÁLISIS DE SISTEMAS" in p.text:
            p.text = p.text.replace("ANÁLISIS DE SISTEMAS", "ANALISTA EN SISTEMAS")
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                r.font.name = "Calibri"
                r.font.size = Pt(12)
                r.font.color.rgb = RGBColor(0, 0, 0)
                
    # -------------------------------------------------------------------------
    # 2. Update Carátula: Add project logo in middle area
    # -------------------------------------------------------------------------
    print("Checking carátula...")
    for i, p in enumerate(doc.paragraphs[:15]):
        if "Gestor de Calorías Regional" in p.text and i < 10:
            has_logo = False
            for j in range(i, min(i+4, len(doc.paragraphs))):
                if "graphicData" in doc.paragraphs[j]._element.xml:
                    has_logo = True
                    break
            if not has_logo and os.path.exists(project_logo_path):
                print("Adding project logo to carátula...")
                target_caratula = doc.paragraphs[i+1]
                p_logo = target_caratula.insert_paragraph_before()
                p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_logo.paragraph_format.space_before = Pt(4)
                p_logo.paragraph_format.space_after = Pt(4)
                p_logo.paragraph_format.first_line_indent = 0
                r_logo = p_logo.add_run()
                r_logo.add_picture(project_logo_path, width=Inches(1.5))
            break

    # Clean up empty spacer paragraphs in carátula to ensure it fits on Page 1
    alumno_idx = None
    for i, p in enumerate(doc.paragraphs[:16]):
        if "Alumno:" in p.text:
            alumno_idx = i
            break
    if alumno_idx is not None:
        to_remove = []
        for j in range(alumno_idx + 1, alumno_idx + 6):
            if doc.paragraphs[j].text.strip() == "":
                to_remove.append(j)
        for idx in reversed(to_remove):
            p_el = doc.paragraphs[idx]._element
            p_el.getparent().remove(p_el)

    # -------------------------------------------------------------------------
    # 3. Update Table of Contents (Índice)
    # -------------------------------------------------------------------------
    print("Updating Table of Contents (Índice)...")
    idx_header_p = None
    next_section_p = None
    
    for i, p in enumerate(doc.paragraphs):
        if p.text.strip() == "Índice" and i < 30:
            idx_header_p = p
        elif idx_header_p is not None and p.text.strip() == "3. Título" and i < 70:
            if i + 1 < len(doc.paragraphs) and doc.paragraphs[i+1].text.strip() == "Gestor de Calorías Regional":
                next_section_p = p
                break
            
    if idx_header_p is None or next_section_p is None:
        raise ValueError("Could not locate Índice header or 3. Título paragraph")
        
    # The paragraphs between idx_header_p and next_section_p are the old TOC items (and page break)
    # We want to remove all paragraphs strictly between idx_header_p and next_section_p except if one is a page break,
    # or better: remove all of them, insert new items, and insert a page break before next_section_p!
    p_curr = idx_header_p._element.getnext()
    while p_curr is not None and p_curr != next_section_p._element:
        p_next = p_curr.getnext()
        p_curr.getparent().remove(p_curr)
        p_curr = p_next
        
    # Now next_section_p is right after idx_header_p.
    # We insert our TOC items before next_section_p, and then a page break before next_section_p.
    target_toc_p = next_section_p
    
    toc_items = [
        ("1. Carátula", 1, True, 0),
        ("2. Índice", 2, True, 0),
        ("3. Título", 3, True, 0),
        ("4. Resumen del Sistema", 3, True, 0),
        ("5. Análisis", 4, True, 0),
        ("   5.1. Introducción", 4, False, 1),
        ("   5.2. Descripción General", 4, False, 1),
        ("   5.3. Justificación", 6, False, 1),
        ("   5.4. Objetivos Generales", 6, False, 1),
        ("   5.5. Objetivos Específicos", 6, False, 1),
        ("   5.6. Límites del Sistema", 8, False, 1),
        ("   5.7. Requerimientos del Sistema. Casos de Uso", 9, False, 1),
        ("   5.8. Estudio de Factibilidad", 22, False, 1),
        ("   5.9. Cronograma (Diagrama Gantt)", 24, False, 1),
        ("   5.10. Presupuesto", 25, False, 1),
        ("6. Diseño", 26, True, 0),
        ("   6.1. Reglas de Negocio", 26, False, 1),
        ("   6.2. Herramientas de Modelado de Datos Seleccionado (DFD)", 28, False, 1),
        ("   6.3. Base de datos (con diccionario y mapa canónico)", 31, False, 1),
        ("   6.4. Frontend / Prototipo", 38, False, 1),
        ("7. Conclusión sobre el Proyecto", 41, True, 0),
        ("8. Bibliografía", 42, True, 0),
        ("9. Glosario de Palabras Técnicas", 43, True, 0)
    ]
    
    for title, default_page, is_main, indent_level in toc_items:
        clean_key = title.strip()
        num_prefix = clean_key.split()[0]
        page_val = default_page
        if toc_page_dict:
            if num_prefix in toc_page_dict:
                page_val = toc_page_dict[num_prefix]
            elif clean_key in toc_page_dict:
                page_val = toc_page_dict[clean_key]
        
        p_item = target_toc_p.insert_paragraph_before()
        p_item.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_item.paragraph_format.space_before = Pt(1)
        p_item.paragraph_format.space_after = Pt(2)
        p_item.paragraph_format.first_line_indent = 0
        
        pPr = p_item._p.get_or_add_pPr()
        tabs = parse_xml(
            f'<w:tabs {nsdecls("w")}>'
            f'<w:tab w:val="right" w:leader="dot" w:pos="9950"/>'
            f'</w:tabs>'
        )
        pPr.append(tabs)
        
        r_title = p_item.add_run(title)
        r_title.font.name = "Calibri"
        r_title.font.size = Pt(11)
        r_title.bold = is_main
        r_title.font.color.rgb = RGBColor(0, 0, 0)
        
        r_tab = p_item.add_run("\t")
        r_tab.font.name = "Calibri"
        r_tab.font.size = Pt(11)
        
        r_page = p_item.add_run(str(page_val))
        r_page.font.name = "Calibri"
        r_page.font.size = Pt(11)
        r_page.bold = is_main
        r_page.font.color.rgb = RGBColor(0, 0, 0)

    # Page break after TOC so 3. Título begins on Page 3
    p_toc_pb = target_toc_p.insert_paragraph_before()
    p_toc_pb.paragraph_format.space_before = Pt(0)
    p_toc_pb.paragraph_format.space_after = Pt(0)
    p_toc_pb.paragraph_format.first_line_indent = 0
    r_toc_pb = p_toc_pb.add_run()
    r_toc_pb.add_break(docx.enum.text.WD_BREAK.PAGE)

    # -------------------------------------------------------------------------
    # 4. Locate insertion point for Chapter 6 (before Chapter 7)
    # -------------------------------------------------------------------------
    print("Locating insertion point for Chapter 6...")
    target_idx = None
    for i, p in enumerate(doc.paragraphs):
        # We need the real chapter 7 (i > 100)
        if i > 100 and p.text.strip().startswith("7. Conclusión sobre el Proyecto"):
            target_idx = i
            break
            
    if target_idx is None:
        raise ValueError("Could not find paragraph '7. Conclusión sobre el Proyecto'")
        
    # The paragraph right before Chapter 7 is paragraph target_idx - 1 (the page break)
    target_p = doc.paragraphs[target_idx - 1]
    
    # -------------------------------------------------------------------------
    # 5. Insert Chapter 6: DISEÑO
    # -------------------------------------------------------------------------
    print("Inserting Chapter 6: DISEÑO...")
    
    # Page break before Chapter 6
    p_pb = target_p.insert_paragraph_before()
    p_pb.paragraph_format.space_before = Pt(0)
    p_pb.paragraph_format.space_after = Pt(0)
    p_pb.paragraph_format.first_line_indent = 0
    r_pb = p_pb.add_run()
    r_pb.add_break(docx.enum.text.WD_BREAK.PAGE)
    
    # Title 6
    add_heading_1(target_p, "6. Diseño")
    add_p(target_p, 
          "El presente capítulo aborda el diseño integral del sistema «Gestor de Calorías Regional», "
          "estableciendo el puente formal entre los requerimientos relevados en la fase de análisis y su "
          "materialización técnica y operativa. En esta etapa se definen con rigor matemático y normativo las "
          "reglas de negocio que gobiernan la lógica del sistema, se modela la dinámica de transformación y "
          "flujo de información a través de Diagramas de Flujo de Datos (DFD), se formaliza el diseño "
          "relacional de la base de datos local SQLite —incorporando el modelo Entidad-Relación, el diccionario "
          "de datos exhaustivo, el mapa canónico de normalización, la tabla de trazabilidad funcional y el acceso "
          "al repositorio institucional—, y finalmente se documenta la arquitectura de interfaz de usuario del "
          "prototipo móvil desarrollado en el framework Flet.")
    
    # 6.1. Reglas de Negocio
    add_heading_2(target_p, "6.1. Reglas de Negocio")
    add_p(target_p, 
          "Las reglas de negocio constituyen los principios rectores, fórmulas biométricas y restricciones lógicas "
          "que determinan el comportamiento algorítmico del software. En el marco del control nutricional con enfoque "
          "regional, estas reglas garantizan la exactitud en la cuantificación calórica y la consistencia en el "
          "seguimiento antropométrico del usuario:")
    
    add_p(target_p, "RN-01: Cálculo de la Tasa Metabólica Basal (TMB) y Gasto Energético Total Diario (TDEE)", bold=True, size_pt=12, first_line_indent=0)
    add_p(target_p, 
          "Para la estimación del gasto calórico basal se implementa la ecuación de Mifflin-St Jeor, reconocida por "
          "la literatura científica contemporánea como la fórmula de mayor precisión en población adulta. La fórmula "
          "discrimina por sexo biológico según los parámetros:")
    add_bullet(target_p, "Hombres:", "TMB = (10 × peso_kg) + (6.25 × altura_cm) - (5 × edad_años) + 5")
    add_bullet(target_p, "Mujeres:", "TMB = (10 × peso_kg) + (6.25 × altura_cm) - (5 × edad_años) - 161")
    add_p(target_p, 
          "Posteriormente, el Gasto Energético Total Diario (TDEE) se obtiene multiplicando la TMB por el coeficiente de "
          "actividad física seleccionado por el usuario: Sedentario (1.20), Actividad Ligera (1.375), Actividad Moderada "
          "(1.55) o Actividad Muy Intensa (1.725). La meta calórica diaria se calcula ajustando el TDEE en función del "
          "objetivo nutricional: Déficit Calórico (-500 kcal/día, con piso de seguridad de 1200 kcal para mujeres y 1500 kcal "
          "para hombres), Mantenimiento (TDEE sin variación) y Superávit Calórico (+350 a +500 kcal/día).")

    add_p(target_p, "RN-02: Distribución y Cuantificación de Macronutrientes", bold=True, size_pt=12, first_line_indent=0)
    add_p(target_p, 
          "El balance energético se desglosa en los tres macronutrientes esenciales aplicando las constantes de densidad "
          "fisiológica estándar de Atwater: Proteínas = 4 kcal/g, Carbohidratos = 4 kcal/g y Grasas = 9 kcal/g. La meta de "
          "hidratación diaria se fija en una tasa de 35 ml de agua por cada kilogramo de peso corporal del usuario.")

    add_p(target_p, "RN-03: Cálculo Proporcional de Ingestas e Inmutabilidad de Referencia", bold=True, size_pt=12, first_line_indent=0)
    add_p(target_p, 
          "Todo alimento cargado en la base de datos maestra o generado como receta propia define sus valores nutricionales "
          "normalizados a una base de referencia de 100 gramos o 100 mililitros. El aporte nutricional efectivo de una ingesta "
          "se computa mediante regla de tres lineal directa en función del gramaje o porción ingresada por el usuario:")
    add_bullet(target_p, "Calorías consumidas =", "(cantidad_g_ml × calorias_100g) / 100")
    add_bullet(target_p, "Macronutriente consumido (P/C/G) =", "(cantidad_g_ml × macro_100g) / 100")
    add_p(target_p, 
          "A fin de garantizar la integridad histórica y cumplir con el principio de inmutabilidad de la auditoría nutricional, "
          "los valores calculados de calorías y macronutrientes se persisten de forma fija en la tupla de REGISTRO_DIARIO al "
          "momento de la carga, previniendo alteraciones involuntarias sobre el historial si el alimento base es editado a futuro.")

    add_p(target_p, "RN-04: Factor de Merma y Variación de Peso por Cocción en Recetas", bold=True, size_pt=12, first_line_indent=0)
    add_p(target_p, 
          "En la elaboración de recetas autóctonas compuestas por múltiples ingredientes crudos (como la sopa paraguaya, chipa "
          "o preparaciones cárnicas), el proceso de cocción genera pérdida de agua por evaporación o merma de volumen. El "
          "sistema permite computar el peso neto total cocido de la preparación y distribuir equitativamente el valor calórico y "
          "nutricional total acumulado entre el número de porciones finales declaradas.")

    add_p(target_p, "RN-05: Alerta Semántica por Desvío o Exceso Calórico", bold=True, size_pt=12, first_line_indent=0)
    add_p(target_p, 
          "El sistema evalúa continuamente la sumatoria de calorías consumidas en la jornada respecto a la meta configurada en "
          "el perfil activo. Al alcanzarse o superarse el 100% de la cuota diaria establecida, el componente visual del "
          "Dashboard transiciona automáticamente al color semántico de advertencia (rojo de alerta) y despliega una notificación "
          "contextual para informar al usuario sobre el exceso generado.")

    add_p(target_p, "RN-06: Persistencia y Autonomía de Operación Offline", bold=True, size_pt=12, first_line_indent=0)
    add_p(target_p, 
          "Todas las transacciones de lectura, inserción, actualización y borrado (CRUD) operan de manera autónoma y 100% offline "
          "sobre el motor local SQLite. La aplicación no exige conectividad a internet, ni sincronización con APIs externas, ni "
          "dependencias de servidores remotos, asegurando privacidad total de la información biométrica y portabilidad absoluta.")

    add_p(target_p, "RN-07: Integridad de Datos y Restricciones de Validación", bold=True, size_pt=12, first_line_indent=0)
    add_p(target_p, 
          "Los formularios de captura validan obligatoriamente la congruencia biológica de las entradas: peso corporal mayor a cero, "
          "altura estrictamente positiva, edad entre rangos reales y gramajes de consumo superiores a cero. Los alimentos "
          "precargados en el catálogo maestro regional se protegen contra corrupción lógica, admitiendo únicamente extensiones y "
          "recetas creadas voluntariamente por el usuario.")

    # 6.2. Herramientas de Modelado de Datos Seleccionado (DFD)
    add_heading_2(target_p, "6.2. Herramientas de Modelado de Datos Seleccionado (DFD)")
    add_p(target_p, 
          "Para modelar la perspectiva funcional y el flujo de información del sistema «Gestor de Calorías Regional» se adoptó "
          "la metodología estructurada clásica mediante Diagramas de Flujo de Datos (DFD) bajo la notación de Yourdon / DeMarco. "
          "Esta herramienta permite representar con total claridad cómo los datos ingresados por el usuario son transformados a "
          "través de los distintos procesos del sistema y almacenados en los repositorios persistentes correspondientes.")
    add_p(target_p, 
          "El modelado se desglosa en dos niveles de abstracción complementarios: el Diagrama de Contexto (Nivel 0), que define la "
          "frontera del sistema y su relación con el entorno exterior, y el Diagrama de Descomposición Funcional (Nivel 1), que "
          "detalla los procesos lógicos internos y sus interacciones con los almacenes de datos.")

    add_heading_3(target_p, "6.2.1. Diagrama de Contexto (DFD Nivel 0)")
    add_p(target_p, 
          "En el Nivel 0 se concibe al sistema completo como una única caja de procesamiento central rotulada «0. Gestor de "
          "Calorías Regional». Dicho proceso interactúa de forma exclusiva con una única entidad externa: el «Usuario». A "
          "continuación se presenta la matriz de flujos del diagrama de contexto:")

    dfd0_headers = ["Tipo de Flujo", "Nombre del Flujo de Datos", "Origen", "Destino", "Descripción Funcional"]
    dfd0_rows = [
        ["Entrada", "Datos biométricos y metas", "Usuario", "Proceso 0", "Edad, sexo, peso, altura, actividad y objetivo calórico."],
        ["Entrada", "Búsqueda de alimentos", "Usuario", "Proceso 0", "Término de consulta de alimentos estándar o regionales."],
        ["Entrada", "Registro de ingesta diaria", "Usuario", "Proceso 0", "Alimento seleccionado, fecha, momento y cantidad en gramos."],
        ["Entrada", "Datos de recetas caseras", "Usuario", "Proceso 0", "Nombre de receta, ingredientes, cantidades y porciones."],
        ["Entrada", "Registro de agua y peso", "Usuario", "Proceso 0", "Tomas de hidratación en ml y peso corporal de control en kg."],
        ["Salida", "Resumen nutricional diario", "Proceso 0", "Usuario", "Calorías y macronutrientes acumulados vs metas en Dashboard."],
        ["Salida", "Resultados de búsqueda", "Proceso 0", "Usuario", "Listado de alimentos coincidentes con valores nutricionales."],
        ["Salida", "Alertas de límite calórico", "Proceso 0", "Usuario", "Notificaciones visuales cuando la ingesta supera la meta."],
        ["Salida", "Histórico y gráficos", "Proceso 0", "Usuario", "Evolución gráfica de pesajes y balance hídrico semanal."]
    ]
    add_custom_table(target_p, doc, dfd0_headers, dfd0_rows, [1.0, 1.6, 0.9, 0.9, 2.2])

    add_heading_3(target_p, "6.2.2. Diagrama de Flujo de Datos del Sistema (DFD Nivel 1)")
    add_p(target_p, 
          "El Diagrama de Nivel 1 descompone el proceso general en cinco subsistemas funcionales perfectamente delimitados, "
          "evidenciando el flujo de información hacia los cinco almacenes de datos relacionales del sistema:")
    add_bullet(target_p, "Proceso 1.0 (Gestionar Perfiles y Metas Biométricas):", "Captura datos personales, calcula la TMB y el TDEE mediante las reglas de negocio y persiste el perfil en el almacén D1 (USUARIO).")
    add_bullet(target_p, "Proceso 2.0 (Administrar Catálogo y Recetas Regionales):", "Permite buscar alimentos locales, dar de alta ingredientes personalizados y armar recetas compuestas persistidas en el almacén D2 (ALIMENTO).")
    add_bullet(target_p, "Proceso 3.0 (Registrar Consumos y Calcular Nutrientes):", "Recibe la comida ingerida, consulta la información nutricional de D2, computa los aportes proporcionales y almacena el registro fijo en D3 (REGISTRO_DIARIO).")
    add_bullet(target_p, "Proceso 4.0 (Controlar Hidratación y Evolución de Peso):", "Registra las tomas de agua en D4 (REGISTRO_AGUA) y los pesajes de control corporal en D5 (REGISTRO_PESO).")
    add_bullet(target_p, "Proceso 5.0 (Generar Dashboard, Métricas y Alertas):", "Consolida las lecturas de los cinco almacenes para generar los indicadores gráficos del Dashboard, el desglose de macronutrientes y las alertas de desvío calórico.")

    if os.path.exists(dfd_img_path):
        add_image_box(target_p, doc, dfd_img_path, 6.2, 
                      "Figura 2. Diagrama de Flujo de Datos (DFD) Nivel 1 del Gestor de Calorías Regional (Yourdon / DeMarco).")

    add_heading_3(target_p, "6.2.3. Diccionario de Almacenes de Datos del DFD")
    add_p(target_p, 
          "A continuación se documentan los almacenes de datos definidos en el modelado DFD, los cuales corresponden "
          "directamente a las tablas de la base de datos relacional SQLite:")

    store_headers = ["ID", "Nombre del Almacén", "Soporte Físico", "Entidad Relacional", "Descripción del Contenido"]
    store_rows = [
        ["D1", "USUARIO", "SQLite (calorias.db)", "Tabla USUARIO", "Perfiles de usuarios locales, datos biométricos y metas calóricas diarias."],
        ["D2", "ALIMENTO", "SQLite (calorias.db)", "Tabla ALIMENTO", "Catálogo maestro regional, alimentos convencionales y recetas del usuario."],
        ["D3", "REGISTRO_DIARIO", "SQLite (calorias.db)", "Tabla REGISTRO_DIARIO", "Historial de ingestas diarias con valores nutricionales calculados y congelados."],
        ["D4", "REGISTRO_AGUA", "SQLite (calorias.db)", "Tabla REGISTRO_AGUA", "Seguimiento diario de hidratación y volumen consumido en mililitros."],
        ["D5", "REGISTRO_PESO", "SQLite (calorias.db)", "Tabla REGISTRO_PESO", "Historial cronológico de pesajes corporales para análisis de tendencia."]
    ]
    add_custom_table(target_p, doc, store_headers, store_rows, [0.6, 1.5, 1.3, 1.4, 2.2])

    # 6.3. Base de Datos (con diccionario y mapa canónico)
    add_heading_2(target_p, "6.3. Base de Datos (con diccionario y mapa canónico)")
    add_p(target_p, 
          "La capa de persistencia constituye el núcleo estructural del software. El sistema utiliza el motor de base de datos "
          "relacional SQLite, garantizando portabilidad multiplataforma, cero latencia de red y resguardo seguro y privado de "
          "los datos en el dispositivo. A continuación se presentan el Diagrama Entidad-Relación (DER), el Diccionario de Datos, "
          "el Mapa Canónico de Normalización, la Tabla de Trazabilidad de Requerimientos Funcionales y el enlace al repositorio oficial.")

    add_heading_3(target_p, "6.3.1. Diagrama Entidad-Relación (DER) del Proyecto")
    add_p(target_p, 
          "El modelo conceptual de la base de datos organiza la información en cinco entidades principales conectadas mediante "
          "relaciones de cardinalidad uno a muchos (1:N), optimizadas para consultas ágiles en tiempo de ejecución:")

    if os.path.exists(er_img_path):
        add_image_box(target_p, doc, er_img_path, 5.8, 
                      "Figura 3. Diagrama Entidad-Relación (DER) de la base de datos del proyecto.")

    add_p(target_p, "Descripción de Entidades y Atributos Principales:", bold=True, size_pt=12, first_line_indent=0)
    add_bullet(target_p, "1. USUARIO:", "Almacena la identidad de la persona que se registra en la aplicación, sus datos físicos personales (nombre, género, edad, peso, altura), su objetivo nutricional (déficit, superávit o mantenimiento) y sus metas diarias de calorías, proteínas, carbohidratos, grasas y agua.")
    add_bullet(target_p, "2. ALIMENTO:", "Catálogo central donde residen las comidas. Contiene alimentos convencionales estandarizados, platos autóctonos regionales (mandioca, sopa paraguaya, chipa, reviro, mbaipy, etc.) y las recetas personalizadas creadas por el usuario, con su aporte nutricional normalizado por cada 100 gramos.")
    add_bullet(target_p, "3. REGISTRO_DIARIO:", "Historial operativo de ingestas. Relaciona a un usuario con un alimento o receta en una fecha particular, indicando el tipo de comida (Desayuno, Almuerzo, Cena, Snack), la cantidad en gramos o porciones y el cálculo resultante de calorías y macronutrientes.")
    add_bullet(target_p, "4. REGISTRO_AGUA:", "Control de hidratación diaria que acumula las tomas de agua en mililitros efectuadas por el usuario en cada jornada.")
    add_bullet(target_p, "5. REGISTRO_PESO:", "Historial cronológico de control antropométrico donde se registran los pesajes del usuario para proyectar gráficos de evolución corporal.")

    add_p(target_p, "Relaciones y Cardinalidades de la Base de Datos:", bold=True, size_pt=12, first_line_indent=0)
    add_bullet(target_p, "USUARIO (1) ── (N) REGISTRO_DIARIO:", "Un usuario carga múltiples registros de comida en distintas fechas; cada registro diario pertenece indefectiblemente a un único usuario (FK id_usuario).")
    add_bullet(target_p, "USUARIO (1) ── (N) REGISTRO_AGUA:", "Un usuario registra múltiples tomas de agua a lo largo del tiempo; cada toma corresponde a un solo usuario (FK id_usuario).")
    add_bullet(target_p, "USUARIO (1) ── (N) REGISTRO_PESO:", "Un usuario se pesa periódicamente generando un histórico de registros corporales vinculados a su perfil (FK id_usuario).")
    add_bullet(target_p, "ALIMENTO (1) ── (N) REGISTRO_DIARIO:", "Un alimento del catálogo o receta propia puede figurar en innumerables registros diarios a lo largo del tiempo (FK id_alimento).")

    add_heading_3(target_p, "6.3.2. Diccionario de Datos Completo")
    add_p(target_p, 
          "El diccionario de datos define la estructura física, tipos primitivos en SQLite, longitudes de referencia, "
          "claves primarias (PK), claves foráneas (FK), restricciones de nulidad y el significado funcional de cada campo:")

    add_p(target_p, "Tabla 11. Diccionario de Datos — Entidad USUARIO", bold=True, size_pt=11, first_line_indent=0)
    user_headers = ["Campo", "Tipo SQLite", "Clave", "Nulo", "Descripción Funcional"]
    user_rows = [
        ["id_usuario", "INTEGER", "PK", "NO", "Identificador unívoco autoincremental del usuario."],
        ["nombre", "TEXT", "—", "NO", "Nombre completo o alias del perfil de usuario."],
        ["genero", "TEXT", "—", "NO", "Sexo biológico ('M' o 'F') para la fórmula Mifflin-St Jeor."],
        ["edad", "INTEGER", "—", "NO", "Edad del usuario en años cumplidos."],
        ["peso", "REAL", "—", "NO", "Peso corporal actual en kilogramos (ej. 75.5)."],
        ["altura", "REAL", "—", "NO", "Estatura en centímetros (ej. 175.0)."],
        ["objetivo", "TEXT", "—", "NO", "Meta física ('deficit', 'mantenimiento', 'superavit')."],
        ["meta_calorias", "INTEGER", "—", "NO", "Límite calórico objetivo diario sugerido o personalizado."],
        ["meta_proteinas", "REAL", "—", "NO", "Meta diaria de proteínas en gramos."],
        ["meta_carbos", "REAL", "—", "NO", "Meta diaria de carbohidratos en gramos."],
        ["meta_grasas", "REAL", "—", "NO", "Meta diaria de lípidos en gramos."],
        ["meta_agua_ml", "INTEGER", "—", "NO", "Objetivo hídrico diario en mililitros (ej. 2500)."]
    ]
    add_custom_table(target_p, doc, user_headers, user_rows, [1.3, 1.0, 0.7, 0.7, 2.9])

    add_p(target_p, "Tabla 12. Diccionario de Datos — Entidad ALIMENTO", bold=True, size_pt=11, first_line_indent=0)
    food_headers = ["Campo", "Tipo SQLite", "Clave", "Nulo", "Descripción Funcional"]
    food_rows = [
        ["id_alimento", "INTEGER", "PK", "NO", "Identificador unívoco autoincremental del alimento o receta."],
        ["nombre", "TEXT", "—", "NO", "Denominación del alimento (ej. 'Mandioca hervida', 'Chipa')."],
        ["calorias_100g", "REAL", "—", "NO", "Contenido calórico por cada 100 gramos de porción comestible."],
        ["proteinas_100g", "REAL", "—", "NO", "Gramos de proteína aportados por cada 100 gramos."],
        ["carbos_100g", "REAL", "—", "NO", "Gramos de hidratos de carbono por cada 100 gramos."],
        ["grasas_100g", "REAL", "—", "NO", "Gramos de lípidos totales por cada 100 gramos."],
        ["es_regional", "INTEGER", "—", "NO", "Bandera booleana (1 = autóctono argentino/regional, 0 = general)."],
        ["es_receta", "INTEGER", "—", "NO", "Bandera booleana (1 = receta elaborada por usuario, 0 = ingrediente)."],
        ["es_favorito", "INTEGER", "—", "NO", "Bandera booleana (1 = alimento marcado en favoritos, 0 = no marcado)."]
    ]
    add_custom_table(target_p, doc, food_headers, food_rows, [1.3, 1.0, 0.7, 0.7, 2.9])

    add_p(target_p, "Tabla 13. Diccionario de Datos — Entidad REGISTRO_DIARIO", bold=True, size_pt=11, first_line_indent=0)
    diary_headers = ["Campo", "Tipo SQLite", "Clave", "Nulo", "Descripción Funcional"]
    diary_rows = [
        ["id_registro", "INTEGER", "PK", "NO", "Identificador unívoco de la ingesta consumida."],
        ["id_usuario", "INTEGER", "FK", "NO", "Referencia al usuario consumidor (FK -> USUARIO.id_usuario)."],
        ["id_alimento", "INTEGER", "FK", "NO", "Referencia al alimento ingerido (FK -> ALIMENTO.id_alimento)."],
        ["fecha", "TEXT", "—", "NO", "Fecha de consumo en formato estándar ISO 'YYYY-MM-DD'."],
        ["tipo_comida", "TEXT", "—", "NO", "Momento del consumo ('Desayuno', 'Almuerzo', 'Cena', 'Snack')."],
        ["cantidad_g_ml", "REAL", "—", "NO", "Cantidad neta ingerida en gramos o mililitros."],
        ["calorias", "REAL", "—", "NO", "Aporte calórico efectivo computado para la cantidad ingerida."],
        ["proteinas", "REAL", "—", "NO", "Gramos netos de proteína calculados para la ingesta."],
        ["carbos", "REAL", "—", "NO", "Gramos netos de carbohidratos calculados para la ingesta."],
        ["grasas", "REAL", "—", "NO", "Gramos netos de lípidos calculados para la ingesta."]
    ]
    add_custom_table(target_p, doc, diary_headers, diary_rows, [1.3, 1.0, 0.7, 0.7, 2.9])

    add_p(target_p, "Tabla 14. Diccionario de Datos — Entidades REGISTRO_AGUA y REGISTRO_PESO", bold=True, size_pt=11, first_line_indent=0)
    misc_headers = ["Campo", "Tipo SQLite", "Clave", "Nulo", "Entidad", "Descripción Funcional"]
    misc_rows = [
        ["id_agua", "INTEGER", "PK", "NO", "REGISTRO_AGUA", "Identificador autoincremental de la toma de agua."],
        ["id_usuario", "INTEGER", "FK", "NO", "REGISTRO_AGUA", "Usuario que registró la ingesta hídrica."],
        ["fecha", "TEXT", "—", "NO", "REGISTRO_AGUA", "Fecha de la toma en formato 'YYYY-MM-DD'."],
        ["cantidad_ml", "INTEGER", "—", "NO", "REGISTRO_AGUA", "Volumen consumido en mililitros (ej. 250 ml por vaso)."],
        ["id_peso", "INTEGER", "PK", "NO", "REGISTRO_PESO", "Identificador autoincremental del registro de pesaje."],
        ["id_usuario", "INTEGER", "FK", "NO", "REGISTRO_PESO", "Usuario al que pertenece el registro de peso."],
        ["fecha", "TEXT", "—", "NO", "REGISTRO_PESO", "Fecha del pesaje en formato 'YYYY-MM-DD'."],
        ["peso_registrado", "REAL", "—", "NO", "REGISTRO_PESO", "Masa corporal registrada en kilogramos (ej. 76.2)."]
    ]
    add_custom_table(target_p, doc, misc_headers, misc_rows, [1.2, 0.9, 0.6, 0.6, 1.3, 2.0])

    add_heading_3(target_p, "6.3.3. Mapa Canónico y Proceso de Normalización")
    add_p(target_p, 
          "El diseño relacional fue sometido a las reglas de normalización de Edgar F. Codd, garantizando la eliminación de "
          "redundancias indeseadas, la preservación de dependencias funcionales y la integridad referencial:")
    add_bullet(target_p, "Primera Forma Normal (1FN):", "Todos los atributos son atómicos e indivisibles; no existen grupos repetitivos ni atributos multivaluados en una misma columna (las listas de ingredientes de recetas y las comidas diarias se descomponen en registros individuales). Cada tabla posee una clave primaria simple (id_usuario, id_alimento, id_registro, id_agua, id_peso).")
    add_bullet(target_p, "Segunda Forma Normal (2FN):", "El esquema se encuentra en 1FN y todos los atributos que no forman parte de la clave primaria dependen de forma completa y directa de la totalidad de la clave primaria, eliminando dependencias parciales al no emplearse claves compuestas redundantes.")
    add_bullet(target_p, "Tercera Forma Normal (3FN) y Decisión de Ingeniería:", "El esquema satisface 2FN y no existen dependencias transitivas entre atributos no clave (ningún atributo no clave depende funcionalmente de otro atributo no clave). Se destaca la decisión arquitectónica fundamentada de desnormalización controlada en REGISTRO_DIARIO: si bien las calorías y macros podrían derivarse dinámicamente de ALIMENTO, se almacenan precalculadas en la tupla de consumo para garantizar el principio de inmutabilidad histórica y trazabilidad contable nutricional, previniendo alteraciones involuntarias en el pasado si el catálogo base sufre ajustes posteriores.")

    add_heading_3(target_p, "6.3.4. Tabla de Trazabilidad y Estado de Avance")
    add_p(target_p, 
          "A continuación se presenta la tabla de trazabilidad que vincula la totalidad de los catorce requerimientos funcionales "
          "definidos en el punto 5.7 con los componentes de software, módulos y métodos implementados en la arquitectura del proyecto, "
          "consignando el estado real de avance a la fecha:")

    trace_headers = ["Req.", "Descripción Funcional (5.7)", "Archivo / Módulo", "Función / Pantalla", "Estado", "Observación Técnica"]
    trace_rows = [
        ["R1", "El usuario debe poder crear y seleccionar un perfil local.", "ui/profile.py\nui/setup.py\ndatabase.py", "get_profile_view()\non_profile_change()\nsave_profile()", "Implementado", "—"],
        ["R2", "El usuario debe poder configurar su perfil biométrico y metas.", "ui/profile.py\nui/setup.py\ndatabase.py", "auto_recalculate()\nupdate_profile()\nsave_profile()", "Implementado", "—"],
        ["R3", "El usuario debe poder buscar alimentos regionales en el sistema.", "ui/diary.py\ndatabase.py", "search_foods()\nopen_food_picker()", "Implementado", "—"],
        ["R4", "El usuario debe poder registrar los alimentos consumidos en el día.", "ui/diary.py\ndatabase.py", "add_diary_entry()\nopen_add_dialog()", "Implementado", "—"],
        ["R5", "El sistema debe calcular automáticamente las calorías consumidas.", "ui/dashboard.py\nui/diary.py", "get_dashboard_view()\nopen_add_dialog()", "Implementado", "—"],
        ["R6", "El sistema debe calcular el desglose de macronutrientes.", "ui/dashboard.py\nui/diary.py", "macro_card()\nget_dashboard_view()", "Implementado", "—"],
        ["R7", "El usuario debe poder ingresar el gramaje exacto o en medidas caseras.", "ui/diary.py", "open_add_dialog()\nunit selector", "Implementado", "—"],
        ["R8", "El usuario debe poder crear y guardar recetas propias.", "ui/recipes.py\ndatabase.py", "save_recipe_dialog()\nsave_recipe()", "Implementado", "—"],
        ["R9", "El usuario debe poder marcar alimentos frecuentes como 'Favoritos'.", "database.py\nui/diary.py", "toggle_favorite()\nsearch_foods()", "Implementado", "—"],
        ["R10", "El usuario debe poder editar o eliminar registros de alimentos del diario.", "ui/diary.py\ndatabase.py", "edit_entry()\ndelete_diary_entry()", "Implementado", "—"],
        ["R11", "El sistema debe calcular la variación de peso de los alimentos por cocción.", "ui/recipes.py", "create_recipe_view()\ncalculate_macros()", "Parcial", "Aplica factor de merma y porciones en la receta total, pero aún no discrimina coeficientes específicos por tipo de ingrediente."],
        ["R12", "El usuario debe poder ver un historial gráfico con su progreso de peso.", "ui/profile.py\ndatabase.py", "get_weight_logs()\nft.LineChart", "Implementado", "—"],
        ["R13", "El usuario debe poder registrar su consumo diario de agua.", "ui/dashboard.py\nui/history.py\ndatabase.py", "add_water()\nget_water_today()\nwater_card", "Implementado", "—"],
        ["R14", "El sistema debe mostrar alertas visuales cuando el usuario supere su límite.", "ui/dashboard.py\nui/history.py", "get_dashboard_view()\ntheme.DANGER trigger", "Implementado", "—"]
    ]
    add_custom_table(target_p, doc, trace_headers, trace_rows, [0.5, 1.8, 1.1, 1.1, 0.9, 1.2])

    add_heading_3(target_p, "6.3.5. Enlace al Repositorio del Proyecto")
    add_p(target_p, 
          "El código fuente íntegro de la aplicación, el script de inicialización de la base de datos SQLite con el catálogo "
          "maestro regional precargado y la suite de módulos de interfaz gráfica se encuentran disponibles públicamente en el "
          "repositorio institucional del desarrollador:")
    add_repo_box(target_p, doc, "https://github.com/Joacogzz/Gestor_Calorias_Regional")

    # 6.4. Frontend / Prototipo (Móvil Flet)
    add_heading_2(target_p, "6.4. Frontend / Prototipo (Móvil Flet)")
    add_p(target_p, 
          "La interfaz de usuario del sistema «Gestor de Calorías Regional» fue concebida bajo una rigurosa filosofía de diseño "
          "Mobile-First, orientada a proporcionar una experiencia de interacción ergonómica, ágil y visualmente atractiva en pantallas "
          "táctiles de smartphones. Se implementó utilizando el framework Flet (arquitectura reactiva basada en el motor de Flutter "
          "para Python), lo que permite compilar y ejecutar una aplicación nativa multiplataforma con transiciones fluidas de 60 cuadros "
          "por segundo a partir de una única base de código fuente mantenible.")

    add_heading_3(target_p, "6.4.1. Arquitectura Visual y Principios de Diseño UI/UX")
    add_p(target_p, 
          "El sistema visual respeta los lineamientos de Material Design 3 combinados con la sobriedad y refinamiento ergonómico de iOS, "
          "fijando un lienzo base de vista móvil de 390 × 844 píxeles (formato estándar de smartphones contemporáneos):")
    add_bullet(target_p, "Geometría y Jerarquía de Superficies:", "Uso extensivo de tarjetas elevadas (`Card`) con bordes redondeados (radios de curvatura de 12 a 20 px), fondos oscuros en capas semánticas (superficie base `#121212`, tarjetas `#1E1E1E`) y micro-espaciados consistentes que eliminan la fatiga cognitiva del usuario.")
    add_bullet(target_p, "Tipografía y Legibilidad Dinámica:", "Tipografía sans-serif de alta legibilidad (Roboto / Inter) parametrizada jerárquicamente en rangos de 11 a 28 puntos para diferenciar métricas numéricas cardinales, etiquetas secundarias de macronutrientes y leyendas de apoyo.")
    add_bullet(target_p, "Paleta Cromática Semántica y Modo Oscuro:", "Implementación modularizada en `ui/theme.py` orientada a la eficiencia energética en paneles OLED y al confort visual. Se destacan acentos cromáticos unívocos: azul suave para calorías y carbohidratos, tono celeste para hidratación, coral/salmón para lípidos y violeta para proteínas, facilitando una lectura analítica instantánea.")

    add_heading_3(target_p, "6.4.2. Módulo de Inicialización y Configuración de Perfil (Wizard Inicial)")
    add_p(target_p, 
          "El flujo de inicialización (`ui/setup.py`) se activa automáticamente en el primer lanzamiento de la aplicación si el motor "
          "de base de datos detecta la ausencia de perfiles registrados. Dicho asistente guía al usuario en una experiencia libre de fricciones:")
    add_bullet(target_p, "Pantalla de Bienvenida (Figura 4):", "Presenta la identidad visual del software y sintetiza la propuesta de valor orientada a la nutrición regional inteligente, ofreciendo una puerta de entrada clara y amigable.")
    add_bullet(target_p, "Configuración de Perfil Biométrico y Metas (Figura 5):", "Formulario interactivo que releva los datos antropométricos del usuario (nombre, sexo biológico, edad, peso corporal en kg y altura en cm), el nivel de actividad física estandarizado (desde sedentario hasta ejercicio intenso) y la meta corporal deseada (déficit para pérdida de grasa, mantenimiento normocalórico o superávit para ganancia de masa muscular). Con estos datos, el sistema computa en tiempo real la Tasa Metabólica Basal (TMB) mediante la ecuación científica de Mifflin-St Jeor y establece el Gasto Energético Total Diario (TDEE).")
    
    add_two_screenshots_card(target_p, doc, 
                             img_bienvenida, "Figura 4. Asistente Inicial — Pantalla de Bienvenida del Sistema.",
                             img_perfil_setup, "Figura 5. Asistente Inicial — Configuración de Parámetros Biométricos y Metas.")

    add_heading_3(target_p, "6.4.3. Módulo Central: Dashboard Nutricional y Diario de Ingestas")
    add_p(target_p, 
          "El módulo central integra la operatoria cotidiana del usuario, garantizando un registro expedito y un monitoreo claro de su balance calórico:")
    add_bullet(target_p, "Dashboard Principal y Balance de Macronutrientes (Figura 6):", "Diseñado en `ui/dashboard.py`, exhibe un indicador circular de progreso (`ProgressRing`) que cuantifica las calorías consumidas respecto a la meta diaria asignada (ej. 1623 kcal sobre un objetivo de 3193 kcal). Acompaña tres indicadores radiales específicos para proteínas, carbohidratos y grasas con sus respectivos gramos ingeridos y metas individuales. Asimismo, incorpora la tarjeta de hidratación diaria que muestra los mililitros consumidos frente al objetivo hídrico con botones de acción rápida de ±250 ml (un vaso de agua).")
    add_bullet(target_p, "Diario de Ingestas y Búsqueda de Alimentos (Figura 7):", "Desarrollado en `ui/diary.py`, permite explorar el catálogo maestro de alimentos mediante un buscador en tiempo real con latencia menor a 100 ms. Permite visualizar aportes calóricos directos por 100 gramos (ej. Aceite de girasol, Acelga fresca), marcar ítems con estrella de favoritos e incorporarlos al consumo del día con selección de gramaje o medidas caseras.")
    
    add_two_screenshots_card(target_p, doc, 
                             img_dashboard, "Figura 6. Dashboard Principal — Indicadores Circulares de Calorías, Macronutrientes y Registro Hídrico.",
                             img_diario, "Figura 7. Diario de Ingestas — Búsqueda Rápida de Alimentos y Registro Diario.")

    add_heading_3(target_p, "6.4.4. Módulo de Gestión de Recetas Regionales y Catálogo de Alimentos")
    add_p(target_p, 
          "Este módulo materializa la principal ventaja competitiva del sistema frente a aplicaciones globales, adaptándose a los patrones culinarios del Nordeste Argentino:")
    add_bullet(target_p, "Creación de Recetas con Merma de Cocción (Figura 8):", "Implementado en `ui/recipes.py`, permite formular platos compuestos autóctonos (chipa, sopa paraguaya, mbaipy, mandioca frita, guiso de arroz) sumando múltiples ingredientes en crudo y definiendo las porciones resultantes. El algoritmo aplica el factor de variación de peso por cocción (merma o absorción hídrica), calculando con exactitud matemática el perfil nutricional consolidado y el aporte calórico neto por cada porción servida.")
    add_bullet(target_p, "Catálogo Maestro 'Mis Alimentos' (Figura 9):", "Permite inspeccionar la totalidad de alimentos regionales y genéricos incorporados en SQLite, visualizar su desglose exacto de proteínas, carbohidratos y grasas por 100 g, crear alimentos personalizados no listados en la base inicial y editar o eliminar ítems con actualización inmediata del catálogo.")
    
    add_two_screenshots_card(target_p, doc, 
                             img_recetas, "Figura 8. Módulo de Recetas — Creación y Cálculo de Preparaciones Autóctonas con Factor de Merma.",
                             img_alimentos, "Figura 9. Catálogo de Alimentos — Gestión de Ingredientes y Composición Nutricional.")

    add_heading_3(target_p, "6.4.5. Módulo de Métricas Históricas y Gestión de Perfiles")
    add_p(target_p, 
          "El seguimiento longitudinal y la versatilidad de uso del sistema se garantizan mediante las pantallas de historial y administración de usuarios:")
    add_bullet(target_p, "Historial de Progreso y Cumplimiento Semanal (Figura 10):", "Desarrollado en `ui/history.py`, resume el comportamiento calórico e hídrico de los últimos siete días a través de gráficos de barras verticales comparativas. Incluye una cronología detallada día por día que detalla las calorías totales y el consumo de macronutrientes, con botón de exportación de reportes para auditoría nutricional.")
    add_bullet(target_p, "Panel de Gestión de Perfil y Recálculo Antropométrico (Figura 11):", "Ubicado en `ui/profile.py`, permite la alternancia multiusuario dentro del mismo dispositivo. Exhibe en tarjetas destacadas las metas calóricas y de macronutrientes activas (ej. 3193 kcal, 180g P, 456g C, 72g G) y permite ajustar dinámicamente el peso actual, la altura, el nivel de actividad o el objetivo (ej. Superávit para ganar masa con ajuste adicional de +200 kcal), recalculando instantáneamente todos los valores del sistema.")
    
    add_two_screenshots_card(target_p, doc, 
                             img_historial, "Figura 10. Historial de Progreso — Registro Cronológico Semanal y Cumplimiento de Metas.",
                             img_perfil, "Figura 11. Panel de Perfil — Administración Multiusuario y Recálculo Antropométrico.")

    add_heading_3(target_p, "6.4.6. Flujo de Navegación del Usuario")
    add_p(target_p, 
          "La arquitectura de navegación principal se apoya en una barra inferior persistente de cinco destinos (`NavigationBar`) "
          "integrada en `main.py`: [Inicio, Diario, Recetas, Historial, Perfil]. Esta disposición física en la zona inferior de la pantalla "
          "respeta los principios ergonómicos de alcance del pulgar (Thumb Zone), garantizando que las tareas frecuentes de registro y "
          "consulta se ejecuten en tres toques o menos, en estricto cumplimiento con el requerimiento no funcional RNF3.")

    # -------------------------------------------------------------------------
    # 6. Save modified document
    # -------------------------------------------------------------------------
    print("Saving completed document...")
    doc.save(target_docx)
    os.makedirs(os.path.dirname(downloads_docx), exist_ok=True)
    shutil.copy2(target_docx, downloads_docx)
    print(f"Copied to: {downloads_docx}")

if __name__ == "__main__":
    complete_project_folder()

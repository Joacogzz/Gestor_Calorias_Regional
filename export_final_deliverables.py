import os
import sys
import shutil
import subprocess
from build_completed_carpeta import complete_project_folder

def run_export():
    sys.stdout.reconfigure(encoding='utf-8')
    print("=" * 60)
    print("INICIANDO PROCESO DE COMPLETADO Y EXPORTACIÓN DE CARPETA")
    print("=" * 60)
    
    # -------------------------------------------------------------------------
    # PASO 1: Generación preliminar de Carpeta final .docx
    # -------------------------------------------------------------------------
    print("\n[Paso 1/4] Generando documento Word preliminar...")
    complete_project_folder()
    
    docx_facultad = r"C:\Users\Joaquín\Documents\Facultad\Practica profesional\Gestor de calorias regional\Carpeta\Carpeta final (Gómez Axel Joaquín).docx"
    pdf_facultad = r"C:\Users\Joaquín\Documents\Facultad\Practica profesional\Gestor de calorias regional\Carpeta\Carpeta final (Gómez Axel Joaquín).pdf"
    
    docx_downloads = r"C:\Users\Joaquín\Downloads\Carpeta\Carpeta final (Gómez Axel Joaquín).docx"
    pdf_downloads = r"C:\Users\Joaquín\Downloads\Carpeta\Carpeta final (Gómez Axel Joaquín).pdf"
    
    docx_downloads_alt = r"C:\Users\Joaquín\Downloads\Carpeta final\Carpeta final (Gómez Axel Joaquín).docx"
    pdf_downloads_alt = r"C:\Users\Joaquín\Downloads\Carpeta final\Carpeta final (Gómez Axel Joaquín).pdf"
    
    docx_desktop = r"C:\Users\Joaquín\Desktop\Carpeta final (Gómez Axel Joaquín).docx"
    pdf_desktop = r"C:\Users\Joaquín\Desktop\Carpeta final (Gómez Axel Joaquín).pdf"

    # -------------------------------------------------------------------------
    # PASO 2: Consulta de paginación real mediante Word COM
    # -------------------------------------------------------------------------
    print("\n[Paso 2/4] Consultando paginación exacta mediante Microsoft Word...")
    ps_query = f'''
    $w = New-Object -ComObject Word.Application
    $w.Visible = $false
    $d = $w.Documents.Open("{docx_facultad}")
    $totalPages = $d.ComputeStatistics(2)
    Write-Host "TOTAL_PAGES:$totalPages"
    
    $sections = @(
        "1. Carátula", "2. Índice", "3. Título", "4. Resumen del Sistema", "5. Análisis",
        "5.1. Introducción", "5.2. Descripción General", "5.3. Justificación",
        "5.4. Objetivos Generales", "5.5. Objetivos Específicos", "5.6. Límites del Sistema",
        "5.7. Requerimientos del Sistema. Casos de Uso", "5.8. Estudio de Factibilidad",
        "5.9. Cronograma (Diagrama Gantt)", "5.10. Presupuesto", "6. Diseño",
        "6.1. Reglas de Negocio", "6.2. Herramientas de Modelado de Datos Seleccionado (DFD)",
        "6.3. Base de Datos (con diccionario y mapa canónico)", "6.4. Frontend / Prototipo",
        "7. Conclusión sobre el Proyecto", "8. Bibliografía", "9. Glosario de Palabras Técnicas"
    )

    foreach ($para in $d.Paragraphs) {{
        $t = $para.Range.Text.Trim()
        foreach ($sec in $sections) {{
            if ($t -eq $sec -or $t.StartsWith($sec)) {{
                $pg = $para.Range.Information(3)
                if ($para.Range.Start -gt 2500) {{
                    Write-Host "PAGE_ENTRY:$sec=$pg"
                    break
                }}
            }}
        }}
    }}
    $d.Close([ref]0)
    $w.Quit()
    '''
    
    res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_query], capture_output=True, text=True)
    page_dict = {
        "1.": 1,
        "2.": 2,
        "3.": 3,
        "4.": 3,
        "5.": 4,
        "1. Carátula": 1,
        "2. Índice": 2,
        "3. Título": 3,
        "4. Resumen del Sistema": 3
    }
    
    for line in res.stdout.splitlines():
        line = line.strip()
        if line.startswith("TOTAL_PAGES:"):
            print("  Total de páginas preliminares:", line.split(":", 1)[1])
        elif line.startswith("PAGE_ENTRY:"):
            entry = line.split(":", 1)[1]
            if "=" in entry:
                sec_name, sec_pg = entry.split("=", 1)
                sec_name = sec_name.strip()
                sec_pg = int(sec_pg.strip())
                num_prefix = sec_name.split()[0]
                page_dict[num_prefix] = sec_pg
                page_dict[sec_name] = sec_pg
                print(f"  [{num_prefix}] {sec_name} -> Página {sec_pg}")

    # -------------------------------------------------------------------------
    # PASO 3: Regeneración con números de página 100% exactos en el Índice
    # -------------------------------------------------------------------------
    print("\n[Paso 3/4] Re-construyendo documento con índice verificado...")
    complete_project_folder(page_dict)

    # -------------------------------------------------------------------------
    # PASO 4: Exportación nativa a PDF y guardado final
    # -------------------------------------------------------------------------
    print("\n[Paso 4/4] Exportando a PDF y distribuyendo entregables...")
    ps_export = f'''
    $w = New-Object -ComObject Word.Application
    $w.Visible = $false
    $d = $w.Documents.Open("{docx_facultad}")
    
    # Save docx
    $d.Save()
    
    # Export to PDF (wdFormatPDF = 17)
    $d.SaveAs([ref]"{pdf_facultad}", [ref]17)
    $totalPagesFinal = $d.ComputeStatistics(2)
    Write-Host "FINAL_PAGES:$totalPagesFinal"
    $d.Close([ref]0)
    $w.Quit()
    '''
    res_exp = subprocess.run(["powershell", "-NoProfile", "-Command", ps_export], capture_output=True, text=True)
    for line in res_exp.stdout.splitlines():
        if "FINAL_PAGES:" in line:
            print("  Total de páginas final en PDF:", line.split(":", 1)[1])

    # Copy to Downloads\Carpeta, Downloads\Carpeta final and Desktop
    os.makedirs(os.path.dirname(docx_downloads), exist_ok=True)
    shutil.copy2(docx_facultad, docx_downloads)
    shutil.copy2(pdf_facultad, pdf_downloads)
    
    os.makedirs(os.path.dirname(docx_downloads_alt), exist_ok=True)
    shutil.copy2(docx_facultad, docx_downloads_alt)
    shutil.copy2(pdf_facultad, pdf_downloads_alt)
    
    os.makedirs(os.path.dirname(docx_desktop), exist_ok=True)
    shutil.copy2(docx_facultad, docx_desktop)
    shutil.copy2(pdf_facultad, pdf_desktop)
    
    gdrive_dir = r"G:\Mi unidad"
    gdrive_copied = False
    if os.path.exists(gdrive_dir):
        docx_gdrive = os.path.join(gdrive_dir, "Carpeta final (Gómez Axel Joaquín).docx")
        pdf_gdrive = os.path.join(gdrive_dir, "Carpeta final (Gómez Axel Joaquín).pdf")
        shutil.copy2(docx_facultad, docx_gdrive)
        shutil.copy2(pdf_facultad, pdf_gdrive)
        gdrive_copied = True
    
    print("\n" + "=" * 60)
    print("PROCESO FINALIZADO CON ÉXITO")
    print("=" * 60)
    print(f"Archivos Word generados:")
    print(f"  - {docx_facultad}")
    print(f"  - {docx_downloads}")
    print(f"  - {docx_desktop}")
    if gdrive_copied:
        print(f"  - {docx_gdrive}")
    print(f"Archivos PDF generados:")
    print(f"  - {pdf_facultad}")
    print(f"  - {pdf_downloads}")
    print(f"  - {pdf_desktop}")
    if gdrive_copied:
        print(f"  - {pdf_gdrive}")

if __name__ == "__main__":
    run_export()

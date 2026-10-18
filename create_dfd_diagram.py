from PIL import Image, ImageDraw, ImageFont
import math

def draw_arrow(draw, start, end, color=(40, 40, 40), width=2, arrow_len=10, arrow_angle=25):
    # Draw line
    draw.line([start, end], fill=color, width=width)
    # Calculate angle
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    angle = math.atan2(dy, dx)
    
    # Arrow wings
    angle1 = angle + math.radians(180 - arrow_angle)
    angle2 = angle - math.radians(180 - arrow_angle)
    
    x1 = end[0] + arrow_len * math.cos(angle1)
    y1 = end[1] + arrow_len * math.sin(angle1)
    x2 = end[0] + arrow_len * math.cos(angle2)
    y2 = end[1] + arrow_len * math.sin(angle2)
    
    draw.polygon([end, (x1, y1), (x2, y2)], fill=color)

def draw_rounded_proc(draw, box, proc_id, title, font_id, font_title, bg=(245, 247, 250), border=(50, 70, 95)):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=16, fill=bg, outline=border, width=2)
    # Divider line
    mid_y = y0 + 32
    draw.line([(x0, mid_y), (x1, mid_y)], fill=border, width=1)
    # Text
    draw.text(((x0 + x1)//2, y0 + 16), proc_id, fill=border, font=font_id, anchor="mm")
    # Wrap title if needed
    lines = title.split("\n")
    if len(lines) == 1:
        draw.text(((x0 + x1)//2, (mid_y + y1)//2), lines[0], fill=(20, 20, 20), font=font_title, anchor="mm")
    else:
        spacing = 18
        start_y = (mid_y + y1)//2 - (len(lines)-1)*spacing//2
        for i, l in enumerate(lines):
            draw.text(((x0 + x1)//2, start_y + i*spacing), l, fill=(20, 20, 20), font=font_title, anchor="mm")

def draw_store(draw, box, store_id, title, font_id, font_title):
    x0, y0, x1, y1 = box
    # Data store has top and bottom lines, closed on left with ID
    draw.rectangle(box, fill=(255, 255, 255), outline=None)
    draw.line([(x0, y0), (x1, y0)], fill=(30, 30, 30), width=2)
    draw.line([(x0, y1), (x1, y1)], fill=(30, 30, 30), width=2)
    id_w = 60
    draw.line([(x0, y0), (x0, y1)], fill=(30, 30, 30), width=2)
    draw.line([(x0 + id_w, y0), (x0 + id_w, y1)], fill=(30, 30, 30), width=2)
    # Text
    draw.text((x0 + id_w//2, (y0 + y1)//2), store_id, fill=(0, 0, 0), font=font_id, anchor="mm")
    draw.text((x0 + id_w + 12, (y0 + y1)//2), title, fill=(0, 0, 0), font=font_title, anchor="lm")

def build_dfd_image(out_path):
    w, h = 1700, 1150
    im = Image.new("RGB", (w, h), color=(255, 255, 255))
    draw = ImageDraw.Draw(im)

    # Fonts
    font_main_title = ImageFont.truetype("C:/Windows/Fonts/calibrib.ttf", 26)
    font_sub_title = ImageFont.truetype("C:/Windows/Fonts/calibri.ttf", 15)
    font_id = ImageFont.truetype("C:/Windows/Fonts/calibrib.ttf", 15)
    font_proc = ImageFont.truetype("C:/Windows/Fonts/calibrib.ttf", 15)
    font_entity = ImageFont.truetype("C:/Windows/Fonts/calibrib.ttf", 18)
    font_store_id = ImageFont.truetype("C:/Windows/Fonts/calibrib.ttf", 15)
    font_store = ImageFont.truetype("C:/Windows/Fonts/calibri.ttf", 15)
    font_flow = ImageFont.truetype("C:/Windows/Fonts/calibri.ttf", 13)

    # Header
    draw.text((w//2, 35), "DIAGRAMA DE FLUJO DE DATOS (DFD) — NIVEL 1", fill=(0, 0, 0), font=font_main_title, anchor="mm")
    draw.text((w//2, 68), "Sistema: Gestor de Calorías Regional · Notación: Yourdon / DeMarco", fill=(90, 90, 90), font=font_sub_title, anchor="mm")
    draw.line([(80, 95), (w - 80, 95)], fill=(200, 200, 200), width=1)

    # Entity USUARIO (Left side)
    ent_box = (80, 380, 230, 780)
    draw.rectangle(ent_box, fill=(240, 243, 248), outline=(30, 40, 60), width=2)
    # Inner border to look like an external entity
    draw.rectangle((ent_box[0]+4, ent_box[1]+4, ent_box[2]-4, ent_box[3]-4), outline=(100, 120, 150), width=1)
    draw.text(((ent_box[0]+ent_box[2])//2, (ent_box[1]+ent_box[3])//2 - 20), "ENTIDAD\nEXTERNA", fill=(80, 80, 80), font=font_flow, anchor="mm")
    draw.text(((ent_box[0]+ent_box[2])//2, (ent_box[1]+ent_box[3])//2 + 25), "USUARIO", fill=(10, 20, 40), font=font_entity, anchor="mm")

    # Processes (Middle column)
    # P1: (380, 140, 670, 240)
    p1_box = (380, 140, 680, 240)
    draw_rounded_proc(draw, p1_box, "PROCESO 1.0", "Gestionar Perfiles y\nMetas Biométricas", font_id, font_proc)

    # P2: (380, 340, 680, 440)
    p2_box = (380, 340, 680, 440)
    draw_rounded_proc(draw, p2_box, "PROCESO 2.0", "Administrar Catálogo\ny Recetas Regionales", font_id, font_proc)

    # P3: (380, 540, 680, 640)
    p3_box = (380, 540, 680, 640)
    draw_rounded_proc(draw, p3_box, "PROCESO 3.0", "Registrar Consumos y\nCalcular Nutrientes", font_id, font_proc)

    # P4: (380, 740, 680, 840)
    p4_box = (380, 740, 680, 840)
    draw_rounded_proc(draw, p4_box, "PROCESO 4.0", "Controlar Hidratación\ny Evolución de Peso", font_id, font_proc)

    # P5: (380, 940, 680, 1040)
    p5_box = (380, 940, 680, 1040)
    draw_rounded_proc(draw, p5_box, "PROCESO 5.0", "Generar Dashboard,\nMétricas y Alertas", font_id, font_proc)

    # Data Stores (Right column)
    d1_box = (1050, 160, 1580, 220)
    draw_store(draw, d1_box, "D1", "USUARIO (Perfiles y Metas Calóricas)", font_store_id, font_store)

    d2_box = (1050, 360, 1580, 420)
    draw_store(draw, d2_box, "D2", "ALIMENTO (Catálogo Regional y Recetas)", font_store_id, font_store)

    d3_box = (1050, 560, 1580, 620)
    draw_store(draw, d3_box, "D3", "REGISTRO_DIARIO (Ingestas y Macros)", font_store_id, font_store)

    d4_box = (1050, 730, 1580, 790)
    draw_store(draw, d4_box, "D4", "REGISTRO_AGUA (Consumo Diario)", font_store_id, font_store)

    d5_box = (1050, 820, 1580, 880)
    draw_store(draw, d5_box, "D5", "REGISTRO_PESO (Historial Corporal)", font_store_id, font_store)

    # --- Flows between Usuario and Processes ---
    # Flow User -> P1
    draw_arrow(draw, (230, 420), (380, 190))
    draw.text((285, 290), "Datos biométricos y metas", fill=(40, 40, 40), font=font_flow, anchor="mm")

    # Flow User -> P2
    draw_arrow(draw, (230, 480), (380, 390))
    draw.text((290, 420), "Búsqueda e ingredientes", fill=(40, 40, 40), font=font_flow, anchor="mm")

    # Flow User -> P3
    draw_arrow(draw, (230, 580), (380, 590))
    draw.text((300, 570), "Alimento, fecha y gramaje", fill=(40, 40, 40), font=font_flow, anchor="mm")

    # Flow User -> P4
    draw_arrow(draw, (230, 680), (380, 790))
    draw.text((290, 750), "Toma de agua y peso", fill=(40, 40, 40), font=font_flow, anchor="mm")

    # Flow P5 -> User
    draw_arrow(draw, (380, 990), (230, 740))
    draw.text((280, 885), "Dashboard, métricas y alertas", fill=(20, 70, 140), font=font_flow, anchor="mm")

    # --- Flows between Processes and Stores ---
    # P1 -> D1
    draw_arrow(draw, (680, 190), (1050, 190))
    draw.text((865, 175), "Guardar / actualizar perfil", fill=(40, 40, 40), font=font_flow, anchor="mm")

    # P2 -> D2
    draw_arrow(draw, (680, 380), (1050, 380))
    draw.text((865, 365), "Guardar recetas y alimentos", fill=(40, 40, 40), font=font_flow, anchor="mm")

    # D2 -> P2
    draw_arrow(draw, (1050, 400), (680, 400))
    draw.text((865, 415), "Catálogo de alimentos locales", fill=(40, 40, 40), font=font_flow, anchor="mm")

    # D2 -> P3 (Read nutrients)
    draw.line([(1050, 410), (960, 410), (960, 570), (680, 570)], fill=(40, 40, 40), width=2)
    draw_arrow(draw, (960, 570), (680, 570))
    draw.text((840, 555), "Valores nutricionales / 100g", fill=(40, 40, 40), font=font_flow, anchor="mm")

    # P3 -> D3
    draw_arrow(draw, (680, 600), (1050, 600))
    draw.text((865, 615), "Ingesta calculada y macronutrientes", fill=(40, 40, 40), font=font_flow, anchor="mm")

    # P4 -> D4
    draw_arrow(draw, (680, 770), (1050, 760))
    draw.text((865, 750), "Registro de agua (ml)", fill=(40, 40, 40), font=font_flow, anchor="mm")

    # P4 -> D5
    draw_arrow(draw, (680, 810), (1050, 850))
    draw.text((865, 840), "Registro de peso (kg)", fill=(40, 40, 40), font=font_flow, anchor="mm")

    # Stores to P5 (Generation of metrics and summary)
    # Line from D1, D3, D4, D5 down to P5
    draw.line([(1315, 620), (1315, 990), (680, 990)], fill=(20, 70, 140), width=2)
    draw_arrow(draw, (850, 990), (680, 990), color=(20, 70, 140))
    draw.text((920, 975), "Consumos del día, metas activas e históricos", fill=(20, 70, 140), font=font_flow, anchor="mm")

    im.save(out_path, quality=95)
    print("DFD diagram generated successfully at:", out_path)

if __name__ == "__main__":
    out = r"C:\Users\Joaquín\Documents\Facultad\Practica profesional\Gestor de calorias regional\Carpeta\diagrama_dfd_proyecto.png"
    build_dfd_image(out)

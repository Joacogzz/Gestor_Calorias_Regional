import sqlite3
import datetime

DB_PATH = 'calorias.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # App Settings
    c.execute('''
        CREATE TABLE IF NOT EXISTS app_settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    
    # Profile
    c.execute('''
        CREATE TABLE IF NOT EXISTS profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            gender TEXT,
            age INTEGER,
            weight REAL,
            height REAL,
            goal TEXT,
            target_calories INTEGER,
            target_protein REAL,
            target_carbs REAL,
            target_fat REAL
        )
    ''')
    
    # Foods
    c.execute('''
        CREATE TABLE IF NOT EXISTS foods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            calories_per_100g REAL,
            protein_per_100g REAL,
            carbs_per_100g REAL,
            fat_per_100g REAL,
            is_regional INTEGER DEFAULT 0,
            is_recipe INTEGER DEFAULT 0,
            is_favorite INTEGER DEFAULT 0
        )
    ''')
    
    # Diary
    c.execute('''
        CREATE TABLE IF NOT EXISTS diary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id INTEGER DEFAULT 0,
            date TEXT,
            food_id INTEGER,
            food_name TEXT,
            amount_g REAL,
            calories REAL,
            protein REAL,
            carbs REAL,
            fat REAL,
            meal_type TEXT DEFAULT 'Snack'
        )
    ''')
    
    # Water Log
    c.execute('''
        CREATE TABLE IF NOT EXISTS water_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id INTEGER DEFAULT 0,
            date TEXT,
            amount_ml INTEGER
        )
    ''')
    
    # Weight Log
    c.execute('''
        CREATE TABLE IF NOT EXISTS weight_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id INTEGER DEFAULT 0,
            date TEXT,
            weight REAL
        )
    ''')
    
    try:
        c.execute('ALTER TABLE diary ADD COLUMN profile_id INTEGER DEFAULT 0')
    except:
        pass
    try:
        c.execute('ALTER TABLE water_log ADD COLUMN profile_id INTEGER DEFAULT 0')
    except:
        pass
    try:
        c.execute('ALTER TABLE diary ADD COLUMN meal_type TEXT DEFAULT "Snack"')
    except:
        pass
    try:
        c.execute('ALTER TABLE profile ADD COLUMN target_protein REAL DEFAULT 150')
        c.execute('ALTER TABLE profile ADD COLUMN target_carbs REAL DEFAULT 200')
        c.execute('ALTER TABLE profile ADD COLUMN target_fat REAL DEFAULT 60')
    except:
        pass
        
    try:
        c.execute('ALTER TABLE profile ADD COLUMN water_goal INTEGER DEFAULT 2000')
    except:
        pass
        
    try:
        c.execute('ALTER TABLE profile ADD COLUMN activity_level TEXT DEFAULT "Actividad moderada: ejercicio moderado o deporte 3-5 días a la semana"')
    except:
        pass
        
    conn.commit()
    conn.close()
    
    seed_regional_foods()

def seed_regional_foods():
    regional_foods = [
        ("Mandioca Hervida", 160, 1.4, 38.1, 0.3, 1),
        ("Sopa Paraguaya", 260, 8.5, 23.0, 15.0, 1),
        ("Bife Asado (Vaca)", 250, 26.0, 0.0, 17.0, 1),
        ("Chipa", 320, 10.0, 40.0, 14.0, 1),
        ("Empanada de Carne (al horno)", 280, 10.0, 30.0, 13.0, 1),
        ("Guiso de Arroz", 130, 4.0, 20.0, 3.5, 1),
        ("Mbeyú", 300, 5.0, 45.0, 12.0, 1),
        ("Puchero", 150, 12.0, 8.0, 8.0, 1),
        ("Asado (Tira de Asado)", 350, 15.0, 0.0, 32.0, 1),
        ("Choripán", 290, 12.0, 25.0, 16.0, 1),
        ("Milanesa de Carne (frita)", 260, 14.0, 22.0, 13.0, 1),
        ("Milanesa de Carne (al horno)", 220, 15.0, 22.0, 8.0, 1),
        ("Mandioca Frita", 310, 1.2, 40.0, 16.0, 1),
        
        # --- Comidas Regionales (Misiones, Argentina) ---
        ("Reviro", 350, 6.0, 45.0, 18.0, 1),
        ("Ticueí (Carne picada frita)", 280, 20.0, 2.0, 22.0, 1),
        ("Surubí al Horno", 140, 18.0, 0.0, 7.0, 1),
        ("Pacú a la Parrilla", 180, 20.0, 0.0, 10.0, 1),
        ("Mate Cocido (con azúcar)", 40, 0.0, 10.0, 0.0, 1),
        ("Torta Frita", 380, 5.0, 48.0, 20.0, 1),
        ("Vorí Vorí de Pollo", 120, 10.0, 12.0, 4.0, 1),
        ("Chipa Guazú", 260, 9.0, 25.0, 14.0, 1),
        ("Caburé (Chipa Asado)", 330, 11.0, 38.0, 15.0, 1),
        ("Locro", 180, 8.0, 18.0, 8.0, 1),
        
        # --- Alimentos Genéricos (Básicos y Cocina) ---
        # Harinas y Panadería
        ("Harina de Trigo (0000)", 364, 10.0, 76.0, 1.0, 0),
        ("Harina de Trigo Integral", 340, 13.0, 72.0, 2.5, 0),
        ("Harina de Maíz (Polenta)", 362, 8.0, 77.0, 1.5, 0),
        ("Avena Tradicional", 389, 16.9, 66.3, 6.9, 0),
        ("Pan Rallado", 395, 13.0, 75.0, 3.0, 0),
        ("Pan Lactal Blanco", 265, 8.0, 49.0, 3.0, 0),
        ("Pan Lactal Integral", 250, 9.0, 43.0, 4.0, 0),
        ("Pan Francés", 270, 9.0, 50.0, 3.0, 0),
        ("Galletas de Arroz", 380, 8.0, 80.0, 2.0, 0),
        
        # Huevos
        ("Huevo Entero (Crudo)", 143, 12.5, 0.7, 9.5, 0),
        ("Huevo Duro", 155, 13.0, 1.1, 11.0, 0),
        ("Huevo Frito", 196, 13.6, 1.0, 15.0, 0),
        ("Huevo Revuelto (con aceite)", 210, 14.0, 1.5, 16.0, 0),
        ("Clara de Huevo (Cruda)", 52, 11.0, 0.7, 0.2, 0),
        ("Yema de Huevo (Cruda)", 322, 16.0, 3.6, 27.0, 0),
        ("Omelette (2 huevos)", 170, 12.0, 1.0, 13.0, 0),
        
        # Carnes y Aves
        ("Pechuga de Pollo (Cruda)", 120, 23.0, 0.0, 2.6, 0),
        ("Pechuga de Pollo (Plancha)", 165, 31.0, 0.0, 3.6, 0),
        ("Pata/Muslo de Pollo (Horno)", 210, 24.0, 0.0, 12.0, 0),
        ("Carne Picada Magra", 212, 26.0, 0.0, 11.0, 0),
        ("Carne Picada Común", 332, 14.0, 0.0, 30.0, 0),
        ("Bife de Chorizo", 270, 25.0, 0.0, 19.0, 0),
        ("Milanesa de Carne (Frita)", 260, 14.0, 22.0, 13.0, 0),
        ("Milanesa de Carne (Horno)", 220, 15.0, 22.0, 8.0, 0),
        ("Milanesa de Pollo (Frita)", 280, 15.0, 20.0, 15.0, 0),
        ("Cerdo (Costillita)", 290, 20.0, 0.0, 23.0, 0),
        ("Bondiola de Cerdo", 310, 16.0, 0.0, 27.0, 0),
        ("Chorizo Parrillero", 340, 14.0, 2.0, 30.0, 0),
        ("Salchicha de Viena", 260, 12.0, 3.0, 22.0, 0),
        ("Hamburguesa (Medallón crudo)", 250, 15.0, 2.0, 20.0, 0),
        
        # Pescados
        ("Atún al Natural (Lata)", 116, 26.0, 0.0, 1.0, 0),
        ("Atún en Aceite (Lata)", 198, 29.0, 0.0, 8.0, 0),
        ("Filet de Merluza (Crudo)", 90, 19.0, 0.0, 1.5, 0),
        ("Filet de Merluza (Frito)", 200, 16.0, 12.0, 10.0, 0),
        ("Salmón Rosado", 208, 20.0, 0.0, 13.0, 0),
        
        # Lácteos y Grasas
        ("Leche Entera", 61, 3.2, 4.8, 3.3, 0),
        ("Leche Descremada", 34, 3.4, 5.0, 0.1, 0),
        ("Yogur Natural", 61, 3.5, 4.7, 3.3, 0),
        ("Queso Cremoso / Cuartirolo", 300, 14.0, 2.0, 25.0, 0),
        ("Queso Mozzarella", 300, 22.0, 2.0, 22.0, 0),
        ("Queso Rallado", 431, 38.0, 4.0, 29.0, 0),
        ("Queso Untable Clásico", 250, 8.0, 4.0, 23.0, 0),
        ("Ricota Magra", 100, 11.0, 3.0, 4.0, 0),
        ("Manteca", 717, 0.8, 0.1, 81.0, 0),
        ("Crema de Leche", 340, 2.0, 3.0, 36.0, 0),
        ("Aceite de Girasol", 884, 0.0, 0.0, 100.0, 0),
        ("Aceite de Oliva", 884, 0.0, 0.0, 100.0, 0),
        
        # Cereales y Legumbres
        ("Arroz Blanco (Crudo)", 360, 7.0, 80.0, 0.6, 0),
        ("Arroz Blanco (Hervido)", 130, 2.7, 28.0, 0.3, 0),
        ("Arroz Integral (Hervido)", 111, 2.6, 23.0, 0.9, 0),
        ("Fideos Secos (Crudos)", 350, 12.0, 70.0, 1.5, 0),
        ("Fideos (Hervidos)", 130, 4.0, 25.0, 0.5, 0),
        ("Lentejas (Crudas)", 352, 24.0, 60.0, 1.0, 0),
        ("Lentejas (Hervidas)", 116, 9.0, 20.0, 0.4, 0),
        ("Garbanzos (Hervidos)", 164, 8.8, 27.0, 2.5, 0),
        ("Porotos (Hervidos)", 127, 8.6, 22.0, 0.5, 0),
        ("Quinoa (Hervida)", 120, 4.4, 21.0, 1.9, 0),
        
        # Verduras
        ("Papa (Cruda)", 77, 2.0, 17.0, 0.1, 0),
        ("Papa Hervida", 87, 1.9, 20.0, 0.1, 0),
        ("Papa Frita", 312, 3.4, 41.0, 15.0, 0),
        ("Batata Hervida", 86, 1.6, 20.1, 0.1, 0),
        ("Zapallo / Calabaza", 26, 1.0, 6.0, 0.1, 0),
        ("Tomate Fresco", 18, 0.9, 3.9, 0.2, 0),
        ("Cebolla Fresca", 40, 1.1, 9.3, 0.1, 0),
        ("Cebolla Caramelizada / Frita", 120, 1.5, 12.0, 8.0, 0),
        ("Morrón / Pimiento", 20, 0.9, 4.6, 0.2, 0),
        ("Ajo", 149, 6.3, 33.0, 0.5, 0),
        ("Zanahoria Fresca", 41, 0.9, 9.5, 0.2, 0),
        ("Zanahoria Hervida", 35, 0.8, 8.2, 0.2, 0),
        ("Lechuga", 15, 1.4, 2.9, 0.2, 0),
        ("Rúcula", 25, 2.5, 3.6, 0.6, 0),
        ("Espinaca Fresca", 23, 2.8, 3.6, 0.4, 0),
        ("Brócoli Hervido", 35, 2.4, 7.2, 0.4, 0),
        ("Choclo (Maíz dulce)", 86, 3.2, 18.0, 1.1, 0),
        ("Arvejas (Lata)", 68, 4.0, 12.0, 0.4, 0),
        
        # Frutas
        ("Manzana", 52, 0.3, 14.0, 0.2, 0),
        ("Banana", 89, 1.1, 23.0, 0.3, 0),
        ("Naranja", 47, 0.9, 12.0, 0.1, 0),
        ("Mandarina", 53, 0.8, 13.0, 0.3, 0),
        ("Palta (Aguacate)", 160, 2.0, 8.5, 14.7, 0),
        ("Frutilla", 32, 0.6, 7.6, 0.3, 0),
        ("Limón", 29, 1.1, 9.3, 0.3, 0),
        ("Uva", 69, 0.7, 18.0, 0.1, 0),
        ("Durazno", 39, 0.9, 9.5, 0.2, 0),
        
        # Azúcares, Condimentos y Otros
        ("Azúcar Blanca", 387, 0.0, 100.0, 0.0, 0),
        ("Edulcorante (Polvo/Líquido)", 0, 0.0, 0.0, 0.0, 0),
        ("Cacao en Polvo Amargo", 228, 19.0, 57.0, 13.0, 0),
        ("Miel", 304, 0.3, 82.0, 0.0, 0),
        ("Mayonesa", 680, 1.0, 0.6, 75.0, 0),
        ("Ketchup", 112, 1.0, 25.0, 0.1, 0),
        ("Mostaza", 60, 3.0, 5.0, 3.0, 0),
        ("Salsa de Tomate (Puré)", 38, 1.5, 8.0, 0.2, 0),
        ("Salsa de Soja", 53, 8.0, 4.0, 0.1, 0),
        
        # Snacks y Galletas
        ("Maní Tostado", 567, 25.8, 16.1, 49.2, 0),
        ("Almendras", 579, 21.0, 21.0, 49.0, 0),
        ("Nueces", 654, 15.0, 13.0, 65.0, 0),
        ("Galletitas de Agua", 414, 10.0, 70.0, 10.0, 0),
        ("Galletitas de Salvado", 405, 12.0, 65.0, 12.0, 0),
        ("Galletitas Dulces (Vainilla)", 460, 6.0, 65.0, 20.0, 0),
        ("Galletitas Pepas (Membrillo)", 410, 5.0, 70.0, 14.0, 0),
        ("Galletitas Rellenas (tipo Oreo)", 480, 5.0, 68.0, 22.0, 0),
        ("Galletitas Surtidas", 450, 6.0, 68.0, 18.0, 0),
        ("Galletitas de Chocolate", 440, 6.0, 70.0, 15.0, 0),
        ("Vainillas", 360, 8.0, 75.0, 3.0, 0),
        ("Alfajor de Maicena", 380, 5.0, 55.0, 15.0, 0),
        ("Dulce de Leche", 315, 7.0, 55.0, 7.0, 0),
        
        # --- Bebidas e Infusiones ---
        ("Agua", 0, 0.0, 0.0, 0.0, 0),
        ("Gaseosa Cola (Común)", 42, 0.0, 10.6, 0.0, 0),
        ("Gaseosa Cola (Zero/Diet)", 0, 0.0, 0.0, 0.0, 0),
        ("Cerveza Rubia", 43, 0.5, 3.6, 0.0, 0),
        ("Vino Tinto", 85, 0.1, 2.6, 0.0, 0),
        ("Vino Blanco", 82, 0.1, 2.6, 0.0, 0),
        ("Jugo de Naranja Exprimid", 45, 0.7, 10.4, 0.2, 0),
        ("Café (Sin azúcar)", 1, 0.1, 0.0, 0.0, 0),
        ("Té (Sin azúcar)", 1, 0.0, 0.0, 0.0, 0),
        ("Mate (Infusión sin azúcar)", 1, 0.0, 0.0, 0.0, 0),

        # --- Comidas Preparadas / Rápidas ---
        ("Pizza de Muzzarella (1 porción)", 260, 10.0, 30.0, 10.0, 0),
        ("Empanada de Jamón y Queso (Horno)", 250, 10.0, 25.0, 12.0, 0),
        ("Tartas (Verdura/Pascualina)", 200, 7.0, 20.0, 10.0, 0),
        ("Ravioles de Ricota (con salsa)", 210, 8.0, 30.0, 6.0, 0),
        ("Ñoquis de Papa (con salsa)", 180, 5.0, 32.0, 3.0, 0),
        ("Sándwich de Milanesa Completo", 650, 30.0, 60.0, 30.0, 0),
        ("Hamburguesa Completa (Rápida)", 550, 25.0, 45.0, 30.0, 0),
        ("Papas Fritas de Paquete (Snack)", 536, 6.0, 53.0, 35.0, 0),
        ("Helado (Crema)", 207, 3.5, 24.0, 11.0, 0),
        
        # --- Fiambres y Embutidos ---
        ("Jamón Cocido", 108, 18.0, 1.5, 3.0, 0),
        ("Jamón Crudo", 235, 28.0, 0.0, 13.0, 0),
        ("Salame", 410, 22.0, 1.0, 35.0, 0),
        ("Mortadela", 311, 14.0, 3.0, 27.0, 0),
        ("Queso de Máquina (Tybo)", 320, 23.0, 2.0, 24.0, 0),
        ("Panceta Frita", 541, 37.0, 0.0, 42.0, 0),

        # --- Más Platos Regionales / Tradicionales ---
        ("Guiso de Fideos", 140, 5.0, 22.0, 4.0, 1),
        ("Sopa de Verduras", 40, 2.0, 6.0, 1.0, 0),
        
        # --- Panadería Dulce y Desayuno ---
        ("Medialuna de Manteca", 380, 7.0, 48.0, 18.0, 0),
        ("Medialuna de Grasa", 420, 7.0, 45.0, 24.0, 0),
        ("Bizcochito de Grasa", 480, 10.0, 50.0, 28.0, 0),
        ("Churros (sin relleno)", 350, 4.0, 40.0, 20.0, 0),
        ("Granola (con pasas/almendras)", 470, 10.0, 64.0, 20.0, 0),
        ("Cereales Azucarados (Copos)", 380, 5.0, 85.0, 1.0, 0),
        
        # --- Más Frutas ---
        ("Ananá (Piña)", 50, 0.5, 13.0, 0.1, 0),
        ("Sandía", 30, 0.6, 8.0, 0.1, 0),
        ("Melón", 34, 0.8, 8.0, 0.2, 0),
        ("Kiwi", 61, 1.1, 15.0, 0.5, 0),
        ("Ciruela", 46, 0.7, 11.0, 0.3, 0),
        ("Mango", 60, 0.8, 15.0, 0.4, 0),
        
        # --- Más Verduras ---
        ("Zapallito Verde (Hervido)", 17, 1.0, 3.5, 0.1, 0),
        ("Berenjena (Al horno)", 35, 1.0, 8.0, 0.2, 0),
        ("Pepino", 15, 0.6, 3.6, 0.1, 0),
        ("Coliflor (Hervido)", 23, 1.8, 4.1, 0.5, 0),
        ("Apio", 16, 0.7, 3.0, 0.2, 0),
        ("Remolacha (Hervida)", 44, 1.7, 10.0, 0.2, 0),
        ("Acelga Fresca", 19, 1.8, 3.7, 0.2, 0),
        
        # --- Más Pescados y Mariscos ---
        ("Calamar (Hervido)", 90, 15.0, 3.0, 1.5, 0),
        ("Rabas (Calamares Fritos)", 250, 14.0, 20.0, 13.0, 0),
        ("Camarones (Hervidos)", 99, 24.0, 0.0, 0.3, 0),
        
        # --- Lácteos, Fiambres y Cortadillos Adicionales ---
        ("Queso Roquefort / Azul", 353, 21.0, 2.0, 28.0, 0),
        ("Queso Sardo / Duro", 390, 33.0, 2.0, 28.0, 0),
        ("Jamón de Pavo / Pechuga", 104, 16.0, 4.0, 2.0, 0),
        ("Salchicha Parrillera", 340, 14.0, 2.0, 30.0, 0),
        
        # --- Más Bebidas y Salsas ---
        ("Leche Chocolatada", 80, 3.3, 11.0, 2.5, 0),
        ("Agua con Gas / Soda", 0, 0.0, 0.0, 0.0, 0),
        ("Jugo en Polvo (Preparado)", 10, 0.0, 2.5, 0.0, 0),
        ("Salsa Blanca (Bechamel)", 130, 4.0, 9.0, 8.0, 0),
        ("Salsa Pesto", 450, 5.0, 4.0, 45.0, 0),
        
        # --- Legumbres y Otros ---
        ("Soja Texturizada (Seca)", 350, 50.0, 30.0, 1.5, 0),
        ("Tofu (Queso de soja)", 76, 8.0, 1.9, 4.8, 0),
        ("Arepa (Maíz blanco)", 350, 7.0, 75.0, 1.5, 0),
        ("Tortilla de Trigo (Wrap)", 310, 8.0, 50.0, 8.0, 0),
    ]
    
    conn = get_db_connection()
    c = conn.cursor()
    for f in regional_foods:
        c.execute('SELECT COUNT(*) FROM foods WHERE name = ?', (f[0],))
        if c.fetchone()[0] == 0:
            c.execute('''
                INSERT INTO foods (name, calories_per_100g, protein_per_100g, carbs_per_100g, fat_per_100g, is_regional)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', f)
    conn.commit()
    conn.close()

# --- PROFILE METHODS ---
def get_profiles():
    conn = get_db_connection()
    profiles = conn.execute('SELECT * FROM profile').fetchall()
    conn.close()
    return [dict(p) for p in profiles]

def get_active_profile_id():
    conn = get_db_connection()
    res = conn.execute('SELECT value FROM app_settings WHERE key = "active_profile_id"').fetchone()
    conn.close()
    return int(res['value']) if res else None

def set_active_profile_id(profile_id):
    conn = get_db_connection()
    conn.execute('INSERT OR REPLACE INTO app_settings (key, value) VALUES ("active_profile_id", ?)', (str(profile_id),))
    conn.commit()
    conn.close()

def get_theme_mode():
    conn = get_db_connection()
    res = conn.execute('SELECT value FROM app_settings WHERE key = "theme_mode"').fetchone()
    conn.close()
    return res['value'] if res else "dark"

def set_theme_mode(mode_str):
    conn = get_db_connection()
    conn.execute('INSERT OR REPLACE INTO app_settings (key, value) VALUES ("theme_mode", ?)', (mode_str,))
    conn.commit()
    conn.close()

def get_profile():
    pid = get_active_profile_id()
    if not pid:
        # Fallback to first profile if exists
        profiles = get_profiles()
        if profiles:
            set_active_profile_id(profiles[-1]['id'])
            return profiles[-1]
        return None
    conn = get_db_connection()
    profile = conn.execute('SELECT * FROM profile WHERE id = ?', (pid,)).fetchone()
    conn.close()
    return dict(profile) if profile else None

def save_profile(name, gender, age, weight, height, goal, target_calories, target_prot=150, target_carbs=200, target_fat=60, water_goal=2000, activity_level="Actividad moderada: ejercicio moderado o deporte 3-5 días a la semana"):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO profile (name, gender, age, weight, height, goal, target_calories, target_protein, target_carbs, target_fat, water_goal, activity_level)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, gender, age, weight, height, goal, target_calories, target_prot, target_carbs, target_fat, water_goal, activity_level))
    conn.commit()
    pid = cursor.lastrowid
    conn.close()
    set_active_profile_id(pid)
    add_weight_log(pid, weight)
    return pid

def update_profile(profile_id, name, gender, age, weight, height, goal, target_calories, target_prot, target_carbs, target_fat, water_goal, activity_level="Actividad moderada: ejercicio moderado o deporte 3-5 días a la semana"):
    conn = get_db_connection()
    conn.execute('''
        UPDATE profile 
        SET name=?, gender=?, age=?, weight=?, height=?, goal=?, target_calories=?, target_protein=?, target_carbs=?, target_fat=?, water_goal=?, activity_level=?
        WHERE id=?
    ''', (name, gender, age, weight, height, goal, target_calories, target_prot, target_carbs, target_fat, water_goal, activity_level, profile_id))
    conn.commit()
    conn.close()
    # No agregamos weight_log acá para evitar spam, o se podría hacer si cambió el peso.

def delete_profile(profile_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM profile WHERE id = ?', (profile_id,))
    conn.execute('DELETE FROM diary WHERE profile_id = ?', (profile_id,))
    conn.execute('DELETE FROM water_log WHERE profile_id = ?', (profile_id,))
    conn.execute('DELETE FROM weight_log WHERE profile_id = ?', (profile_id,))
    conn.commit()
    conn.close()
    
    active_pid = get_active_profile_id()
    if active_pid == profile_id:
        profiles = get_profiles()
        if profiles:
            set_active_profile_id(profiles[0]['id'])
        else:
            conn = get_db_connection()
            conn.execute('DELETE FROM app_settings WHERE key = "active_profile_id"')
            conn.commit()
            conn.close()

# --- WEIGHT LOG METHODS ---
def add_weight_log(profile_id, weight):
    date_str = datetime.date.today().strftime('%Y-%m-%d')
    conn = get_db_connection()
    conn.execute('INSERT INTO weight_log (profile_id, date, weight) VALUES (?, ?, ?)', (profile_id, date_str, weight))
    conn.commit()
    conn.close()

def get_weight_logs():
    pid = get_active_profile_id()
    conn = get_db_connection()
    logs = conn.execute('SELECT date, weight FROM weight_log WHERE profile_id = ? ORDER BY id ASC', (pid,)).fetchall()
    conn.close()
    return [dict(l) for l in logs]

# --- FOOD METHODS ---
def search_foods(query=""):
    conn = get_db_connection()
    if query:
        foods = conn.execute('SELECT * FROM foods WHERE name LIKE ? ORDER BY is_favorite DESC, name', ('%' + query + '%',)).fetchall()
    else:
        foods = conn.execute('SELECT * FROM foods ORDER BY is_favorite DESC, name').fetchall()
    conn.close()
    return [dict(f) for f in foods]

def add_custom_food(name, cal, prot, carb, fat):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO foods (name, calories_per_100g, protein_per_100g, carbs_per_100g, fat_per_100g, is_regional, is_recipe, is_favorite)
        VALUES (?, ?, ?, ?, ?, 0, 0, 0)
    ''', (name, cal, prot, carb, fat))
    conn.commit()
    food_id = cursor.lastrowid
    conn.close()
    return food_id

def get_custom_foods():
    conn = get_db_connection()
    foods = conn.execute('SELECT * FROM foods WHERE is_regional = 0 AND is_recipe = 0 ORDER BY name').fetchall()
    conn.close()
    return [dict(f) for f in foods]

def update_custom_food(food_id, name, cal, prot, carb, fat):
    conn = get_db_connection()
    conn.execute('''
        UPDATE foods 
        SET name = ?, calories_per_100g = ?, protein_per_100g = ?, carbs_per_100g = ?, fat_per_100g = ?
        WHERE id = ? AND is_regional = 0 AND is_recipe = 0
    ''', (name, cal, prot, carb, fat, food_id))
    conn.commit()
    conn.close()

def delete_custom_food(food_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM foods WHERE id = ? AND is_regional = 0 AND is_recipe = 0', (food_id,))
    conn.commit()
    conn.close()

def toggle_favorite(food_id, is_favorite):
    conn = get_db_connection()
    conn.execute('UPDATE foods SET is_favorite = ? WHERE id = ?', (is_favorite, food_id))
    conn.commit()
    conn.close()

# --- RECIPE METHODS ---
def save_recipe(name, total_cal, total_prot, total_carb, total_fat):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO foods (name, calories_per_100g, protein_per_100g, carbs_per_100g, fat_per_100g, is_recipe)
        VALUES (?, ?, ?, ?, ?, 1)
    ''', (name, total_cal, total_prot, total_carb, total_fat))
    conn.commit()
    recipe_id = cursor.lastrowid
    conn.close()
    return recipe_id

def get_recipes():
    conn = get_db_connection()
    recipes = conn.execute('SELECT * FROM foods WHERE is_recipe = 1 ORDER BY name').fetchall()
    conn.close()
    return [dict(r) for r in recipes]

def delete_recipe(recipe_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM foods WHERE id = ? AND is_recipe = 1', (recipe_id,))
    conn.commit()
    conn.close()

# --- DIARY METHODS ---
def get_today_date():
    return datetime.date.today().strftime('%Y-%m-%d')

def add_diary_entry(food_id, food_name, amount_g, cal, prot, carb, fat, meal_type="Snack"):
    pid = get_active_profile_id()
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO diary (profile_id, date, food_id, food_name, amount_g, calories, protein, carbs, fat, meal_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (pid, get_today_date(), food_id, food_name, amount_g, cal, prot, carb, fat, meal_type))
    conn.commit()
    conn.close()

def update_diary_entry(entry_id, amount_g, cal, prot, carb, fat, meal_type="Snack"):
    conn = get_db_connection()
    conn.execute('''
        UPDATE diary 
        SET amount_g = ?, calories = ?, protein = ?, carbs = ?, fat = ?, meal_type = ?
        WHERE id = ?
    ''', (amount_g, cal, prot, carb, fat, meal_type, entry_id))
    conn.commit()
    conn.close()

def get_diary_entries(date_str=None):
    if not date_str:
        date_str = get_today_date()
    pid = get_active_profile_id()
    conn = get_db_connection()
    entries = conn.execute('SELECT * FROM diary WHERE date = ? AND profile_id = ? ORDER BY id DESC', (date_str, pid)).fetchall()
    conn.close()
    return [dict(e) for e in entries]

def delete_diary_entry(entry_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM diary WHERE id = ?', (entry_id,))
    conn.commit()
    conn.close()

# --- WATER METHODS ---
def add_water(amount_ml):
    pid = get_active_profile_id()
    date_str = get_today_date()
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO water_log (profile_id, date, amount_ml) VALUES (?, ?, ?)
    ''', (pid, date_str, amount_ml))
    conn.commit()
    conn.close()

def get_water_today():
    pid = get_active_profile_id()
    date_str = get_today_date()
    conn = get_db_connection()
    res = conn.execute('SELECT SUM(amount_ml) FROM water_log WHERE date = ? AND profile_id = ?', (date_str, pid)).fetchone()
    conn.close()
    return res[0] if res[0] else 0

# --- HISTORY METHODS ---
def get_historical_summary():
    pid = get_active_profile_id()
    conn = get_db_connection()
    
    diary = conn.execute('SELECT date, SUM(calories) as cal, SUM(protein) as prot, SUM(carbs) as carb, SUM(fat) as fat FROM diary WHERE profile_id = ? GROUP BY date', (pid,)).fetchall()
    water = conn.execute('SELECT date, SUM(amount_ml) as water FROM water_log WHERE profile_id = ? GROUP BY date', (pid,)).fetchall()
    
    conn.close()
    
    summary = {}
    for d in diary:
        summary[d['date']] = {
            'date': d['date'],
            'calories': d['cal'],
            'protein': d['prot'],
            'carbs': d['carb'],
            'fat': d['fat'],
            'water': 0
        }
    for w in water:
        if w['date'] not in summary:
            summary[w['date']] = {
                'date': w['date'],
                'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0,
                'water': w['water']
            }
        else:
            summary[w['date']]['water'] = w['water']
            
    result = list(summary.values())
    result.sort(key=lambda x: x['date'], reverse=True)
    return result

def delete_historical_day(date_str):
    pid = get_active_profile_id()
    conn = get_db_connection()
    conn.execute('DELETE FROM diary WHERE profile_id = ? AND date = ?', (pid, date_str))
    conn.execute('DELETE FROM water_log WHERE profile_id = ? AND date = ?', (pid, date_str))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully.")

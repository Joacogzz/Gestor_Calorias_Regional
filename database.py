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
        
    try:
        c.execute('CREATE INDEX IF NOT EXISTS idx_foods_name ON foods(name)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_foods_flags ON foods(is_favorite, is_regional, is_recipe)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_diary_date ON diary(date, profile_id)')
    except:
        pass
        
    conn.commit()
    conn.close()
    
    seed_regional_foods()

def reset_and_seed_foods(force=False):
    conn = get_db_connection()
    c = conn.cursor()
    
    if force:
        c.execute('DELETE FROM foods')
        conn.commit()

    c.execute('SELECT COUNT(*) FROM foods')
    count = c.fetchone()[0]
    if count > 0 and not force:
        conn.close()
        return

    # Catálogo curado: Alimentos comunes y habituales + Regionales de Misiones
    curated_foods = [
        # --- REGIONALES (Misiones) (is_regional = 1) ---
        ("Mandioca hervida", 160, 1.4, 38.0, 0.3, 1),
        ("Mandioca frita", 310, 1.2, 40.0, 16.0, 1),
        ("Chipa de almidón (chipa tradicional)", 320, 10.0, 40.0, 14.0, 1),
        ("Chipa guasú", 260, 9.0, 25.0, 14.0, 1),
        ("Caburé", 330, 11.0, 38.0, 15.0, 1),
        ("Reviro tradicional", 350, 6.0, 45.0, 18.0, 1),
        ("Reviro con huevo", 310, 9.0, 36.0, 15.0, 1),
        ("Mbeyú", 300, 5.0, 45.0, 12.0, 1),
        ("Sopa paraguaya", 260, 8.5, 23.0, 15.0, 1),
        ("Poroto negro hervido", 132, 8.9, 23.7, 0.5, 1),
        ("Bori bori (Vorí vorí)", 120, 10.0, 12.0, 4.0, 1),
        ("Torta frita", 380, 5.0, 48.0, 20.0, 1),
        ("Mate cocido con leche", 45, 2.2, 4.5, 2.0, 1),

        # --- BÁSICOS (is_regional = 0) ---
        ("Pechuga de pollo", 120, 23.0, 0.0, 2.5, 0),
        ("Milanesa de pollo al horno", 200, 18.0, 20.0, 6.0, 0),
        ("Milanesa de carne vacuna al horno", 220, 15.0, 22.0, 8.0, 0),
        ("Carne picada especial (magra)", 175, 26.0, 0.0, 7.5, 0),
        ("Carne picada común", 250, 18.0, 0.0, 19.0, 0),
        ("Bife de nalga / cuadril", 160, 28.0, 0.0, 5.0, 0),
        ("Costillita de cerdo magra", 190, 23.0, 0.0, 11.0, 0),
        ("Huevo entero", 143, 12.5, 0.7, 9.5, 0),
        ("Clara de huevo", 52, 11.0, 0.7, 0.2, 0),
        ("Arroz blanco", 360, 7.0, 80.0, 0.6, 0),
        ("Arroz integral", 350, 7.5, 76.0, 2.5, 0),
        ("Fideos secos", 350, 12.0, 70.0, 1.5, 0),
        ("Fideos secos integrales", 340, 13.5, 65.0, 2.5, 0),
        ("Avena tradicional", 389, 16.9, 66.3, 6.9, 0),
        ("Papa hervida", 87, 1.9, 20.0, 0.1, 0),
        ("Batata hervida", 86, 1.6, 20.0, 0.1, 0),
        ("Pan francés", 270, 9.0, 50.0, 3.0, 0),
        ("Pan de molde integral", 245, 9.5, 43.0, 3.5, 0),
        ("Leche descremada", 34, 3.4, 5.0, 0.1, 0),
        ("Leche entera", 61, 3.2, 4.8, 3.3, 0),
        ("Queso cremoso", 300, 14.0, 2.0, 25.0, 0),
        ("Queso muzzarella", 300, 22.0, 2.0, 22.0, 0),
        ("Yogur natural descremado", 45, 4.5, 6.0, 0.5, 0),
        ("Banana", 89, 1.1, 23.0, 0.3, 0),
        ("Manzana", 52, 0.3, 14.0, 0.2, 0),
        ("Naranja", 47, 0.9, 12.0, 0.1, 0),
        ("Tomate", 18, 0.9, 3.9, 0.2, 0),
        ("Zanahoria", 41, 0.9, 9.5, 0.2, 0),
        ("Cebolla", 40, 1.1, 9.3, 0.1, 0),
        ("Lechuga", 15, 1.4, 2.9, 0.2, 0),
        ("Aceite de girasol", 884, 0.0, 0.0, 100.0, 0),
        ("Aceite de oliva", 884, 0.0, 0.0, 100.0, 0),
        ("Manteca", 717, 0.8, 0.1, 81.0, 0),
    ]

    for f in curated_foods:
        c.execute('''
            INSERT INTO foods (name, calories_per_100g, protein_per_100g, carbs_per_100g, fat_per_100g, is_regional)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', f)
    conn.commit()
    conn.close()

def seed_regional_foods():
    reset_and_seed_foods(force=False)

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
def search_foods(query="", limit=100, offset=0, filter_type="ALL"):
    conn = get_db_connection()
    conditions = []
    params = []
    
    clean_query = query.strip() if query else ""
    if clean_query:
        conditions.append("name LIKE ?")
        params.append(f"%{clean_query}%")
        
    if filter_type == "REGIONAL":
        conditions.append("is_regional = 1")
    elif filter_type == "BASIC":
        conditions.append("is_regional = 0 AND is_recipe = 0")
    elif filter_type == "FAVORITES":
        conditions.append("is_favorite = 1")
    elif filter_type == "RECIPES":
        conditions.append("is_recipe = 1")
        
    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    if filter_type == "ALL":
        order_clause = "ORDER BY is_favorite DESC, name ASC"
    else:
        order_clause = "ORDER BY is_favorite DESC, is_regional DESC, name ASC"
    
    if limit is not None:
        sql = f"SELECT * FROM foods {where_clause} {order_clause} LIMIT ? OFFSET ?"
        params.extend([limit, offset])
    else:
        sql = f"SELECT * FROM foods {where_clause} {order_clause}"
        
    foods = conn.execute(sql, params).fetchall()
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
    try:
        amt = int(amount_ml)
        if amt <= 0:
            return
    except (ValueError, TypeError):
        return
    pid = get_active_profile_id()
    date_str = get_today_date()
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO water_log (profile_id, date, amount_ml) VALUES (?, ?, ?)
    ''', (pid, date_str, amt))
    conn.commit()
    conn.close()

def get_water_for_date(date_str=None):
    if not date_str:
        date_str = get_today_date()
    pid = get_active_profile_id()
    conn = get_db_connection()
    res = conn.execute('SELECT SUM(amount_ml) FROM water_log WHERE date = ? AND profile_id = ?', (date_str, pid)).fetchone()
    conn.close()
    return res[0] if res[0] else 0

def get_water_today():
    return get_water_for_date(get_today_date())

def delete_last_water_entry():
    pid = get_active_profile_id()
    date_str = get_today_date()
    conn = get_db_connection()
    row = conn.execute('SELECT id, amount_ml FROM water_log WHERE profile_id = ? AND date = ? ORDER BY id DESC LIMIT 1', (pid, date_str)).fetchone()
    if row:
        conn.execute('DELETE FROM water_log WHERE id = ?', (row['id'],))
        conn.commit()
        deleted_amount = row['amount_ml']
    else:
        deleted_amount = 0
    conn.close()
    return deleted_amount

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

# 🥗 Gestor de Calorías Regional

Aplicación multiplataforma (Escritorio y Móvil) diseñada para el control nutricional, conteo de macronutrientes y registro de hábitos saludables, con un enfoque e identidad gastronómica autóctona de la región del **Nordeste Argentino (NEA)**.

---

## 🌟 Características Principales

* **Base de Datos de Alimentos Regionales:** Incluye platos y alimentos tradicionales de la región (Chipa, Mbeyú, Reviro, Mandioca hervida/frita, Sopa Paraguaya, Chipa Guazú, etc.) junto a alimentos genéricos de consumo diario.
* **Cálculo Científico Personalizado:**
  * **Tasa Metabólica Basal (TMB):** Calculada mediante la fórmula de **Mifflin-St Jeor**.
  * **Gasto Energético Total Diario (TDEE):** Ajustado por nivel de actividad física (Sedentario hasta Actividad muy intensa).
  * **Ajuste por Objetivo:** Déficit calórico (pérdida de grasa), mantenimiento o superávit (ganancia muscular).
* **Gestor de Recetas Inteligente:**
  * Creación de recetas personalizadas combinando ingredientes.
  * Estimación de merma en cocción.
  * Fraccionamiento y registro automático en porciones.
* **Diario Nutricional y Seguimiento:**
  * Desglose por comidas (Desayuno, Almuerzo, Merienda, Cena, Snacks).
  * Monitoreo de hidratación diaria (agua en ml) y registro histórico de peso.
  * Visualización interactiva mediante gráficos circulares y de barras con límites de meta diarios.
* **Arquitectura Offline-First:** Toda la información se almacena localmente de forma segura en SQLite, permitiendo un uso fluido sin necesidad de conexión a internet.
* **Interfaz de Usuario:** Diseñada con una estética moderna, modo oscuro/claro y animaciones fluidas a 60/120 Hz.

---

## 🛠️ Tecnologías Utilizadas

* **Lenguaje:** [Python 3.12](https://www.python.org/)
* **Framework de Interfaz:** [Flet](https://flet.dev/) (basado en el motor de **Flutter**)
* **Base de Datos:** [SQLite3](https://www.sqlite.org/) (embebida)

---

## 🚀 Instalación y Ejecución

### 1. Clonar el repositorio:
```bash
git clone https://github.com/TU_USUARIO/Gestor_Calorias_Regional.git
cd Gestor_Calorias_Regional
```

### 2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

### 3. Ejecutar la aplicación:
```bash
python main.py
```

---

## 📁 Estructura del Proyecto

```text
Gestor_Calorias_Regional/
├── main.py            # Punto de entrada de la aplicación y navegación
├── database.py        # Capa de datos, consultas SQL y carga de alimentos
├── requirements.txt   # Dependencias de Python
├── assets/            # Recursos visuales e íconos de la aplicación
└── ui/                # Módulos y vistas de la interfaz de usuario
    ├── dashboard.py   # Pantalla principal con resumen diario y macros
    ├── diary.py       # Registro diario de comidas
    ├── recipes.py     # Creador y administrador de recetas
    ├── history.py     # Histórico semanal de consumo y agua
    ├── profile.py     # Gestión de perfiles y metas corporales
    ├── setup.py       # Configuración inicial / Onboarding
    └── theme.py       # Estilos globales y paleta de colores
```

---

## 👨‍💻 Autor

Proyecto desarrollado como parte de la **Práctica Profesional** en Informática.
* **Autor:** Axel Joaquín Gómez

# Gestor de Calorías Regional

Aplicación móvil (Android) desarrollada para el control nutricional, balance de macronutrientes y registro de hábitos alimenticios, con foco en comidas tradicionales y gastronomía autóctona de Argentina.

---

## Características Principales

* **Base de datos de alimentos regionales:** Incorpora platos tradicionales de la cocina autóctona (Chipa, Mbeyú, Reviro, Mandioca hervida/frita, Sopa Paraguaya, Chipa Guazú, entre otros) junto con alimentos genéricos y comerciales.
* **Cálculo metabólico:**
  * **Tasa Metabólica Basal (TMB):** Determinada mediante la ecuación de Mifflin-St Jeor en base a sexo, peso, altura y edad.
  * **Gasto Energético Total Diario (TDEE):** Ajustado según el factor de actividad física del usuario (desde nivel sedentario hasta actividad muy intensa).
  * **Ajuste por objetivo:** Adaptación calórica para pérdida de grasa, mantenimiento o superávit calórico orientado a hipertrofia.
* **Gestión de recetas:**
  * Combinación de ingredientes crudos.
  * Estimación de merma por cocción.
  * Fraccionamiento y registro automático en porciones.
* **Diario nutricional e hidratación:**
  * Registro por comidas (Desayuno, Almuerzo, Merienda, Cena, Snacks).
  * Registro de consumo de agua diario y evolución histórica de peso corporal.
  * Visualización de datos mediante gráficos circulares y de barras con metas límite.
* **Arquitectura Offline-First:** Almacenamiento local mediante SQLite3, garantizando funcionamiento autónomo sin requerir conexión a internet.
* **Interfaz:** Diseñada para dispositivos móviles con soporte para modo oscuro y claro nativo.

---

## Tecnologías Utilizadas

* **Lenguaje:** Python 3.12
* **Framework UI:** Flet (motor Flutter para Android)
* **Base de datos:** SQLite3 (embebida)

---

## Instalación y Ejecución

### 1. Clonar el repositorio:
```bash
git clone https://github.com/Joacogzz/Gestor_Calorias_Regional.git
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

## Estructura del Proyecto

```text
Gestor_Calorias_Regional/
├── main.py            # Punto de entrada y navegación
├── database.py        # Esquema de base de datos y consultas SQL
├── requirements.txt   # Dependencias del proyecto
├── assets/            # Recursos gráficos e íconos
└── ui/                # Módulos de la interfaz de usuario
    ├── dashboard.py   # Resumen diario y control de macronutrientes
    ├── diary.py       # Registro diario de alimentos
    ├── recipes.py     # Creación y administración de recetas
    ├── history.py     # Histórico de consumo semanal y agua
    ├── profile.py     # Perfil de usuario y parámetros metabólicos
    ├── setup.py       # Configuración inicial del usuario
    └── theme.py       # Definición de paleta de colores y estilos
```

---

## Autor

Proyecto desarrollado para Práctica Profesional de Analista en Sistemas.
* **Autor:** Axel Joaquín Gómez

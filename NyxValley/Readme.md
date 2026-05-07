# NyxValley
### Sistema de Reservación y Mapeo — Festival Internacional de las Luciérnagas 2026
**Equipo Ada** | Ingeniería de Software 2026-2 | Facultad de Ciencias, UNAM

---

## Tecnologías
- Python 3.13
- Django 6.0.1
- SQLite (desarrollo)
- HTMX
- HTML / CSS

---

## Configuración del proyecto (hacer una sola vez)

Sigue estos pasos **en orden** después de clonar el repositorio.

### 1. Clonar el repositorio
```bash
git clone https://github.com/AlanKevinCT/Ada.git
cd Ada/NyxValley
```

### 2. Activar el entorno de Conda
```bash
conda activate <<Tu entorno>>
```

### 3. Verificar que Django está instalado
```bash
django-admin --version
```
Si no aparece una versión, instálalo con:
```bash
pip install django
```

### 4. Aplicar las migraciones (crea tu base de datos local)
```bash
python manage.py migrate
```

### 5. Crear tu superusuario local
```bash
python manage.py createsuperuser
```
Llena los campos que te pida: correo, nombre, apellido paterno, apellido materno y contraseña.

### 6. Levantar el servidor
```bash
python manage.py runserver
```
Abre tu navegador en **http://127.0.0.1:8000**

---

## Estructura del proyecto
```bash
Ada/
├── NyxValley/              ← raíz del proyecto Django
│   ├── manage.py
│   ├── templates/          ← HTMLs globales
│   ├── static/             ← CSS, JS e imágenes
│   ├── media/              ← archivos subidos por usuarios
│   ├── Festival2026/       ← app principal
│   │   ├── models.py       ← Usuario, Parque, Reservacion
│   │   ├── views.py        ← lógica de cada página
│   │   ├── admin.py        ← panel de administración
│   │   └── migrations/     ← historial de cambios en la BD
│   └── NyxValley/
│       ├── settings.py     ← configuración general
│       └── urls.py         ← rutas del sistema
└── .gitignore
```

---

## Ramas de trabajo

| Rama | Responsable | Descripción |
|------|-------------|-------------|
| `main` | Todos | Código estable y revisado |
| `dev/backend` | Gera, Danna, Claudia | Modelos, vistas y lógica |
| `dev/frontend` | Mali | Templates y archivos estáticos |
| `dev/testing` | Alan | Pruebas unitarias e integración |

**Siempre crea tu rama desde `main` actualizado y haz Pull Request antes de mergear.**

---

## Mensajes de Commit Semánticos

Cada mensaje de commit debe seguir la convención de **Commits Convencionales**.  
El mensaje debe empezar con un tipo, seguido de una descripción concisa en español o inglés:

| Tipo | Cuándo usarlo |
|------|---------------|
| `feat` | Nueva funcionalidad |
| `fix` | Corrección de un error |
| `docs` | Cambios en documentación |
| `style` | Formato (espacios, comas, etc.) sin cambiar lógica |
| `refactor` | Cambio de código que no arregla bug ni agrega feature |
| `test` | Agregar o corregir pruebas |
| `chore` | Configuración, dependencias, tareas de build |

### Ejemplos
```bash
git commit -m "feat: agregar modelo de Reservacion con validacion de fechas"
git commit -m "fix: corregir restriccion de reservaciones en martes"
git commit -m "docs: actualizar README con instrucciones de instalacion"
git commit -m "chore: configurar settings.py con zona horaria Mexico"
```

---

## Notas importantes
- **Nunca subas `db.sqlite3` al repositorio** — cada quien tiene su base de datos local.
- **Nunca subas credenciales** — la `SECRET_KEY` del `settings.py` debe cambiarse antes de producción.
- Antes de hacer `push`, asegúrate de que `python manage.py migrate` corra sin errores.
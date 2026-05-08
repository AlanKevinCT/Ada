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
├── .gitignore
├── Readme.md                    ← descripción general del repo
└── NyxValley/                   ← raíz del proyecto Django
├── manage.py                    ← comando principal de Django
├── Readme.md                    ← este archivo
├── templates/                   ← HTMLs globales
├── static/                      ← CSS, JS e imágenes
├── media/                       ← archivos subidos por usuarios
├── Festival2026/                ← app principal del proyecto
│   ├── models.py                ← BD: clases Usuario, Parque, Reservacion
│   ├── views.py                 ← vistas de todas las páginas del mapa de navegación
│   ├── urls.py                  ← rutas del sistema (todas las URLs del proyecto)
│   ├── admin.py                 ← panel de administración de Django
│   ├── apps.py                  ← configuración de la app, conecta signals
│   ├── services.py              ← lógica de negocio: Autenticador, Disponibilidad, AsistReserva
│   ├── decorators.py            ← patrón Decorator: ServicioParque, ParqueBase, Cabanas
│   ├── signals.py               ← patrón Observer: correos y notificaciones automáticas
│   ├── mapa.py                  ← lógica del mapa interactivo
│   ├── tests.py                 ← pruebas unitarias e integración
│   └── migrations/              ← historial de cambios en la base de datos
│       └── 0001_initial.py      ← migración inicial con los 3 modelos
└── NyxValley/
├── settings.py              ← configuración general del proyecto
├── urls.py                  ← configuración de URLs del proyecto Django
├── wsgi.py                  ← despliegue en servidor
└── asgi.py                  ← despliegue asíncrono
```

---

### ¿Qué hace cada archivo nuevo?

**`services.py`** — Contiene la lógica de negocio principal:
- `Autenticador` — maneja el hash SHA-256 de contraseñas
- `Disponibilidad` — valida fechas del festival (junio-agosto), bloquea martes y verifica cupo
- `AsistReserva` — crea, cancela y modifica reservaciones con todas las validaciones

**`decorators.py`** — Implementa el patrón Decorator para los parques:
- `ServicioParque` — clase abstracta base
- `ParqueBase` — parque con zona de camping (todos los parques)
- `ParqueDecorator` — decorator base
- `Cabanas` — agrega servicio de cabañas al parque si el admin lo define

**`signals.py`** — Implementa el patrón Observer para notificaciones:
- `SignalCorreoCliente` — manda correos al cliente al reservar, cancelar o modificar
- `SignalModificacion` — notifica a clientes afectados cuando un parque cambia o se elimina
- Se dispara automáticamente al crear una reservación — no hay que llamarlo manualmente

**`mapa.py`** — Lógica del mapa interactivo:
- `MapaNavegacion` — carga parques activos con coordenadas, devuelve info por pin y exporta GeoJSON para Leaflet/Google Maps

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
- Si agregas un modelo nuevo o modificas uno existente, siempre corre `python manage.py makemigrations` antes de `migrate`.
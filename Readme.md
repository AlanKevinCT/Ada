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
### 2. Instalar gettext
```bash
sudo dnf install gettext
```
En este proyecto se utiliza gettext para manejar el sistema multi-idioma.

### 3. Activar el entorno de Conda
```bash
conda activate <<Tu entorno>>
```

### 4. Verificar que Django está instalado e instalar dependencias
```bash
django-admin --version
```
Si no aparece una versión, instálalo con:
```bash
pip install django
```

Ahora instalamos las dependecias de nuestro proyecto
```bash
pip install -r requirements.txt
```

### 5. Aplicar las migraciones (crea tu base de datos local)
```bash
python manage.py migrate
```

### 6. Crear tu superusuario local
```bash
python manage.py createsuperuser
```
Llena los campos que te pida: correo, nombre, apellido paterno, apellido materno y contraseña.

### 7. Compilar las traducciones del proyecto
```bash
python manage.py compilemessages
```

### 8. Levantar el servidor
```bash
python manage.py runserver
```
Abre tu navegador en **http://127.0.0.1:8000**

### 9. Ejecutar pruebas
para ejecutar toda la suit de pruebas:
```bash
python manage.py test Festival2026.tests
```
En caso que solo quieras ejecutar un conjunto en especifico:
```bash
python manage.py test Festival2026.tests.(nombre del archivo de pruebas)

Ejemplo:
python manage.py test Festival2026.tests.test_services
```

---

## Estructura del proyecto
```bash
Ada/
├── .gitignore
├── Readme.md                        ← descripción general del repo
└── NyxValley/                       ← raíz del proyecto Django
    ├── manage.py                    ← comando principal de Django
    ├── Readme.md                    ← descripción general del repo
    ├── templates/                   ← HTMLs globales
    ├── static/                      ← CSS, JS e imágenes
    ├── media/                       ← archivos subidos por usuarios
    ├── Festival2026/                ← app principal del proyecto
    │   ├── models.py                ← BD: clases Usuario, Parque, Reservacion
    │   ├── views.py                 ← vistas de todas las páginas del mapa de navegación
    │   ├── admin.py                 ← panel de administración de Django
    │   ├── apps.py                  ← configuración de la app, conecta signals
    │   ├── services.py              ← lógica de negocio: Autenticador, Disponibilidad, AsistReserva
    │   ├── decorators.py            ← patrón Decorator: ServicioParque, ParqueBase, Cabanas
    │   ├── signals.py               ← patrón Observer: correos y notificaciones automáticas
    │   ├── mapa.py                  ← lógica del mapa interactivo
    │   └── tests/                   ← historial de cambios en la base de datos
    │       └── test_models.py       ← pruebas unitarias para los modelos
    │       └── test_services.py     ← pruebas unitarias para la lógica de negocio
    │       └── test_signals.py      ← pruebas de integracion para las señales.
    │       └── test_system.py       ← pruebas de sistema
    │       └── test_views.py        ← pruebas de integración
    │   └── migrations/              ← historial de cambios en la base de datos
    │       └── 0001_initial.py      ← migración inicial con los 3 modelos
    └── NyxValley/
        ├── settings.py              ← configuración general del proyecto
        ├── urls.py                  ← todas las rutas del sistema
        ├── wsgi.py                  ← despliegue en servidor
        └── asgi.py                  ← despliegue asíncrono
```

---

### ¿Qué hace cada archivo?

**`models.py`** — Define las tablas de la base de datos:
- `Usuario` — modelo base con correo como login, hash SHA-256 de contraseña
- `Parque` — información del parque, coordenadas para el mapa, tipo de hospedaje
- `Reservacion` — estancia de un cliente en un parque, con fechas y estado

**`views.py`** — Contiene todas las vistas del sistema organizadas por sección:
- Autenticación: `inicio`, `registro`, `login`, `logout`
- Panel cliente: `panel_cliente`, `mis_reservaciones`, `cancelar_reservacion`
- Mapa: `mapa`, `detalle_parque` — Ayros implementa estas
- Reservaciones: `formulario_reserva`, `confirmacion`
- Panel admin: `panel_admin`, `gestionar_reservaciones`, `consultar_reservas`, `crear_parque`, `editar_parque`, `eliminar_parque`

**`services.py`** — Lógica de negocio principal:
- `Autenticador` — maneja el hash SHA-256 de contraseñas
- `Disponibilidad` — valida fechas del festival (junio-agosto), bloquea martes y verifica cupo
- `AsistReserva` — crea, cancela y modifica reservaciones con todas las validaciones

**`decorators.py`** — Patrón Decorator para los parques:
- `ServicioParque` — clase abstracta base
- `ParqueBase` — parque con zona de camping (todos los parques)
- `ParqueDecorator` — decorator base
- `Cabanas` — agrega servicio de cabañas al parque si el admin lo define

**`signals.py`** — Patrón Observer para notificaciones automáticas:
- `SignalCorreoCliente` — manda correos al cliente al reservar, cancelar o modificar
- `SignalModificacion` — notifica a clientes afectados cuando un parque cambia o se elimina
- Se dispara automáticamente al crear una reservación, no hay que llamarlo manualmente

**`mapa.py`** — Lógica del mapa interactivo (Ayros):
- `MapaNavegacion` — carga parques activos con coordenadas, devuelve info por pin
- Exporta GeoJSON compatible con Leaflet y Google Maps API

**`NyxValley/urls.py`** — Todas las rutas del sistema:
- Autenticación: `/`, `/registro/`, `/login/`, `/logout/`
- Cliente: `/panel/`, `/mis-reservaciones/`, `/mis-reservaciones/cancelar/<id>/`
- Mapa: `/mapa/`, `/mapa/parque/<id>/`
- Reservaciones: `/reservar/`, `/reservar/confirmacion/`
- Admin: `/admin-panel/` y todas sus sub-rutas

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

from .autenticacion import (
    inicio,
    registro,
    login,
    logout,
)

from .mapa_interactivo import (
    mapa,
    detalle_parque,
    info_completa_parque,
)

from .reservaciones import (
    formulario_reserva,
    confirmacion,
)

from .cliente import (
    panel_cliente,
    mis_reservaciones,
    cancelar_reservacion,
)

from .admin import (
    panel_admin,
    consultar_reservas,
    crear_parque,
    editar_parque,
    eliminar_parque,
)
from .autenticacion import (
    inicio,
    registro,
    login,
    logout,
    enviar_bienvenida,
)

from .mapa import (
    mapa,
    detalle_parque,
    info_completa_parque,
)

from .reservaciones import (
    formulario_reserva,
    confirmacion,
    cancelar_reservacion,
)

from .cliente import (
    panel_cliente,
    mis_reservaciones,
)

from .admin import (
    panel_admin,
    gestionar_reservaciones,
    consultar_reservas,
    crear_parque,
    editar_parque,
    eliminar_parque,
)
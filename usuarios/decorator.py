from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def requiere_permiso(codigo_permiso):
    """
    codigo_permiso, ej: 'facturas.add_factura', 'inventario.delete_producto'
    """
    def decorador(vista):
        @login_required
        @wraps(vista)
        def envoltura(request, *args, **kwargs):
            if not request.user.has_perm(codigo_permiso):
                raise PermissionDenied
            return vista(request, *args, **kwargs)
        return envoltura
    return decorador
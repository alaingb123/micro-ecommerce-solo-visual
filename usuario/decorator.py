from functools import wraps
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse


def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            user_rol = request.user.usuario.rol.nombre
            if user_rol in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                # Redireccionar a una página de error o mostrar un mensaje de acceso denegado
                return HttpResponse("Acceso denegado")
        return wrapped_view
    return decorator

"""Filtros de plantilla para consultar el rol del usuario desde el HTML."""

from django import template
from usuarios.decorator import requiere_permiso

register = template.Library()


@register.filter
def is_gestor(user):
    """Filtro para plantillas: {% if user|is_gestor %} ... {% endif %}."""
    return user.is_authenticated and (user.is_superuser or user.groups.filter(name='Gestor').exists())
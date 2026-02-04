from django import template
from ..models import SpeedRun

register = template.Library()
@register.simple_tag
def total_runs():
    return SpeedRun.verified_runs.count()
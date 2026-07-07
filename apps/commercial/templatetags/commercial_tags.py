from django import template

register = template.Library()


@register.filter(name='field_label')
def field_label(form, field_name):
    """Return the label of a form field by its name."""
    try:
        return form.fields[field_name].label or field_name
    except (KeyError, AttributeError):
        return field_name

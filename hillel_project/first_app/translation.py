from modeltranslation.translator import TranslationOptions, register

from first_app.models import Position, Department

@register(Department)
class DepartmentTranslationOptions(TranslationOptions):
    fields = ("name", "parent_department",)

@register(Position)
class PositionTranslationOption(TranslationOptions):
    fields = ("title", "description", "monthly_rate", "department",)

from django import forms
from .models import Badge


# =========================
# BADGE CREATION FORM
# =========================
class BadgeForm(forms.ModelForm):
    """
    RULES:
    - shop → requires price
    - automatic → requires event threshold
    """

    class Meta:
        model = Badge
        fields = [
            "name",
            "description",
            "icon",
            "acquisition_type",
            "shop_price",
            "required_events"
        ]

    def clean(self):
        cleaned_data = super().clean()

        acquisition_type = cleaned_data.get("acquisition_type")
        shop_price = cleaned_data.get("shop_price")
        required_events = cleaned_data.get("required_events")

        # =========================
        # SHOP RULE
        # =========================
        if acquisition_type == "shop":
            if not shop_price:
                self.add_error("shop_price", "Shop badges require a price.")
            cleaned_data["required_events"] = None

        # =========================
        # AUTOMATIC RULE
        # =========================
        if acquisition_type == "automatic":
            if not required_events:
                self.add_error(
                    "required_events",
                    "Automatic badges require event threshold."
                )
            cleaned_data["shop_price"] = None

        return cleaned_data
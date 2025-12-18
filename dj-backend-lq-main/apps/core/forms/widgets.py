from unfold.widgets import UnfoldAdminTextareaWidget


class AutoResizingTextarea(UnfoldAdminTextareaWidget):
    def __init__(self, attrs=None):
        default_attrs = {
            "rows": 1,
            "style": "resize: vertical; max-height: 200px; overflow: auto;",
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)

    def render(self, name, value, attrs=None, renderer=None):
        if value:
            attrs = attrs or {}
            attrs["rows"] = 3
        return super().render(name, value, attrs, renderer)

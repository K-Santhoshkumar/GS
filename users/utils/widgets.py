from django.forms.widgets import ClearableFileInput


class SimpleFileInput(ClearableFileInput):
    template_name = "users/widgets/simple_file_input.html"

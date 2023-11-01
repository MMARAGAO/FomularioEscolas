from django.apps import AppConfig

class AppNameConfig(AppConfig):  # Replace 'YourAppName' with the name of your app
    name = 'app'  # This should match the name of your app. If your app is named differently, update this string.

    def ready(self):
        # Import the signals module so that signals are connected
        from . import signals

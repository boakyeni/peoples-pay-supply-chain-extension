"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""


# activate_this = r'C:\Apache4Django\htdocs\peoples_supply\venv\Scripts\activate_this.py'
# exec(compile(open(activate_this, "rb").read(), activate_this, "exec"), dict(__file__=activate_this))

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()

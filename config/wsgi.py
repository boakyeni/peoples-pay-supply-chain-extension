"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""


# activate_this = r'C:\Apache4Django\htdocs\peoples-pay-supply-chain-extension\venv\Scripts\activate_this.py'
# exec(compile(open(activate_this, "rb").read(), activate_this, "exec"), dict(__file__=activate_this))

import os
import sys


# python_home = 'C:/Apache4Django/htdocs/peoples-pay-supply-chain-extension/venv'

# # Activate the virtual environment
# activate_this = os.path.join(python_home, 'Scripts', 'activate_this.py')
# with open(activate_this, "rb") as file_:
#     exec(compile(file_.read(), activate_this, 'exec'), dict(__file__=activate_this))



"""
FOR WINDOWS ONLY
"""
# sys.path.insert(0, 'C:/Apache4Django/htdocs/peoples-pay-supply-chain-extension/venv/Lib/site-packages')

# sys.path.append('C:/Apache4Django/htdocs/peoples-pay-supply-chain-extension')

"""
FOR WINDOWS ONLY ^^^ UNCOMMENT ON WINDOWS ^^^^
"""

# sys.path.append('C:/Apache4Django/htdocs/peoples-pay-supply-chain-extension/config')

from django.core.wsgi import get_wsgi_application

os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"

application = get_wsgi_application()


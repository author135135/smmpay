from .settings import DEBUG

if DEBUG is True:
    try:
        from .settings_dev import *
    except ImportError:
        from .settings import *
else:
    try:
        from .settings_prod import *
    except ImportError:
        from .settings import *

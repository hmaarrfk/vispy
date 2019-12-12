import os

try:
    import PyQt4
    import qtpy
except Exception as exp:
    # Fail: this backend cannot be used
    available, testable, why_not, which = False, False, str(exp), None
finally:
    pass

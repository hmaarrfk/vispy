import os

try:
    from PySide import QtCore
    import qtpy
    available, testable, why_not = True, True, None
    has_uic = False
    which = ('PyQt5', QtCore.PYQT_VERSION_STR, QtCore.QT_VERSION_STR)
except Exception as exp:
    # Fail: this backend cannot be used
    available, testable, why_not, which = False, False, str(exp), None
finally:
    pass

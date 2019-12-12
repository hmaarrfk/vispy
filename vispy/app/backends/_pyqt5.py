try:
    from PyQt5 import QtCore
    import qtpy

    assert qtpy.API == 'pyqt5'
    available, testable, why_not = True, True, None
    has_uic = True
    which = ('PyQt5', QtCore.PYQT_VERSION_STR, QtCore.QT_VERSION_STR)
except Exception as exp:
    # Fail: this backend cannot be used
    available, testable, why_not, which = False, False, str(exp), None
finally:
    pass

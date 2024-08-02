# coding=utf-8
"""DockWidget test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tea5209@psu.edu'
__date__ = '2024-08-01'
__copyright__ = 'Copyright 2024, Geoinformation and Big Data Research Laboratory (GIBD)'

import unittest

from qgis.PyQt.QtGui import QDockWidget

from AGGRA_dockwidget import AGGRADockWidget

from utilities import get_qgis_app

QGIS_APP = get_qgis_app()


class AGGRADockWidgetTest(unittest.TestCase):
    """Test dockwidget works."""

    def setUp(self):
        """Runs before each test."""
        self.dockwidget = AGGRADockWidget(None)

    def tearDown(self):
        """Runs after each test."""
        self.dockwidget = None

    def test_dockwidget_ok(self):
        """Test we can click OK."""
        pass

if __name__ == "__main__":
    suite = unittest.makeSuite(AGGRADialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)


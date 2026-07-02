import os
import sys

PLUGIN_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

if PLUGIN_DIR not in sys.path:
    sys.path.insert(0, PLUGIN_DIR)


def classFactory(iface):
    from qgis_cajander_matrix.main import CajanderPlugin

    return CajanderPlugin(iface)

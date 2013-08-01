Flightplan loader plugin for X-Plane 10 v1.0.0
===================================================

This plugin let you type your flight plan into the FMS.
Just open the loader window and type the waypoints of your flight plan.
For example, to the flight plan from LIMF to LIRJ type

	LIMF TOP LAGEN UNITA KONER MAURO LIRJ

You can also type a custom fix by typing its latitude and logitude.
For example, to add the point at N45.67°/E8.30° between LAGEN and UNITA, type

	LIMF TOP LAGEN N04567E00830 UNITA KONER MAURO LIRJ

The plugin is written in Python so you need Sandy Barbour's Python Interface plugin available at http://xpluginsdk.org/ installed in X-Plane 10.

This file works in both 32 and 64 bit version of X-Plane.

Installation
------------

Copy "PI_FMSLoader.py" in the "X-Plane 10/Resources/plugins/PythonScripts" folder.
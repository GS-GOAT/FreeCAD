# ***************************************************************************
# *   Copyright (c) 2009, 2010 Yorik van Havre <yorik@uncreated.net>        *
# *   Copyright (c) 2009, 2010 Ken Cline <cline@frii.com>                   *
# *   Copyright (c) 2020 Eliud Cabrera Castillo <e.cabrera-castillo@tum.de> *
# *   Copyright (c) 2022 FreeCAD Project Association                        *
# *                                                                         *
# *   This file is part of the FreeCAD CAx development system.              *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   FreeCAD is distributed in the hope that it will be useful,            *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with FreeCAD; if not, write to the Free Software        *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************
"""Provides GUI tools to activate the different snapping methods."""
## @package gui_snaps
# \ingroup draftguitools
# \brief Provides GUI tools to activate the different snapping methods.

## \addtogroup draftguitools
# @{
from PySide import QtGui, QtCore
from PySide.QtCore import QT_TRANSLATE_NOOP
import FreeCAD
import FreeCADGui as Gui
import draftguitools.gui_base as gui_base
from draftguitools.gui_trackers import Tracker, SnapTracker  # Import SnapTracker from gui_trackers

from draftutils.messages import _log
from draftutils.translate import translate


class Draft_Snap_Base():
    """Base Class inherited by all Draft Snap commands."""

    def Activated(self, status=0):
        # _log("GuiCommand: {}".format(self.__class__.__name__))

        if hasattr(Gui, "Snapper"):
            Gui.Snapper.toggle_snap(self.__class__.__name__[11:], bool(status))

    def IsActive(self):
        return hasattr(Gui, "Snapper") and Gui.Snapper.isEnabled("Lock")

    def isChecked(self):
        """Return true if the given snap is active in Snapper."""
        return hasattr(Gui, "Snapper") and self.__class__.__name__[11:] in Gui.Snapper.active_snaps

    def toggleSnapMode(self, mode, status):
        """
        Toggle snap modes efficiently without redundant updates.
        """
        if not hasattr(Gui, "Snapper"):
            FreeCAD.Console.PrintError("Error: Gui.Snapper is missing. Cannot toggle snap mode.\n")
            return
        
        # Ensure snap_modes exists before checking state
        if not hasattr(Gui.Snapper, "snap_modes") or Gui.Snapper.snap_modes is None:
            FreeCAD.Console.PrintError("Error: Gui.Snapper.snap_modes is missing. Cannot check snap state.\n")
            return 

        Gui.Snapper.toggle_snap(mode, bool(status))


class Draft_Snap_Lock(Draft_Snap_Base):
    """GuiCommand for the Draft_Snap_Lock tool."""

    def __init__(self):
        self.tracker = SnapTracker()  # Use the existing SnapTracker

    def GetResources(self):
        return {
            "Pixmap": "Draft_Snap_Lock",
            "Accel": "Shift+S",
            "MenuText": QT_TRANSLATE_NOOP("Draft_Snap_Lock", "Snap lock"),
            "ToolTip": QT_TRANSLATE_NOOP("Draft_Snap_Lock", "Enables or disables snapping globally."),
            "CmdType": "NoTransaction",
            "Checkable": self.isChecked()
        }

    def Activated(self, status=0):
        super().Activated(status)
        if status:
            self.toggleSnapMode("Lock", True)
            self.tracker.start_tracking()  # Start tracking when activated
        else:
            self.toggleSnapMode("Lock", False) 
            self.tracker.stop_tracking()  # Stop tracking when deactivated

    def IsActive(self):
        return self.tracker.is_active()  # Check if the tracker is active


try:
    Gui.addCommand("Draft_Snap_Lock", Draft_Snap_Lock())
except AttributeError:
    FreeCAD.Console.PrintError("Warning: Draft_Snap_Lock command missing.\n")


class Draft_Snap_Midpoint(Draft_Snap_Base):
    """GuiCommand for the Draft_Snap_Midpoint tool."""

    def GetResources(self):
        return {"Pixmap":    "Draft_Snap_Midpoint",
                "MenuText":  QT_TRANSLATE_NOOP("Draft_Snap_Midpoint", "Snap midpoint"),
                "ToolTip":   QT_TRANSLATE_NOOP("Draft_Snap_Midpoint", "Snaps to the midpoint of edges."),
                "CmdType":   "NoTransaction",
                "Checkable": self.isChecked()}


Gui.addCommand("Draft_Snap_Midpoint", Draft_Snap_Midpoint())


class Draft_Snap_Perpendicular(Draft_Snap_Base):
    """GuiCommand for the Draft_Snap_Perpendicular tool."""

    def GetResources(self):
        return {"Pixmap":    "Draft_Snap_Perpendicular",
                "MenuText":  QT_TRANSLATE_NOOP("Draft_Snap_Perpendicular", "Snap perpendicular"),
                "ToolTip":   QT_TRANSLATE_NOOP("Draft_Snap_Perpendicular", "Snaps to the perpendicular points on faces and edges."),
                "CmdType":   "NoTransaction",
                "Checkable": self.isChecked()}


Gui.addCommand("Draft_Snap_Perpendicular", Draft_Snap_Perpendicular())


class Draft_Snap_Grid(Draft_Snap_Base):
    """GuiCommand for the Draft_Snap_Grid tool."""

    def GetResources(self):
        return {"Pixmap":    "Draft_Snap_Grid",
                "MenuText":  QT_TRANSLATE_NOOP("Draft_Snap_Grid", "Snap grid"),
                "ToolTip":   QT_TRANSLATE_NOOP("Draft_Snap_Grid", "Snaps to the intersections of grid lines."),
                "CmdType":   "NoTransaction",
                "Checkable": self.isChecked()}


Gui.addCommand("Draft_Snap_Grid", Draft_Snap_Grid())


class Draft_Snap_Intersection(Draft_Snap_Base):
    """GuiCommand for the Draft_Snap_Intersection tool."""

    def GetResources(self):
        return {"Pixmap":    "Draft_Snap_Intersection",
                "MenuText":  QT_TRANSLATE_NOOP("Draft_Snap_Intersection", "Snap intersection"),
                "ToolTip":   QT_TRANSLATE_NOOP("Draft_Snap_Intersection", "Snaps to the intersection of two edges."),
                "CmdType":   "NoTransaction",
                "Checkable": self.isChecked()}


Gui.addCommand("Draft_Snap_Intersection", Draft_Snap_Intersection())


class Draft_Snap_Parallel(Draft_Snap_Base):
    """GuiCommand for the Draft_Snap_Parallel tool."""

    def GetResources(self):
        return {"Pixmap":    "Draft_Snap_Parallel",
                "MenuText":  QT_TRANSLATE_NOOP("Draft_Snap_Parallel", "Snap parallel"),
                "ToolTip":   QT_TRANSLATE_NOOP("Draft_Snap_Parallel", "Snaps to an imaginary line parallel to straight edges."),
                "CmdType":   "NoTransaction",
                "Checkable": self.isChecked()}


Gui.addCommand("Draft_Snap_Parallel", Draft_Snap_Parallel())


class Draft_Snap_Endpoint(Draft_Snap_Base):
    """GuiCommand for the Draft_Snap_Endpoint tool."""

    def GetResources(self):
        return {"Pixmap":    "Draft_Snap_Endpoint",
                "MenuText":  QT_TRANSLATE_NOOP("Draft_Snap_Endpoint", "Snap endpoint"),
                "ToolTip":   QT_TRANSLATE_NOOP("Draft_Snap_Endpoint", "Snaps to the endpoints of edges."),
                "CmdType":   "NoTransaction",
                "Checkable": self.isChecked()}


Gui.addCommand("Draft_Snap_Endpoint", Draft_Snap_Endpoint())


class Draft_Snap_Angle(Draft_Snap_Base):
    """GuiCommand for the Draft_Snap_Angle tool."""

    def GetResources(self):
        return {"Pixmap":    "Draft_Snap_Angle",
                "MenuText":  QT_TRANSLATE_NOOP("Draft_Snap_Angle", "Snap angle"),
                "ToolTip":   QT_TRANSLATE_NOOP("Draft_Snap_Angle", "Snaps to the special cardinal points on circular edges, at multiples of 30° and 45°."),
                "CmdType":   "NoTransaction",
                "Checkable": self.isChecked()}


Gui.addCommand("Draft_Snap_Angle", Draft_Snap_Angle())


class Draft_Snap_Center(Draft_Snap_Base):
    """GuiCommand for the Draft_Snap_Center tool."""

    def GetResources(self):
        return {"Pixmap":    "Draft_Snap_Center",
                "MenuText":  QT_TRANSLATE_NOOP("Draft_Snap_Center", "Snap center"),
                "ToolTip":   QT_TRANSLATE_NOOP("Draft_Snap_Center", "Snaps to the center point of faces and circular edges, and to the Placement point of Working Plane Proxies and Building Parts."),
                "CmdType":   "NoTransaction",
                "Checkable": self.isChecked()}


Gui.addCommand("Draft_Snap_Center", Draft_Snap_Center())


class Draft_Snap_Extension(Draft_Snap_Base):
    """GuiCommand for the Draft_Snap_Extension tool."""

    def GetResources(self):
        return {"Pixmap":    "Draft_Snap_Extension",
                "MenuText":  QT_TRANSLATE_NOOP("Draft_Snap_Extension", "Snap extension"),
                "ToolTip":   QT_TRANSLATE_NOOP("Draft_Snap_Extension", "Snaps to an imaginary line that extends beyond the endpoints of straight edges."),
                "CmdType":   "NoTransaction",
                "Checkable": self.isChecked()}


Gui.addCommand("Draft_Snap_Extension", Draft_Snap_Extension())


class Draft_Snap_Near(Draft_Snap_Base):
    """GuiCommand for the Draft_Snap_Near tool."""

    def GetResources(self):
        return {"Pixmap":    "Draft_Snap_Near",
                "MenuText":  QT_TRANSLATE_NOOP("Draft_Snap_Near", "Snap near"),
                "ToolTip":   QT_TRANSLATE_NOOP("Draft_Snap_Near", "Snaps to the nearest point on faces and edges."),
                "CmdType":   "NoTransaction",
                "Checkable": self.isChecked()}


Gui.addCommand("Draft_Snap_Near", Draft_Snap_Near())


class Draft_Snap_Ortho(Draft_Snap_Base):
    """GuiCommand for the Draft_Snap_Ortho tool."""

    def GetResources(self):
        return {"Pixmap":    "Draft_Snap_Ortho",
                "MenuText":  QT_TRANSLATE_NOOP("Draft_Snap_Ortho", "Snap ortho"),
                "ToolTip":   QT_TRANSLATE_NOOP("Draft_Snap_Ortho", "Snaps to imaginary lines that cross the previous point at multiples of 45°."),
                "CmdType":   "NoTransaction",
                "Checkable": self.isChecked()}


Gui.addCommand("Draft_Snap_Ortho", Draft_Snap_Ortho())


class Draft_Snap_Special(Draft_Snap_Base):
    """GuiCommand for the Draft_Snap_Special tool."""

    def GetResources(self):
        return {"Pixmap":    "Draft_Snap_Special",
                "MenuText":  QT_TRANSLATE_NOOP("Draft_Snap_Special", "Snap special"),
                "ToolTip":   QT_TRANSLATE_NOOP("Draft_Snap_Special", "Snaps to special points defined by the object."),
                "CmdType":   "NoTransaction",
                "Checkable": self.isChecked()}


Gui.addCommand("Draft_Snap_Special", Draft_Snap_Special())


class Draft_Snap_Dimensions(Draft_Snap_Base):
    """GuiCommand for the Draft_Snap_Dimensions tool."""

    def GetResources(self):
        return {"Pixmap":    "Draft_Snap_Dimensions",
                "MenuText":  QT_TRANSLATE_NOOP("Draft_Snap_Dimensions", "Snap dimensions"),
                "ToolTip":   QT_TRANSLATE_NOOP("Draft_Snap_Dimensions", "Shows temporary X and Y dimensions."),
                "CmdType":   "NoTransaction",
                "Checkable": self.isChecked()}


Gui.addCommand("Draft_Snap_Dimensions", Draft_Snap_Dimensions())


class Draft_Snap_WorkingPlane(Draft_Snap_Base):
    """GuiCommand for the Draft_Snap_WorkingPlane tool."""

    def GetResources(self):
        return {"Pixmap":    "Draft_Snap_WorkingPlane",
                "MenuText":  QT_TRANSLATE_NOOP("Draft_Snap_WorkingPlane", "Snap working plane"),
                "ToolTip":   QT_TRANSLATE_NOOP("Draft_Snap_WorkingPlane", "Projects snap points onto the current working plane."),
                "CmdType":   "NoTransaction",
                "Checkable": self.isChecked()}


Gui.addCommand("Draft_Snap_WorkingPlane", Draft_Snap_WorkingPlane())


class ShowSnapBar(Draft_Snap_Base):
    """GuiCommand for the Draft_ShowSnapBar tool."""

    def GetResources(self):
        return {"Pixmap":    "Draft_Snap",
                "MenuText":  QT_TRANSLATE_NOOP("Draft_ShowSnapBar", "Show snap toolbar"),
                "ToolTip":   QT_TRANSLATE_NOOP("Draft_ShowSnapBar", "Shows the snap toolbar if it is hidden."),
                "CmdType":   "NoTransaction"}

    def Activated(self):
        """Execute when the command is called."""
        if hasattr(Gui, "Snapper"):
            toolbar = Gui.Snapper.get_snap_toolbar()
            if toolbar is not None:
                toolbar.show()


Gui.addCommand('Draft_ShowSnapBar', ShowSnapBar())

## @}

def keyPressEvent(self, event):
    key = event.key()

    # Ensure tracker is initialized before using it
    if not hasattr(self, "tracker") or self.tracker is None:
        FreeCAD.Console.PrintError("Error: Tracker is missing. Cannot process input.\n")
        event.accept()
        return

    if key == QtCore.Qt.Key_Q:
        # Set the hold point using the current snap point
        if self.currentSnapPoint is not None:
            self.tracker.setHoldPoint(self.currentSnapPoint)
            FreeCAD.Console.PrintMessage(f"Hold point set to: {self.currentSnapPoint}\n")
        event.accept()
        return

    elif key == QtCore.Qt.Key_Escape:
        # Clear the hold point
        self.tracker.clearHoldPoint()
        FreeCAD.Console.PrintMessage("Hold point cleared.\n")
        event.accept()
        return

    elif QtCore.Qt.Key_0 <= key <= QtCore.Qt.Key_9:
        if not self.tracker.holdPoint:
            event.accept()  
            return

        digit = event.text()
        if not digit.isdigit():
            FreeCAD.Console.PrintError(f"Invalid numeric input ignored: {digit}\n")
            event.accept()
            return

        # Directions only calculated for first digit and the rest only updates number
        if self.tracker.inputDistance is None:
            self.tracker.processNumericInput(digit)

            if self.tracker.holdPoint and self.currentSnapPoint:
                direction = self.currentSnapPoint - self.tracker.holdPoint
                wp = self.tracker._get_wp()
                direction_local = wp.get_local_rotation().multVec(direction)
                self.tracker.locked_dir_vector = self.tracker.get_orthogonal_direction(direction_local)
        else:
            self.tracker.processNumericInput(digit)  #Only updates number, not direction

        event.accept()
        return
    
    elif key in (QtCore.Qt.Key_Backspace, QtCore.Qt.Key_Delete):
        if self.tracker.inputDistance:
            self.tracker.inputDistance = self.tracker.inputDistance[:-1] # Remove last char
            self.tracker.updateTracking() # Update tracker after correction
            FreeCAD.Console.PrintMessage("Numeric input backspaced. Current input: {}\n".format(self.tracker.inputDistance)) # Optional feedback
        event.accept()
        return

    elif key in (QtCore.Qt.Key_Period, QtCore.Qt.Key_Comma):
        # Accept decimal separator (convert comma to dot if necessary)
        self.tracker.processNumericInput(".")
        event.accept()
        return

    elif key in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
        # Ensure tracker has valid input before committing
        if not self.tracker.inputDistance or self.tracker.inputDistance.strip() == "":
            FreeCAD.Console.PrintError("No valid numeric input. Press Escape to reset or enter a valid number.\n")
            event.accept()
            return

        # Proceed with committing valid input
        target = self.tracker.commitInput()
        if target is not None:
            FreeCAD.Console.PrintMessage(f"Geometry created at: {target}\n")

        event.accept()
        return

    # For any other key, invoke the default handler
    super().keyPressEvent(event)


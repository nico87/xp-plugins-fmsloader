from XPLMDefs import *
from XPLMProcessing import *
from XPLMDataAccess import *
from XPLMUtilities import *
from XPLMPlanes import *
from XPLMNavigation import *
from SandyBarbourUtilities import *
from PythonScriptMessaging import *
from XPLMPlugin import *
from XPLMMenus import *
from XPWidgetDefs import *
from XPWidgets import *
from XPStandardWidgets import *
import re

VERSION = "1.0.0"

class PythonInterface:
    def XPluginStart(self):
        self.Name = "FMS Loader - " + VERSION
        self.Sig = "claudionicolotti.xplane.fmsloader"
        self.Desc = "FMS Loader Tool"
        
        self.window = False
        self.ufmcPlansPath = False
        
        # Main menu
        self.Cmenu = self.mmenuCallback
        self.mPluginItem = XPLMAppendMenuItem(XPLMFindPluginsMenu(), 'FMS Loader', 0, 1)
        self.mMain = XPLMCreateMenu(self, 'FMS Loader', XPLMFindPluginsMenu(), self.mPluginItem, self.Cmenu, 0)
        self.mNewPlan = XPLMAppendMenuItem(self.mMain, 'Insert plan', False, 1)
        
        return self.Name, self.Sig, self.Desc
    
    def XPluginStop(self):
        XPLMDestroyMenu(self, self.mMain)
        if (self.window):
            XPDestroyWidget(self, self.WindowWidget, 1)
        pass
        
    def XPluginEnable(self):
        return 1
    
    def XPluginDisable(self):
        pass
    
    def XPluginReceiveMessage(self, inFromWho, inMessage, inParam):
        pass
        
    def mmenuCallback(self, menuRef, menuItem):
        # Start/Stop menuitem
        if menuItem == self.mNewPlan:
            if (not self.window):
                self.CreateWindow(221, 640, 900, 45)
                self.window = True
            else:
                if(not XPIsWidgetVisible(self.WindowWidget)):
                    XPSetWidgetDescriptor(self.errorCaption, '')
                    XPShowWidget(self.WindowWidget)
            XPSetKeyboardFocus(self.routeInput)

    def CreateWindow(self, x, y, w, h):
        x2 = x + w
        y2 = y - h - 100
        Buffer = "FMS Loader"
        
        # Create the Main Widget window
        self.WindowWidget = XPCreateWidget(x, y, x2, y2, 1, Buffer, 1,    0, xpWidgetClass_MainWindow)
        
        # Config Sub Window, style
        subw = XPCreateWidget(x+10, y-30, x2-20 + 10, y2+40 -25, 1, "",  0,self.WindowWidget, xpWidgetClass_SubWindow)
        XPSetWidgetProperty(subw, xpProperty_SubWindowType, xpSubWindowStyle_SubWindow)
        x += 25
        y -= 20
        
        # Add Close Box decorations to the Main Widget
        XPSetWidgetProperty(self.WindowWidget, xpProperty_MainWindowHasCloseBoxes, 1)
        
        # Load route button
        self.RouteButton = XPCreateWidget(x2 - 150, y-50, x2-70, y-72, 1, "To XP FMC", 0, self.WindowWidget, xpWidgetClass_Button)

        x2 = 0

        XPSetWidgetProperty(self.RouteButton, xpProperty_ButtonType, xpPushButton)
        
        # Route input
        self.routeInput = XPCreateWidget(x+20, y-50, x+660, y-72, 1, "", 0, self.WindowWidget, xpWidgetClass_TextField)
        XPSetWidgetProperty(self.routeInput, xpProperty_TextFieldType, xpTextEntryField)
        XPSetWidgetProperty(self.routeInput, xpProperty_Enabled, 1)
        
        y -= 40
        
        # Error caption
        self.errorCaption = XPCreateWidget(x+20, y-70, x+300, y-90, 1, '', 0, self.WindowWidget, xpWidgetClass_Caption)
        
        # Register our widget handler
        self.WindowHandlerrCB = self.WindowHandler
        XPAddWidgetCallback(self, self.WindowWidget, self.WindowHandlerrCB)
        
        # set focus
        XPSetKeyboardFocus(self.routeInput)
        pass

    def WindowHandler(self, inMessage, inWidget, inParam1, inParam2):
        if (inMessage == xpMessage_CloseButtonPushed):
            if (self.window):
                XPHideWidget(self.WindowWidget)
            return 1

        # Handle any button pushes
        if (inMessage == xpMsg_PushButtonPressed):

            XPSetWidgetDescriptor(self.errorCaption, '')
            buff = []
            XPGetWidgetDescriptor(self.routeInput, buff, 256)
            param = buff[0].strip().split(' ')
                
            if (inParam1 == self.RouteButton and len(param) > 0):
                # Get te actual coordinates
                latDataRef = XPLMFindDataRef("sim/flightmodel/position/lat_ref")
                lonDataRef = XPLMFindDataRef("sim/flightmodel/position/lon_ref")
                lat = XPLMGetDataf(latDataRef)
                lon = XPLMGetDataf(lonDataRef)
                # Clear the current flight plan
                XPLMSetDestinationFMSEntry(0)
                XPLMSetDisplayedFMSEntry(0)
                for r in range(XPLMCountFMSEntries(), 0, -1):
                    XPLMClearFMSEntry(r)
                # Load the navaids
                i = 0
                pattern = re.compile('(N|S)([0-9]{5})(E|W)([0-9]{5})')
                for navaid in param:
                    result = pattern.match(navaid)
                    if (result):
                        # It's a custom point
                        lat = float(result.group(2)) / 100
                        if (result.group(1) == "S"):
                            lat = lat * -1
                        lon = float(result.group(4)) / 100
                        if (result.group(1) == "W"):
                            lon = lon * -1
                        XPLMSetFMSEntryLatLon(i, lat, lon, 0)
                        i += 1
                    else:
                        # It's a regular navaid
                        # NAVAID_TYPES = xplm_Nav_Airport + xplm_Nav_NDB + xplm_Nav_VOR + xplm_Nav_Fix + xplm_Nav_DME
                        type = xplm_Nav_Fix
                        if (len(navaid) == 4):
                            type = xplm_Nav_Airport
                        elif (len(navaid) == 3):
                            type = xplm_Nav_NDB + xplm_Nav_VOR + xplm_Nav_DME
                        nref = XPLMFindNavAid(None, navaid, lat, lon, None, type)
                        found = False
                        while (nref != XPLM_NAV_NOT_FOUND and not found):
                            # Get some infos
                            xlat = []
                            xlon = []
                            outID = []
                            XPLMGetNavAidInfo(nref, None, xlat, xlon, None, None, None, outID, None, None)
                            if (outID[0] == navaid):
                                lat = xlat[0]
                                lon = xlon[0]
                                XPLMSetFMSEntryInfo(i, nref, 0)        
                                found = True
                                i += 1
                            else:
                                SandyBarbourPrint("Navaid not found (1) " + navaid + " (" + outID[0] + " was found)")
                                nref = XPLMGetNextNavAid(nref)
                # Set destination
                XPLMSetDestinationFMSEntry(0)
                XPLMSetDisplayedFMSEntry(0)
                return 1
        return 0
        
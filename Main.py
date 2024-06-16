#!/usr/bin/env python3
import os
from Common import *
from XMLParser import *
from GATORRun import GatorCaller
from WidgetInfo import WidgetInfo
from androguard.core.androconf import load_api_specific_resource_module
from Mapping import get_mappings

if __name__ == '__main__':

    # GUI widgets extraction
    gatorCaller = GatorCaller()
    gatorCaller.start()

    # Codebase extraction
    parse_xml = XMLParser()
    parse_xml.start()
    widget_info = WidgetInfo()
    widget_info.start() 

    # Permission extraction
    permissionMap = load_api_specific_resource_module('api_permission_mappings')
    get_mappings(permissionMap)
#!/usr/bin/python
# -*- coding: cp1252 -*-
#
#Programmers:   Christian Kohl�ffel
#               Vinzenz Schulz
#
#Distributed under the terms of the GPL (GNU Public License)
#
#dxf2gcode is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 2 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


import Core.Globals as g

import re

import logging
logger = logging.getLogger("Core.LayerContent") 

class LayerContentClass:
    """
    The LayerContentClass is used for the definition of the shape order to 
    export and to store and change (GUI) the different export parameters. The
    LayerConentClasses for each Layer is stored in a list. This List Defines
    the order for Layers to be exported. 
    """
    def __init__(self, LayerNr=None, LayerName='', shapes=[]):
        """
        Initialization of the LayerContentClass. This is performed during the
        shapes creation in the main dxf2gcode.py file. 
        @param LayerNr: This parameter is forwarded from the dxf import
        @param LayerName: This parameter is forwarded from the dxf import
        @param shapes: This is a list which includes all shapes on the layer.
        """
        
        #Define Short Name for config.vars
        vars = g.config.vars
        
        self.type = "Layer"
        self.LayerNr = LayerNr
        self.LayerName = LayerName
        self.shapes = shapes
        self.exp_order = [] #used for shape order optimization, ... Only contains shapes
        self.exp_order_complete = [] #used for outputing the GCODE ; can contain shapes, custom gcode, ...

        #preset defaults
        self.axis3_slice_depth = vars.Depth_Coordinates['axis3_slice_depth']
        self.axis3_start_mill_depth = vars.Depth_Coordinates['axis3_start_mill_depth']
        self.axis3_mill_depth = vars.Depth_Coordinates['axis3_mill_depth']
        self.axis3_retract = vars.Depth_Coordinates['axis3_retract']
        self.axis3_safe_margin = vars.Depth_Coordinates['axis3_safe_margin']
        self.f_g1_plane = vars.Feed_Rates['f_g1_plane']
        self.f_g1_depth = vars.Feed_Rates['f_g1_depth']

        #Use default tool 1 (always exists in config)
        self.tool_nr = 1
        self.tool_diameter = vars.Tool_Parameters['1']['diameter']
        self.speed = vars.Tool_Parameters['1']['speed']
        self.start_radius = vars.Tool_Parameters['1']['start_radius']


        #search for layer commands to override defaults
        if self.LayerName.startswith("MILL:") or self.isBreakLayer():
            lopts_re = re.compile("([a-zA-Z]{1,10}:\s{0,}[\-\.0-9]{1,30}\s{0,})")
            #result = rcmp.search(self.LayerName)
            layer_commands = self.LayerName.replace(",", ".")
            
            for lc in lopts_re.findall(layer_commands):
                try:
                    name, value = lc.split(":")
                except ValueError:
                    continue

                if name in vars.Layer_Options['mill_depth_identifiers']:
                    self.axis3_mill_depth = float(value)

                if name in vars.Layer_Options['slice_depth_identifiers']:
                    self.axis3_slice_depth = float(value)
                
                if name in vars.Layer_Options['start_mill_depth_identifiers']:
                    self.axis3_start_mill_depth = float(value)
                
                if name in vars.Layer_Options['retract_identifiers']:
                    self.axis3_retract = float(value)
                
                if name in vars.Layer_Options['safe_margin_identifiers']:
                    self.axis3_safe_margin = float(value)

                if name in vars.Layer_Options['f_g1_plane_identifiers']:
                    self.f_g1_plane = float(value)
                
                if name in vars.Layer_Options['f_g1_depth_identifiers']:
                    self.f_g1_depth = float(value)

                if name in vars.Layer_Options['tool_nr_identifiers']:
                    self.tool_nr = float(value)
                
                if name in vars.Layer_Options['tool_diameter_identifiers']:
                    self.tool_diameter = float(value)

                if name in vars.Layer_Options['spindle_speed_identifiers']:
                    self.speed = float(value)
                
                if name in vars.Layer_Options['start_radius_identifiers']:
                    self.start_radius = float(value)
                

        
        
    def __cmp__(self, other):
        """
        This function just compares the LayerNr to sort the List of LayerContents
        @param other: This is the 2nd of the LayerContentClass to be compared.
        """
        return cmp(self.LayerNr, other.LayerNr)

    def __str__(self):
        """ 
        Standard method to print the object
        @return: A string
        """
        return ('\ntype:          %s' % self.type) +\
               ('\nLayerNr :      %i' % self.LayerNr) +\
               ('\nLayerName:     %s' % self.LayerName)+\
               ('\nshapes:        %s' % self.shapes)+\
               ('\nexp_order:     %s' % self.exp_order)+\
               ('\nexp_order_comp:%s' % self.exp_order_complete)+\
               ('\ntool_diameter: %i' % self.tool_nr)

    def should_ignore(self):
        return self.LayerName.startswith("IGNORE:") or self.isBreakLayer()
    
    def isBreakLayer(self):
        return self.LayerName.startswith("BREAKS:")
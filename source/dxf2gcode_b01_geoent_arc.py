#!/usr/bin/python
# -*- coding: cp1252 -*-
#
#dxf2gcode_b01_ent_polyline
#Programmer: Christian Kohl�ffel
#E-mail:     n/A
#
#Copyright 2008 Christian Kohl�ffel
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

from Canvas import Oval, Arc, Line
from math import sqrt, sin, cos, atan2, radians, degrees
from dxf2gcode_b01_point import PointClass, PointsClass, ArcGeo, ContourClass

class ArcClass:
    def __init__(self,Nr=0,caller=None):
        self.Typ='Arc'
        self.Nr = Nr
        self.Layer_Nr = 0
        self.length=0
        self.geo=None

        #Lesen der Geometrie
        self.Read(caller)

    def __str__(self):
        # how to print the object
        return("\nTyp: Arc ")+\
              ("\nNr: %i" %self.Nr)+\
              ("\nLayer Nr:%i" %self.Layer_Nr)+\
              str(self.geo)
    def reverse(self):
        self.geo.reverse()
    def App_Cont_or_Calc_IntPts(self, cont, points, i, tol):
        points.append(PointsClass(point_nr=len(points),geo_nr=i,\
                          Layer_Nr=self.Layer_Nr,\
                          be=self.geo.Pa,\
                          en=self.geo.Pe,\
                          be_cp=[],en_cp=[]))        
    
    def Read(self, caller):
        #K�rzere Namen zuweisen
        lp=caller.line_pairs

        #Layer zuweisen        
        s=lp.index_code(8,caller.start+1)
        self.Layer_Nr=caller.Get_Layer_Nr(lp.line_pair[s].value)
        #XWert
        s=lp.index_code(10,s+1)
        x0=float(lp.line_pair[s].value)
        #YWert
        s=lp.index_code(20,s+1)
        y0=float(lp.line_pair[s].value)
        O=PointClass(x0,y0)
        #Radius
        s=lp.index_code(40,s+1)
        r= float(lp.line_pair[s].value)
        #Start Winkel
        s=lp.index_code(50,s+1)
        s_ang= radians(float(lp.line_pair[s].value))
        #End Winkel
        s=lp.index_code(51,s+1)
        e_ang= radians(float(lp.line_pair[s].value))

        #Berechnen der Start und Endwerte des Arcs
        Pa=PointClass(x=cos(s_ang)*r,y=sin(s_ang)*r)+O
        Pe=PointClass(x=cos(e_ang)*r,y=sin(e_ang)*r)+O

        #Anh�ngen der ArcGeo Klasse f�r die Geometrie
        self.geo=ArcGeo(Pa=Pa,Pe=Pe,O=O,r=r,s_ang=s_ang,e_ang=e_ang,dir=1)

        #L�nge entspricht der L�nge des Kreises
        self.length=self.geo.length

        #Neuen Startwerd f�r die n�chste Geometrie zur�ckgeben        
        caller.start=s

    def plot2can(self,canvas,p0,sca,tag):
        hdl=self.geo.plot2can(canvas,p0,sca,tag)
        return hdl

    def get_start_end_points(self,direction):
        punkt,angle=self.geo.get_start_end_points(direction)
        return punkt,angle
    
    def Write_GCode(self,paras,sca,p0,dir,axis1,axis2):
        string=self.geo.Write_GCode(paras,sca,p0,dir,axis1,axis2)
        return string
            
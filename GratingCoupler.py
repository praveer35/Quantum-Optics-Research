import gdspy
import math
import os

################################################################
# Title:    GratingCoupler.java                                #
# Author:   Praveer Sharan                                     #
# Version:  10/24/2022 (v1)                                    #
# Description:                                                 #
#   A class that contains functions for generating .txt files  #
#   from .gds files with coordinates, generating .gds files    #
#   from .txt files, and generating .gds files from specified  #
#   measurements about the grating coupler.                    #
################################################################

class GratingCoupler:
    # initializes the GratingCoupler class
    def __init__(self):
        self.lib = gdspy.GdsLibrary()
        self.cell = self.lib.new_cell('FIRST')
    
    # returns True if polygon is a rectangle, else returns False
    def is_rectangle(self, pol):
        x_coord_check = False
        y_coord_check = False
        if (round(pol[0][0], 3) == round(pol[1][0], 3)):
            if (round(pol[2][0], 3) == round(pol[3][0], 3)):
                x_coord_check = True
        if (round(pol[0][0], 3) == round(pol[2][0], 3)):
            if (round(pol[1][0], 3) == round(pol[3][0], 3)):
                x_coord_check = True
        if (round(pol[0][0], 3) == round(pol[3][0], 3)):
            if (round(pol[1][0], 3) == round(pol[2][0], 3)):
                x_coord_check = True
        if (round(pol[0][1], 3) == round(pol[1][1], 3)):
            if (round(pol[2][1], 3) == round(pol[3][1], 3)):
                y_coord_check = True
        if (round(pol[0][1], 3) == round(pol[2][1], 3)):
            if (round(pol[1][1], 3) == round(pol[3][1], 3)):
                y_coord_check = True
        if (round(pol[0][1], 3) == round(pol[3][1], 3)):
            if (round(pol[1][1], 3) == round(pol[2][1], 3)):
                y_coord_check = True
        return (x_coord_check and y_coord_check)

    # returns a positive string of 3 decimal places from a decimal number
    def d_to_str(self, decimal):
        truncated_positive_decimal = round(decimal, 3)
        return str(truncated_positive_decimal)
    
    # generates a .txt file containing the coordinates of a .gds file
    def write_gds_to_txt(self, input_file, text_file, out=True):
        gdsii = gdspy.GdsLibrary(infile=input_file)
        coordFile = open(text_file, "w", -1)
        coordFile.truncate(0)
        main_cell = gdsii.top_level()[0]  # Assume a single top level cell
        for layer in range(16):
            for datatype in range(16):
                try:
                    pol_dict = main_cell.get_polygons(by_spec=True)
                    pol_list = pol_dict[(layer, datatype)]
                    for pol in pol_list:
                        coordFile.write("L:" + str(layer) + " D:" + str(datatype))
                        if (self.is_rectangle(pol)):
                            coordFile.write(" RECT x:" + self.d_to_str(pol[0][0]) + " y:" + self.d_to_str(pol[0][1]))
                            coordFile.write(" x:" + self.d_to_str(pol[2][0]) + " y:" + self.d_to_str(pol[2][1]) + "\n")
                        else:
                            coordFile.write(" POLY")
                            vertice = 0
                            while vertice < len(pol):
                                coordFile.write(" x:" + self.d_to_str(pol[vertice][0]) + " y:" + self.d_to_str(pol[vertice][1]))
                                vertice += 1
                            coordFile.write("\n")
                except:
                    print("", end="")
        if (out):
            print("Success in func write_gds_to_txt:", input_file, "written to", text_file + ".")
    
    # generates a .gds file using the coordinates in a .txt file
    def write_txt_to_gds(self, output_file, text_file, out=True):
        coordFile = open(text_file, "r", -1)
        lines = coordFile.readlines()
        for line in lines:
            data = line.strip().split(" ")
            layer = int(data[0][2:])
            datatype = int(data[1][2:])
            if (data[2] == "RECT"):
                rect = gdspy.Rectangle((float(data[3][2:]), float(data[4][2:])), (float(data[5][2:]), float(data[6][2:])), layer, datatype)
                self.cell.add(rect)
            elif (data[2] == "POLY"):
                vertice = 0
                pol_vertices = [(0, 0)] * int((len(data) - 3) / 2)
                while vertice < (len(data) - 3) / 2:
                    pol_vertices[vertice] = (float(data[vertice * 2 + 3][2:]), float(data[vertice * 2 + 4][2:]))
                    vertice += 1
                poly = gdspy.Polygon(pol_vertices, layer, datatype)
                self.cell.add(poly)
            else:
                print("Error! Malfunction in file at line: " + line.strip())
        self.lib.write_gds(output_file)
        self.cell.write_svg(output_file[:len(output_file) - 3] + "svg")
        if (out):
            print("Success in func write_txt_to_gds:", output_file, "generated by", text_file + ".")
    
    def equals(self, gds_file1, gds_file2):
        txt_file1 = gds_file1[:len(gds_file1) - 3] + "txt"
        txt_file2 = gds_file2[:len(gds_file2) - 3] + "txt"
        self.write_gds_to_txt(gds_file1, txt_file1, False)
        self.write_gds_to_txt(gds_file2, txt_file2, False)
        file1 = open(txt_file1, "r", -1)
        file2 = open(txt_file2, "r", -1)
        file1_lines = file1.readlines()
        file2_lines = file2.readlines()
        files_match = True
        shapes_match = True
        for i in range(max(len(file1_lines), len(file2_lines))):
            if (i >= len(file1_lines) or i >= len(file2_lines)):
                files_match = False
                shapes_match = False
                break
            if (file1_lines[i] != file2_lines[i]):
                files_match = False
                if ("RECT" in file1_lines[i] and "RECT" in file2_lines[i]):
                    substr_index1 = file1_lines[i].index("RECT")
                    substr_index2 = file2_lines[i].index("RECT")
                    if (file1_lines[i][substr_index1:] != file2_lines[i][substr_index2:]):
                        shapes_match = False
                        break
                elif ("POLY" in file1_lines[i] and "POLY" in file2_lines[i]):
                    substr_index1 = file1_lines[i].index("POLY")
                    substr_index2 = file2_lines[i].index("POLY")
                    if (file1_lines[substr_index1:] != file2_lines[substr_index2:]):
                        shapes_match = False
                        break
                else:
                    shapes_match = False
                    break
        if (files_match):
            print("Files match.")
        elif (shapes_match):
            print("Files do not match but they would disregarding layer/datatype.")
        else:
            print("Files do not match.")
        os.remove(txt_file1)
        os.remove(txt_file2)
    
    # generates a periodic .gds file mathematically through specified measurement
    def write_gds(self, output_file, p, l_e, h, n, taper, w_wg, h_wg, out=True):
        w = p - l_e
        x = y = count = 0
        while count < n:
            tooth = gdspy.Rectangle((x, y), (x + w, y + h))
            self.cell.add(tooth)
            x += p
            count += 1
        h_tr = (h - h_wg) / 2
        w_tr = h_tr/math.tan(taper * math.pi/180)
        trapezoid = gdspy.Polygon([(x, y), (x + w_tr, y + h_tr), (x + w_tr, y + h_tr + h_wg), (x, y + h)])
        self.cell.add(trapezoid)
        x += w_tr
        wave_guide = gdspy.Rectangle((x, y + h_tr), (x + w_wg, y + h_tr + h_wg))
        self.cell.add(wave_guide)
        x += w_wg
        trapezoid = gdspy.Polygon([(x, y + h_tr), (x + w_tr, y), (x + w_tr, y + h), (x, y + h_tr + h_wg)])
        self.cell.add(trapezoid)
        x += w_tr + l_e
        count = 0
        while count < n:
            tooth = gdspy.Rectangle((x, y), (x + w, y + h))
            self.cell.add(tooth)
            x += p
            count += 1
        self.lib.write_gds(output_file)
        self.cell.write_svg(output_file[:len(output_file) - 3] + "svg")
        if (out):
            print("Success in func write_gds:", output_file, "generated.")
from tkinter import *
from tkinter import filedialog
import math
import numpy as np
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt
import re
from collections import namedtuple

root = Tk()
global filename
root.update_idletasks()
filename = filedialog.askopenfilename(initialdir="/C", title="Select a file")
#A set of starting "commands"

def Choose_File():
    root.update_idletasks()
    global filename
    filename = filedialog.askopenfilename(initialdir="/C", title="Select a file")
#Creating the file choosing function, so you can change the gcode you are editing while in the program

#Variables
Materials = {'PLA':215, 'PETG':230, 'ASA':250,'ABS':245,'PVB':215}

#Functions
def Fix_Print():
    #Variables
    Gcode = ((open(filename, "r")).read()).split('\n')
    FixLayer = float(Fix_Print_Input.get())
    FirstLayer = float(First_Layer_Height_Input.get())
    Z_Hop = float(Z_Hop_Input.get())
    Index = 0
    New_Gcode= ""
    Fixing = False
    #Fixing the print
    for line in Gcode:
        if "G29 " == line[0:4]:
            continue
        if "G28 " == line[0:4]:
            New_Gcode += "\n"
            New_Gcode += "G28 X Y\nG1 Z"+str(float(FixLayer)+15)
            continue
        if ("G1 " in line or "G0 " in line) and " Z" in line:
            try:
                for part in line.split(" "):
                    if "Z" in part:
                        Z= float(part[1:])
                        break
                if Z == FirstLayer:
                    Fixing = True
                    continue
                if Z<FixLayer:
                    continue
                if Z==FixLayer+Z_Hop:
                    Fixing= False
                    New_Gcode += "\n"
                    New_Gcode += "G1 Z"+str(float(FixLayer)+0.5)
                    New_Gcode += "\nM106 S120\n"
                    Index = Gcode.index(line)
                    break
            except:
                for part in line.split(" "):
                    if "Z" in part:
                        Z= float(("0"+part[1:]))
                        break
                if Z == FirstLayer:
                    Fixing = True
                    continue
                if Z<FixLayer:
                    continue
                if Z==FixLayer+Z_Hop:
                    Fixing= False
                    New_Gcode += "\n"
                    New_Gcode += "G1 Z"+str(float(FixLayer)+0.5)
                    New_Gcode += "\nM106 S120\n"
                    Index = Gcode.index(line)
                    break
        if Fixing == True:
            continue
        New_Gcode += "\n"
        New_Gcode += line
    New_Gcode += "\n".join(Gcode[Index:])
    #ReWriting GCODE
    with open(filename.strip(".gcode") + "_cut_at_" + str(FixLayer) + ".gcode", 'w') as file:
        file.write(New_Gcode)
    Text_Space.insert(END,"\nThe print has been fixed\n")
#Fuction cuts the gcode at the specified heigh so you can continue you failed print
#(If you manage to probe the Z axis(or keep the Z value right) and the failed prind sticks to the build plate)

#MaterialChange
def Material_Change():
    #Variables
    Material_Change_Layer = str(Material_Change_Height_Input.get())
    Gcode = ((open(filename, "r")).read()).split('\n')
    New_Gcode= ""
    Material= Material_Box.curselection()
    #Adding the material change commands into the GCODE
    for line in Gcode:
        if "Z"+Material_Change_Layer in line:
            New_Gcode+="\n"
            New_Gcode+="M104 S"+str(Materials[Material_Box.get(Material)])+"\n"
            New_Gcode+="M600\n"
            Index = Gcode.index(line)
            New_Gcode += "\n".join(Gcode[Index:])
            break
        New_Gcode+="\n"
        New_Gcode+=line

    #ReWriting the GCODE      
    with open(filename.strip(".gcode")+"_MCH_on_Z:"+ Material_Change_Layer+"_to_"+Material_Box.get(Material)+".gcode", 'w') as file:
        file.write(New_Gcode)
    Text_Space.insert(END,"\nMaterial change has been added\n")
#This function makes material change possible.
#It makes a classic filament change at the specified height, but it does also change the temperature, so you can print with a new amterial

#GetLayers
def Get_Layers(UserCalled):
    #Variables
    Gcode = ((open(filename, "r")).read()).split('\n')
    global Layers
    Layers = []
    #Getting the layers used in the GCODE
    for line in Gcode:
        if ";" in line[0:2]:
            continue
        if ("G1" or "G0") in line and "Z" in line:
            try:
                z=line.split(" ")[1]
                Z=float(z[1:])
                if Z not in Layers:
                    Layers.append(Z)
            except:
                continue
    Layers.sort()
    if UserCalled == True:
        Text_Space.insert(END,"\nThis print has "+str(len(Layers))+" layers\nThe layers are:\n")
        Text_Space.insert(END, Layers)
#So the whole procces of getting the right heigh will be easier, this function will write out all of the layer heights used by the printer/gcode

#GetLayers
def Get_Xes():
    #Variables
    Gcode = ((open(filename, "r")).read()).split('\n')
    global Xes
    global Mean_Xes
    Xes = []
    #Getting the layers used in the GCODE
    for line in Gcode:
        if ("G1"or "G0") in line and "X" in line:
            try:
                x=line.split(" ")[1]
                for letter in x:
                    if letter[0] == "X":
                        X=int(x[1:])
                Xes.append(X)
            except:
                continue
    Mean_Xes = int(np.mean(Xes))
#So the whole procces of getting the right heigh will be easier, this function will write out all of the layer heights used by the printer/gcode

# Offset the print
def Offset_Print():
    #Variables
    Gcode = ((open(filename, "r")).read()).split('\n')
    New_Gcode=""
    Offset = float(Offset_Print_Input.get())
    Z=float
    #Offseting the print
    for line in Gcode:
        if " Z" in line and ("G1 " in line or "G0 " in line) and ";" not in line:
            Parts=""
            SplitedLine = line.split(" ")
            for part in SplitedLine:
                try:
                    if "Z" in part:
                        Z="Z"+str(float(part[1:])+Offset)
                        Parts+=Z+" "
                    else:
                        Parts+=part+" "       
                except:
                    Text_Space.insert(END,"\nOffseting has failed\n")
            New_Gcode+=Parts+"\n"
        else:
            New_Gcode+=line +"\n"

    #Write
    with open(filename.strip(".gcode")+"offset_by_"+str(Offset_Print_Input.get())+".gcode", "w") as output:
        output.write(New_Gcode)
    Text_Space.insert(END,"\nThe print has been offset\n")
#If for some reason you would want to start tthe print at a different height than Z0, this function does exactly that

def Clear_Text_Input():
   Text_Space.delete("1.0","end")
#Clears the text interface

def Probe_Z():
    Probe_Gcode = "G1 Z"+Probe_Z_Input.get()+"\nG30 X"+Probe_X_Input.get()+" Y"+Probe_Y_Input.get()
    with open("single_z_probe_x"+Probe_X_Input.get()+"_y"+Probe_Y_Input.get()+".gcode", "w") as probe_gcode:
        probe_gcode.write(Probe_Gcode)
    Text_Space.insert(END,"\nThe probe Gcode has been created\n")
#Creates a new gcode, which does a single Z probe on a scpecified location
#!!!Apparently it does not work with Klipper!!!

#Gcode bending, mostly copied from CNC kitchen
def Bend_Gcode():
    #Variables
    Point2D = namedtuple('Point2D', 'x y')
    GCodeLine = namedtuple('GCodeLine', 'x y z e f')
    INPUT_FILE_NAME = filename
    OUTPUT_FILE_NAME = filename.strip(".gcode")+"_bent.gcode"
    Get_Layers(False)
    Get_Xes()
    Heights = []
    for i in range(0,len(Layers)-10):
        Heights.append(Layers[i+1]-Layers[i])
    LAYER_HEIGHT = max(Heights)
    print(LAYER_HEIGHT)
    WARNING_ANGLE = int(Warning_Angle_Input.get())

    #2-point spline
    SPLINE_X = [Mean_Xes,Mean_Xes+float(X_Diff_Input.get())]
    SPLINE_Z = [0, max(Layers[:-1])]
    print(max(Layers))

    SPLINE = CubicSpline(SPLINE_Z, SPLINE_X, bc_type=((1, 0), (1, -np.pi/6)))
    DISCRETIZATION_LENGTH = 0.01 #discretization length for the spline length lookup table

    SplineLookupTable = [0.0]

    nx = np.arange(0,SPLINE_Z[-1],1)
    xs = np.arange(0,SPLINE_Z[-1],1)
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.plot(SPLINE_X, SPLINE_Z, 'o', label='data')
    ax.plot(SPLINE(xs), xs, label="S")
    ax.set_xlim(0, 200)
    ax.set_ylim(0, 200)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()

    def getNormalPoint(currentPoint: Point2D, derivative: float, distance: float) -> Point2D: #claculates the normal of a point on the spline
        angle = np.arctan(derivative) + math.pi /2
        return Point2D(currentPoint.x + distance * np.cos(angle), currentPoint.y + distance * np.sin(angle))

    def parseGCode(currentLine: str) -> GCodeLine: #parse a G-Code line
        thisLine = re.compile('(?i)^[gG][0-3](?:\s+x(?P<x>-?[0-9.]{1,15})|\s+y(?P<y>-?[0-9.]{1,15})|\s+z(?P<z>-?[0-9.]{1,15})|\s+e(?P<e>-?[0-9.]{1,15})|\s+f(?P<f>-?[0-9.]{1,15}))*')
        lineEntries = thisLine.match(currentLine)
        if lineEntries:
            return GCodeLine(lineEntries.group('x'), lineEntries.group('y'), lineEntries.group('z'), lineEntries.group('e'), lineEntries.group('f'))

    def writeLine(G, X, Y, Z, F = None, E = None): #write a line to the output file
        outputSting = "G" + str(int(G)) + " X" + str(round(X,5)) + " Y" + str(round(Y,5)) + " Z" + str(round(Z,3))
        if E is not None:
            outputSting = outputSting + " E" + str(round(float(E),5))
        if F is not None:
            outputSting = outputSting + " F" + str(int(float(F)))
        outputFile.write(outputSting + "\n")

    def onSplineLength(Zheight) -> float: #calculates a new z height if the spline is followed
        for i in range(len(SplineLookupTable)):
            height = SplineLookupTable[i]
            if height >= Zheight:
                return i * DISCRETIZATION_LENGTH
        print("Error! Spline not defined high enough!")

    def createSplineLookupTable():
        heightSteps = np.arange(DISCRETIZATION_LENGTH, SPLINE_Z[-1], DISCRETIZATION_LENGTH)
        for i in range(len(heightSteps)):
            height = heightSteps[i]
            SplineLookupTable.append(SplineLookupTable[i] + np.sqrt((SPLINE(height)-SPLINE(height-DISCRETIZATION_LENGTH))**2 + DISCRETIZATION_LENGTH**2))
    
    lastPosition = Point2D(0, 0)
    currentZ = 0.0
    lastZ = 0.0
    currentLayer = 0
    relativeMode = False
    createSplineLookupTable()

    with open(INPUT_FILE_NAME, "r") as gcodeFile, open(OUTPUT_FILE_NAME, "w+") as outputFile:
        for currentLine in gcodeFile:
            if currentLine[0] == ";":   #if NOT a comment
                outputFile.write(currentLine)
                continue
            if currentLine.find("G91 ") != -1:   #filter relative commands
                relativeMode = True
                outputFile.write(currentLine)
                continue
            if currentLine.find("G90 ") != -1:   #set absolute mode
                relativeMode = False
                outputFile.write(currentLine)
                outputFile.write("\nM83\n")
                continue
            if relativeMode: #if in relative mode don't do anything
                outputFile.write(currentLine)
                continue
            currentLineCommands = parseGCode(currentLine)
            if currentLineCommands is not None: #if current comannd is a valid gcode
                if currentLineCommands.z is not None: #if there is a z height in the command
                    currentZ = float(currentLineCommands.z)
                    
                if currentLineCommands.x is None or currentLineCommands.y is None: #if command does not contain x and y movement it#s probably not a print move
                    if currentLineCommands.z is not None: #if there is only z movement (e.g. z-hop)
                        outputFile.write("G91\nG1 Z" + str(currentZ-lastZ))
                        if currentLineCommands.f is not None:
                            outputFile.write(" F" + str(currentLineCommands.f))
                        outputFile.write("\nG90\n")
                        outputFile.write("\nM83\n")
                        lastZ = currentZ
                        continue
                    outputFile.write(currentLine)
                    continue
                currentPosition = Point2D(float(currentLineCommands.x), float(currentLineCommands.y))
                midpointX = lastPosition.x + (currentPosition.x - lastPosition.x) / 2  #look for midpoint
                distToSpline = midpointX - SPLINE_X[0]
                
                #Correct the z-height if the spline gets followed
                correctedZHeight = onSplineLength(currentZ)         
                angleSplineThisLayer = np.arctan(SPLINE(correctedZHeight, 1)) #inclination angle this layer
                angleLastLayer = np.arctan(SPLINE(correctedZHeight - LAYER_HEIGHT, 1)) # inclination angle previous layer
                heightDifference = np.sin(angleSplineThisLayer - angleLastLayer) * distToSpline * -1 # layer height difference
                
                transformedGCode = getNormalPoint(Point2D(correctedZHeight, SPLINE(correctedZHeight)), SPLINE(correctedZHeight, 1), currentPosition.x - SPLINE_X[0])
                #Check if a move is below Z = 0
                if float(transformedGCode.x) <= 0.0: 
                    print("Warning! Movement below build platform. Check your spline!")

                #Detect unplausible moves
                if transformedGCode.x < 0 or np.abs(transformedGCode.x - currentZ) > 50:
                    print("Warning! Possibly unplausible move detected on height " + str(currentZ) + " mm!")
                    outputFile.write(currentLine)
                    continue 

                #Check for self intersection
                if (LAYER_HEIGHT + heightDifference) < 0:
                    print("ERROR! Self intersection on height " + str(currentZ) + " mm! Check your spline!")
                    
                #Check the angle of the printed layer and warn if it's above the machine limit
                if angleSplineThisLayer > (WARNING_ANGLE * np.pi / 180.):
                    print("Warning! Spline angle is", (angleSplineThisLayer * 180. / np.pi), "at height  ", str(currentZ), " mm! Check your spline!")
                                                    
                if currentLineCommands.e is not None: #if this is a line with extrusion
                    extrusionAmount = float(currentLineCommands.e) * ((LAYER_HEIGHT + heightDifference)/LAYER_HEIGHT)

                else:
                    extrusionAmount = None                    
                writeLine(1,transformedGCode.y, currentPosition.y, transformedGCode.x, None, extrusionAmount)
                lastPosition = currentPosition
                lastZ = currentZ
            else:
                outputFile.write(currentLine)

    
#Globals
global FixPrintInput
global RiseLayerInput
global MaterialChangeInput
global FirstLayerHeightInput
global TextSpace
global OffsetPrintInput
global ZHopInput
global MaterialBox
global gcode
global Gcode

#Buttons
Fix_Print_Button = Button(root, text="Fix the print", width=36, command=Fix_Print)
Offset_Print_Button = Button(root, text="Offset the print",width=36, command=Offset_Print)
Material_Change_Button = Button(root, text="Material change", width=36, command=Material_Change)
Get_Layers_Button = Button(root, text="Get layers", width=36,command= lambda: Get_Layers(True))
Clear_Text_Input_Button = Button(root, text="Clear", width=15,command=Clear_Text_Input)
Choose_File_Button = Button(root, text="Choose file", padx=40, command=Choose_File)
Probe_Z_Button = Button(root, text="Create Z probe", width=36, command=Probe_Z)
Bend_Gcode_Button = Button(root, text="Bend GCODE", width=36, command=Bend_Gcode)

#Inputs
Fix_Print_Input = Entry(root, text="Layer height")
Offset_Print_Input = Entry(root, width=20)
Material_Change_Height_Input = Entry(root, width=20)
Probe_Z_Input = Entry(root, width=20)
Probe_Y_Input = Entry(root, width=20)
Probe_X_Input = Entry(root, width=20)
First_Layer_Height_Input = Entry(root, width=20)
Z_Hop_Input = Entry(root, width=20)
X_Diff_Input = Entry(root, width=20)
Warning_Angle_Input = Entry(root, width=20)

#Frames
Text_Space_Frame = Frame(root, bd=2.5) 
Text_Space = Text(Text_Space_Frame, width=30)

#Labels
Fix_Height_Label = Label(root, text="Height:", width=20)
First_Layer_Height_Label = Label(root, text="First layer height", width=20)
Offset_Print_Label = Label(root, text="Offset:", width=20)
Material_Change_Height_Label = Label(root, text="Height:", width=20)
New_Material_Label = Label(root, text="New Material:")
Probe_Z_Label = Label(root, text="Z height:")
Probe_Y_Label = Label(root, text="Y:")
Probe_X_Label = Label(root, text="X:")
Z_Hop_Label = Label(root, text="Z hop:")
X_Diff_Label = Label(root, text="X difference:")
Warning_Angle_Label = Label(root, text="Warning angle:")

#Lists
Material_Box = Listbox(root, width = 20, height=3)
Material_Box.insert(1, "PLA")
Material_Box.insert(2, "PETG")
Material_Box.insert(3, "ASA")
Material_Box.insert(4, "ABS")
Material_Box.insert(5, "PVB")

#Griding

#Basic utilities
Choose_File_Button.grid(row=0, column=0, columnspan=2)
Clear_Text_Input_Button.grid(row=0, column=6)
Text_Space_Frame.grid(row=1, column=6, rowspan=12)
Text_Space.grid()

#Fix print utility
Fix_Print_Button.grid(row=1, column=0, columnspan=2)
First_Layer_Height_Input.grid(row=3, column=1)
First_Layer_Height_Label.grid(row=3, column=0)
Z_Hop_Label.grid(row=4, column=0)
Z_Hop_Input.grid(row=4, column=1)
Fix_Height_Label.grid(row=2, column=0)
Fix_Print_Input.grid(row=2, column=1)

#Get layers utility
Get_Layers_Button.grid(row=10, column=0, columnspan=2)

#Change material utility
Material_Change_Button.grid(row=7, column=0, columnspan=2)
Material_Change_Height_Input.grid(row=8, column=1)
Material_Box.grid(row=9, column=1)
Material_Change_Height_Label.grid(row=8, column=0)
New_Material_Label.grid(row=9, column=0)

#Offset the print utility
Offset_Print_Input.grid(row=6, column=1)
Offset_Print_Label.grid(row=6, column=0)
Offset_Print_Button.grid(row=5, column=0, columnspan=2)

#Create Z probe utility
Probe_Z_Button.grid(row=11, column=0, columnspan=2)
Probe_Z_Input.grid(row=12, column=1)
Probe_Y_Input.grid(row=13, column=1)
Probe_X_Input.grid(row=14, column=1)
Probe_Z_Label.grid(row=12, column=0)
Probe_Y_Label.grid(row=13, column=0)
Probe_X_Label.grid(row=14, column=0)

#Bend Gcode utility
Bend_Gcode_Button.grid(row=1, column=3, columnspan=2)
X_Diff_Label.grid(row=2, column=3)
X_Diff_Input.grid(row=2, column=4)
Warning_Angle_Label.grid(row=3, column=3)
Warning_Angle_Input.grid(row=3, column=4)

root.mainloop()
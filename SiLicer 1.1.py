from tkinter import *
from tkinter import filedialog
from timeit import default_timer as timer

root = Tk()
global filename
root.update_idletasks()
filename = filedialog.askopenfilename(initialdir="/C", title="Select a file")
#A set of starting "commands"

def ChooseFile():
    root.update_idletasks()
    filename = filedialog.askopenfilename(initialdir="/C", title="Select a file")
#Creating the file choosing function, so you can change the gcode you are editing while in the program

#Variables
Materials = {'PLA':215, 'PETG':230, 'ASA':250,'ABS':245,'PVB':215}

#Functions
def FixPrint():
    #Variables
    gcode = (open(filename, "r")).read()
    Gcode = gcode.split('\n')
    FixLayer = FixPrintInput.get()
    FirstLayer = FirstLayerHeightInput.get()
    ZHop = float(ZHopInput.get())
    Index = 0
    Final= ""
    Fix = False
    Fixing = False

    #Fixing the print
    for line in Gcode:
        if "G29 " in line or " Z" + FirstLayer in line or " Z3 " in line:
            continue
        if "G28 " in line:
            Final += "\n"
            Final += "G28 X Y\nG1 Z"+str(float(FixLayer)+15)
            continue
        if ("M107" in line or "M106 S0" in line) and Fix == False:
            Fixing = True
            Fix = True
            Final += "\n"
            Final += "M106 S120"
            continue
        if Fixing == True:
            if (" Z"+str(float(FixLayer)+ZHop)) in line:
                Fixing= False
                Final += "\n"
                Final += "G1 Z"+str(float(FixLayer)+0.5)
                Final += "\n"
                Index = Gcode.index(line)
                break
            continue
        Final += "\n"
        Final += line
    Final += "\n".join(Gcode[Index:])
    #ReWriting GCODE
    with open(filename.strip(".gcode") + "_cut_at_" + FixLayer + ".gcode", 'w') as file:
        file.write(Final)
    TextSpace.insert(END,"\nThe print has been fixed\n")
#Fuction which cuts the gcode at the specified heigh so you can continue you failed print
#(If you manage to probe the Z axis and it sticks to the build plate)


#MaterialChange
def MaterialChange():
    #Variables
    MaterialChangeLayer = str(MaterialChangeInput.get())
    gcode = (open(filename, "r")).read()
    Gcode = gcode.split('\n')
    Final= ""
    i= MaterialBox.curselection()
    #Adding the material change commands into the GCODE
    for line in Gcode:
        if "Z"+MaterialChangeLayer in line:
            Final+="\n"
            Final+="M104 S"+str(Materials[MaterialBox.get(i)])+"\n"
            Final+="M600\n"
            Index = Gcode.index(line)
            Final += "\n".join(Gcode[Index:])
            break
        Final+="\n"
        Final+=line

    #ReWriting the GCODE      
    with open(filename.strip(".gcode")+"_MCH_on_Z:"+ MaterialChangeLayer+"_to_"+MaterialBox.get(i)+".gcode", 'w') as file:
        file.write(Final)
    TextSpace.insert(END,"\nMaterial change has been added\n")
#This function makes material change possible.
#It makes a classic filament change at the specified height, but it does also change the temperature, so you can print with new amterial

#GetLayers
def Getlayers():
    #Variables
    gcode = (open(filename, "r")).read()
    Gcode = gcode.split('\n')
    Layers = []
    #Getting the layers used in the GCODE
    for line in Gcode:
        if ("G1"or "G0") and "Z"in line:
            Interlayer = line[4:]
            try:
                FLayers=float(Interlayer)
                if FLayers not in Layers:
                    Layers.append(float(Interlayer))
            except:
                continue
    Layers.sort()
    TextSpace.insert(END,"\nThis print has "+str(len(Layers))+" layers\nThe layers are:\n")
    TextSpace.insert(END, Layers)
#So the whole procces of getting the right heigh will be easier, this function will write out all of the layer heights used by the printer/gcode

# Offset the print
def OffsetPrint():
    Start = timer()
    gcode = (open(filename, "r")).read()
    Gcode = gcode.split('\n')
    Final=""
    Offset = float(OffsetPrintInput.get())
    Z=float
    for line in Gcode:
        if " Z" in line and ("G1 " in line or "G0 " in line) and ";" not in line:
            InterFinal=""
            SplitedLine = line.split(" ")
            for line2 in SplitedLine:
                try:
                    if "Z" in line2:
                        Z="Z"+str(float(line2[1:])+Offset)
                        InterFinal+=Z+" "
                    else:
                        InterFinal+=line2+" "       
                except:
                    print("Offseting has failed")
            Final+=InterFinal+"\n"
        else:
            Final+=line +"\n"

    #Write
    with open(filename.strip(".gcode")+"offset_by_"+str(OffsetPrintInput.get())+".gcode", "w") as output:
        output.write(Final)
    TextSpace.insert(END,"\nThe print has been offset\n")
    End = timer()
    print(str(End-Start))
#If for some reason you would want to start tthe print at a different height than Z0, this function does exactly that

def clearToTextInput():
   TextSpace.delete("1.0","end")
#Clears the text interface

def Calibrate_Z():
    pgcode = "G1 Z"+probe_zInput.get()+"\nG30 X"+probe_xInput.get()+" Y"+probe_yInput.get()
    with open("single_z_probe_x"+probe_zInput.get()+"_y"+probe_xInput.get()+".gcode", "w") as probegcode:
        probegcode.write(pgcode)
    TextSpace.insert(END,"\nThe probe Gcode has been created\n")
#Creates a nmew gcode, which does a single Z probe on a scpecified location
#!!!Apparently it does not work with Klipper!!!

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
FixPrintButton = Button(root, text="Fix the print", width=36, pady=5, command=FixPrint)
OffsetPrintButton = Button(root, text="Offset the print",width=36, pady=5, command=OffsetPrint)
MaterialChangeButton = Button(root, text="Material change", width=36, pady=5, command=MaterialChange)
GetLayersButton = Button(root, text="Get layers", width=36, pady=5,command=Getlayers)
clearToTextInputButton = Button(root, text="Clear", width=15, pady=2,command=clearToTextInput)
ChooseFileButton = Button(root, text="Choose file", padx=40, command=ChooseFile)
probeZButton = Button(root, text="Create Z probe", width=36, pady=5, command=Calibrate_Z)

#Inputs
FixPrintInput = Entry(root, text="Layer height")
OffsetPrintInput = Entry(root, width=20)
MaterialChangeInput = Entry(root, width=20)
MaterialChangeInput2 = Entry(root, width=20)
probe_zInput = Entry(root, width=20)
probe_yInput = Entry(root, width=20)
probe_xInput = Entry(root, width=20)
FirstLayerHeightInput = Entry(root, width=20)
ZHopInput = Entry(root, width=20)

#Frames
TextSpaceFrame = Frame(root, bd=2.5) 
TextSpace = Text(TextSpaceFrame, width=30)

#Labels
FixHeight = Label(root, text="Height:", width=20)
FirstLayerHeightLabel = Label(root, text="First layer height", width=20)
OffsetPrintLabel = Label(root, text="Offset:", width=20)
ChangeHeight = Label(root, text="Height:", width=20)
NewMaterial = Label(root, text="New Material:")
probeZ = Label(root, text="Z height:")
probeY = Label(root, text="Y:")
probeX = Label(root, text="X:")
ZHopLabel = Label(root, text="Z hop:")

#Lists
MaterialBox = Listbox(root, width = 20, height=3)
MaterialBox.insert(1, "PLA")
MaterialBox.insert(2, "PETG")
MaterialBox.insert(3, "ASA")
MaterialBox.insert(4, "ABS")
MaterialBox.insert(5, "PVB")

#Griding
ChooseFileButton.grid(row=0, column=0, columnspan=2)
clearToTextInputButton.grid(row=0, column=4)
FixPrintButton.grid(row=1, column=0, columnspan=2)
FirstLayerHeightInput.grid(row=3, column=1)
FirstLayerHeightLabel.grid(row=3, column=0)
ZHopLabel.grid(row=4, column=0)
ZHopInput.grid(row=4, column=1)
OffsetPrintButton.grid(row=5, column=0, columnspan=2)
MaterialChangeButton.grid(row=7, column=0, columnspan=2)
GetLayersButton.grid(row=10, column=0, columnspan=2)
FixPrintInput.grid(row=2, column=1)
OffsetPrintInput.grid(row=6, column=1)
MaterialChangeInput.grid(row=8, column=1)
MaterialBox.grid(row=9, column=1)
TextSpaceFrame.grid(row=1, column=4, rowspan=12)
TextSpace.grid()
FixHeight.grid(row=2, column=0)
OffsetPrintLabel.grid(row=6, column=0)
ChangeHeight.grid(row=8, column=0)
NewMaterial.grid(row=9, column=0)
probeZButton.grid(row=11, column=0, columnspan=2)
probe_zInput.grid(row=12, column=1)
probe_yInput.grid(row=13, column=1)
probe_xInput.grid(row=14, column=1)
probeZ.grid(row=12, column=0)
probeY.grid(row=13, column=0)
probeX.grid(row=14, column=0)

root.mainloop()
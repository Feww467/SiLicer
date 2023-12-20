from tkinter import *
from tkinter import filedialog

root = Tk()
filename = ""

def ChooseFile():
    #Globals
    global filename
    global gcode
    global FixPrintInput
    global RiseLayerInput
    global MaterialChangeInput
    global TextSpace
    global OffsetPrintInput
    global MaterialBox
    filename = filedialog.askopenfilename(initialdir="/C", title="Select a file")
    gcode = open(filename, "r")
    #Buttons
    FixPrintButton = Button(root, text="Fix the print", width=36, pady=5, command=FixPrint)
    OffsetPrintButton = Button(root, text="Rise Layers",width=36, pady=5, command=OffsetPrint)
    MaterialChangeButton = Button(root, text="Material Change", width=36, pady=5, command=MaterialChange)
    GetLayersButton = Button(root, text="Get Layers", width=36, pady=5,command=Getlayers)
    clearToTextInputButton = Button(root, text="Clear", width=15, pady=2,command=clearToTextInput)
    #Inputs
    FixPrintInput = Entry(root, text="Layer height")
    OffsetPrintInput = Entry(root, width=20)
    MaterialChangeInput = Entry(root, width=20)
    MaterialChangeInput2 = Entry(root, width=20)
    #Frames
    TextSpaceFrame = Frame(root, bd=2.5) 
    TextSpace = Text(TextSpaceFrame, width=30)
    #Labels
    FixHeight = Label(root, text="Height:", width=20)
    OffsetPrintLabel = Label(root, text="Offset:", width=20)
    ChangeHeight = Label(root, text="Height:", width=20)
    NewMaterial = Label(root, text="New Material:")
    #Lists
    MaterialBox = Listbox(root, width = 20, height=3)
    MaterialBox.insert(1, "PLA")
    MaterialBox.insert(2, "PETG")
    MaterialBox.insert(3, "ASA")
    MaterialBox.insert(4, "ABS")
    MaterialBox.insert(5, "PVB")

    #Griding
    clearToTextInputButton.grid(row=0, column=2)
    FixPrintButton.grid(row=1, column=0, columnspan=2)
    OffsetPrintButton.grid(row=3, column=0, columnspan=2)
    MaterialChangeButton.grid(row=5, column=0, columnspan=2)
    GetLayersButton.grid(row=8, column=0, columnspan=2)
    FixPrintInput.grid(row=2, column=1)
    OffsetPrintInput.grid(row=4, column=1)
    MaterialChangeInput.grid(row=6, column=1)
    MaterialBox.grid(row=7, column=1)
    TextSpaceFrame.grid(row=1, column=2, rowspan=8)
    TextSpace.grid()
    FixHeight.grid(row=2, column=0)
    OffsetPrintLabel.grid(row=4, column=0)
    ChangeHeight.grid(row=6, column=0)
    NewMaterial.grid(row=7, column=0)

ChooseFileButton = Button(root, text="Choose file", padx=40, command=ChooseFile)
ChooseFileButton.grid(row=0, column=0, columnspan=2)


#Variables
Materials = {'PLA':215, 'PETG':230, 'ASA':250,'ABS':245,'PVB':215}

#Functions
def FixPrint():
    #Variables
    gcode = open(filename, "r")
    GCODE = gcode.read()
    Gcode = GCODE.split('\n')
    FixLayer = str(FixPrintInput.get())
    Final= ""
    Fixing = False
    Fix= False

    #Fixing the print
    for line in Gcode:
        if "G29" in line:
            continue
        if "G80" in line:
            continue
        if "G28" in line:
            Final += "\n"
            Final += "G28 X Y"
            continue
        if "M107" in line:
            if Fix==True:
                Final += line
                continue
            Fixing = True
            Fix = True
            Final += "\n"
            Final += "M106 S120"
        if Fixing == True:
            if ("Z"+FixLayer) in line:
                Fixing= False
                Final += "\n"
                Final += "G1 Z"+str(float(FixLayer)+0.4)
                Final += "\n"
                Final += line
                continue
            continue
        Final += "\n"
        Final += line
    #ReWriting GCODE      
    with open(filename, 'r') as file:
        file_contents = file.read()
    new_contents = file_contents.replace(GCODE, Final)
    GCODE = Final
    with open(filename, 'w') as file:
        file.write(new_contents)
    TextSpace.insert(END,"\nThe print has been fixed\n")

#MaterialChange
def MaterialChange():
    #Variables
    gcode = open(filename, "r")
    GCODE = gcode.read()
    Gcode = GCODE.split('\n')
    MaterialChangeLayer = str(MaterialChangeInput.get())
    Final= ""
    Change=NO
    i= MaterialBox.curselection()
    print("M104 S"+str(Materials[MaterialBox.get(i)])+"\n")
    #Adding the material change commands into the GCODE
    for line in Gcode:
        if "Z"+MaterialChangeLayer in line and Change==NO:
            Final+="\n"
            Final+="M104 S"+str(Materials[MaterialBox.get(i)])+"\n"
            Final+="M600\n"
            Final += line
            Change = YES
            continue
        Final+="\n"
        Final+=line

    #ReWriting the GCODE      
    with open(filename, 'r') as file:
        file_contents = file.read()
    new_contents = file_contents.replace(GCODE, Final)
    GCODE = Final
    with open(filename, 'w') as file:
        file.write(new_contents)
    TextSpace.insert(END,"\nMaterial change has been added\n")

#GetLayers
def Getlayers():
    #Variables
    gcode = open(filename, "r")
    GCODE = gcode.read()
    global SplitedGCODE
    SplitedGCODE = GCODE.split('\n')
    Layers = []
    #Getting the layers used in the GCODE
    for line in SplitedGCODE:
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

#RiseLayers
def OffsetPrint():
    Final=str()
    Offset = float(OffsetPrintInput.get())
    Z=float
    for line in gcode:
        if ";" not in line:
            if "Z" in line:
                InterFinal=""
                SplitedLine = line.split(" ")
                for line2 in SplitedLine :
                    try:
                        if "Z" in line2:
                            Z="Z"+str(float(line2[1:])+Offset)
                            InterFinal+=Z+" "
                        else:
                            InterFinal+=line2+" "       
                    except:
                        Final+=line
                        print("Offseting has failed")
                Final+=InterFinal+"\n"
            else:
                Final+=line
        else:
            Final+=line
    #Write
    GCODE = gcode.read()
    with open(filename, 'r') as file:
        file_contents = file.read()
    new_contents = file_contents.replace(file_contents, Final)
    with open(filename, 'w') as file:
        file.write(new_contents)
    TextSpace.insert(END,"\nThe print has been offset\n")

def clearToTextInput():
   TextSpace.delete("1.0","end")

root.mainloop()
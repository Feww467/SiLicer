from tkinter import *
from tkinter import filedialog

root = Tk()
filename = ""

def ChooseFile():
    global filename
    filename = filedialog.askopenfilename(initialdir="/C", title="Select a file")
    global gcode
    gcode = open(filename, "r")
    #GetBasicInfo
    PrintFixButton = Button(root, text="Fix the print",padx=40, pady=20, command=PrintFix)
    RiseLayersButton = Button(root, text="Rise Layers",padx=40, pady=20, command=RiseLayers)
    MaterialsChangeButton = Button(root, text="Material Change", padx=40, pady=20, command=ChangeMaterials)
    GetLayersButton = Button(root, text="Get Layers", padx=40, pady=20,command=Getlayers)
    
    PrintFixButton.grid(row=1, column=0)
    RiseLayersButton.grid(row=1, column=1)
    MaterialsChangeButton.grid(row=2, column=0)
    GetLayersButton.grid(row=2, column=1)

ChooseFileButton = Button(root, text="Choose file", padx=40, command=ChooseFile)


#Variables
Firstlayerheigh = str(0.2)
FixLayer = str(10)
Layers = []
LayerRise = 1
Rise = 1
Materials = {'PLA':215, 'PETG':230, 'ASA':250,'ABS':245,'PVB':215}
MaterialsChangeLayer = 10
print("Done")

#Functions
#Printfix
def PrintFix():
    gcode = open(filename, "r")
    GCODE = gcode.read()
    global SplitedGCODE
    SplitedGCODE = GCODE.split(';')

    FixState = False
    global Final
    Final = ""
    FixCount = 0
    print("Done")

    for line in SplitedGCODE:
        FixCount += 1
        if FixState == False or line == "Z:"+FixLayer+"\n":
            if line == "Z:"+Firstlayerheigh+"\n":
                FixState  = True
            else:
                Final = Final +";" + line
                FixState = False
                if line == "Z:"+FixLayer+"\n":
                    break
    Fixrest = ";".join(SplitedGCODE[FixCount+6:])

    SplitedFinal = Final.split(';')
    Final = ""
    for line in SplitedFinal:
        if "intro" in line:
             continue
        if "set travel acceleration" in line:
            continue
        if "home all without mesh bed level" in line:
            continue

        Final += line+";"
    Final += "CUT"
    Final += "\nG1 Z"+str(FixLayer)+" F720\n"
    Final += Fixrest

    #Write      
    with open(filename, 'r') as file:
        file_contents = file.read()
    new_contents = file_contents.replace(GCODE, Final)
    GCODE = Final
    with open(filename, 'w') as file:
        file.write(new_contents)
#ChangeMaterials
def ChangeMaterials():
    gcode = open(filename, "r")
    GCODE = gcode.read()
    global SplitedGCODE
    SplitedGCODE = GCODE.split(';')

    global Final
    Final = ";"
    print("Done")

    for line in SplitedGCODE:
        if 'Z:'+str(MaterialsChangeLayer) in line:
            Final += 'G1 Z'+str(MaterialsChangeLayer+1)+'\nG1 X0 Y0\nM104 S215\nM109 S215\nM600'
        else:
            Final += line+";"

    #Write      
    with open(filename, 'r') as file:
        file_contents = file.read()
    new_contents = file_contents.replace(GCODE, Final)
    GCODE = Final
    with open(filename, 'w') as file:
        file.write(new_contents)


#GetLayers
def Getlayers():
    Layers = []
    for line in SplitedGCODE:
        if line[0:2] == "Z:":
            Interlayer = line[3:]
            try:
                Layers.append(float(Interlayer[:-1]))
            except:
                continue
            Layers.sort()
#RiseLayers
def RiseLayers():
    Final=str()
    for line in gcode:
        if "G1 Z" in line:
            Iline = line[5:]
            try:
                SpLine = line.split()
                ZLine = SpLine[1]
                SpLine[1] = 'Z'+str(float(ZLine[1:])+Rise)
                RisedLine = ' '.join(SpLine)+"\n"
                Final+=RisedLine
            except:
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
    print("DoneRL")


ChooseFileButton.grid(row=0, column=0)

print("Done")

root.mainloop()
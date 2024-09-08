# SiLicer
Post processing program for GCODE
Inspired by @CNCkitchen https://www.youtube.com/watch?v=-wjE8eDiKWg 

Usage:
1) Run the code with no initial input
2) It will ask you to choose a file/gcode you want to work with
3) You are than introduced into an enviroment, where you can run some basic functions and change the file you are editing

Functions:
1) Fix the print: Modifies the GCODE, so the printer starts printing on the layer, where it stopped.
2) Material change: A normal filament change, but it also changes the temperature, so another material can be used
3) Get the layers: For some of the functions or something else, you might need to know the layers on which the printer prints
4) Offset the print: Moves the whole print up in Z axis

!!!Warning!!!:
Different slicers use different settings for different printers, so be sure to check out the start of the Gcode for any unwanted Z moves.

In case of any recommendations please contact me on sikorkaj25@outlook.com

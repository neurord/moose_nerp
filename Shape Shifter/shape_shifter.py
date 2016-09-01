'''<Condenses .p files of neuron traces to maintain specific lambda (ac or dc) and removes 0 length compartments.>
    Copyright (C) <2016>  <Saivardhan Mada>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.'''


#Saivardhan Mada
#Jul 20th, 2016
#runs using python3
import sys
import math
import argparse
import numpy as np

#set default parameters
rm = 4.0032 #ohms-m^2 
ri = 2.50 #ohms-m
cm = 0.010153 #F/m^2
lamb = 0.1
f = .1 #Hz
type1 = "radii"

#name of the files
in_name = "ri04_v3.p"
out_name = "out_" + in_name

#dictionary to hold deleted voxels
deleted = {}
needtowrite = []


# def soma(input_file, output_file, type1, RM, RI, CM, F):
	

def condenser(input_file, output_file, type1, RM, RI, CM, F):
	comp2 = []#blank variable to hold previous compartment
	tobecondensed = []
	future = {}
	tm = RM * CM #time constant
	dc_factor = math.sqrt(RM/(RI*4.0))*1000 #1000 is for unit conversion to microns 
	lamb_tot = 0
	surface_tot = 0
	partial_ac= 2.0*math.pi*F*tm 
	ac_factor = dc_factor * math.sqrt(2.0/(1.0+math.sqrt(1.0+math.pow(partial_ac,2.0))))
	for line in input_file:
		comp1 = line.split()
		line_num = input_file.index(line)
		if(line_num <= len(input_file)-2):
			comp2 = input_file[line_num+1].split()

		if(len(comp1) == 6):# if voxel

			if(type1 == "0"):# type which removes 0 length compartments
				print(comp1)
				if(comp1[2] == "0" and comp1[3] == "0" and comp1[4] == "0"):#if all coordinates are 0's
					deleted[comp1[0]] = comp1[1]# saves into dictionary to check future voxels
				elif(deleted.has_key(comp1[1])):# if voxel refers to deleted voxel change the connection to the deleted voxels connection
					print(deleted[comp1[1]])
					output_file.write(comp1[0]+" "+deleted[comp1[1]]+" "+comp1[2]+" "+comp1[3]+" "+comp1[4]+" "+comp1[5]+"\n")
				else:
					output_file.write(line)

			elif(type1 == "ac"):#condenses branches with same radius and minimum electronic length of .01 lambda [AC]
				ac = ac_factor * math.sqrt(float(comp2[5]))#calculates lambda for ac
				if(len(comp1) == 6):
					#basically change this to 10% and calculate the lens again and check for electronic length being less then 
					if(comp1[5] == comp2[5]):#if the radius is the same

						len_comp1 = (math.pow(float(comp1[2]),2.0)+math.pow(float(comp1[3]),2.0)+math.pow(float(comp1[4]),2.0))/ac #electronic length of compartment 1
						len_comp2 = (math.pow(float(comp2[2]),2.0)+math.pow(float(comp2[3]),2.0)+math.pow(float(comp2[4]),2.0))/ac #electronic length of compartment 2

						#print(len_comp1+len_comp2)
						if((len_comp2+len_comp1) < lamb):#if it is less then the designated lambada value condense the branch
								#output_file.write(comp2[0]+" "+deleted[comp2[1]]+" "+comp2[2]+" "+comp2[3]+" "+comp2[4]+" "+comp2[5]+"\n")
								if(comp1[1] in deleted):
									deleted[comp1[0]] = deleted[comp1[1]]
								else:
									deleted[comp1[0]] = comp1[1]
							
						#output_file.write(comp2[0]+" "+comp1[1]+" "+comp2[2]+" "+comp2[3]+" "+comp2[4]+" "+comp2[5]+"\n")
						elif(comp1[1] in deleted):
							output_file.write(comp1[0]+" "+deleted[comp1[1]]+" "+comp1[2]+" "+comp1[3]+" "+comp1[4]+" "+comp1[5]+"\n")
						else:
							output_file.write(line)
					elif(comp1[1] in deleted):
						output_file.write(comp1[0]+" "+deleted[comp1[1]]+" "+comp1[2]+" "+comp1[3]+" "+comp1[4]+" "+comp1[5]+"\n")
					else:
						#check if it has the same radius as the next branch before deciding to write to output 

						output_file.write(line)
			elif(type1 == "radii"):#condenses branches with same radius and minimum electronic length of .01 lambda [AC]
				
				if(len(comp1) == 6):
					ten = .2*float(comp1[5])
					#basically change this to 10% and calculate the lens again and check for electronic length being less then 
					if(abs(float(comp1[5]) - float(comp2[5])) <= ten):#if the radius is the same
						ac1 = ac_factor * math.sqrt(float(comp1[5]))#calculates lambda for ac
						ac2 = ac_factor * math.sqrt(float(comp2[5]))#calculates lambda for ac
						len_comp1 = (math.pow(float(comp1[2]),2.0)+math.pow(float(comp1[3]),2.0)+math.pow(float(comp1[4]),2.0))/ac1 #electronic length of compartment 1
						len_comp2 = (math.pow(float(comp2[2]),2.0)+math.pow(float(comp2[3]),2.0)+math.pow(float(comp2[4]),2.0))/ac2 #electronic length of compartment 2
						#print(len_comp1+len_comp2)
						#comp1[5] = str((float(comp1[5]) + float(comp2[5]))/2.0)
						if((len_comp2+len_comp1)+lamb_tot < lamb):#if it is less then the designated lambada value condense the branch
								#output_file.write(comp2[0]+" "+deleted[comp2[1]]+" "+comp2[2]+" "+comp2[3]+" "+comp2[4]+" "+comp2[5]+"\n")
								#print("hey")
								lamb_tot = lamb_tot + (len_comp2+len_comp1)
								surface_tot = surface_tot + (2* math.pi * float(comp1[5]) * (math.pow(float(comp1[2]),2.0)+math.pow(float(comp1[3]),2.0)+math.pow(float(comp1[4]),2.0)))
								if(comp1[1] in deleted):
									deleted[comp1[0]] = deleted[comp1[1]]
									tobecondensed.append(comp1)
								else:
									deleted[comp1[0]] = comp1[1]
								
						#output_file.write(comp2[0]+" "+comp1[1]+" "+comp2[2]+" "+comp2[3]+" "+comp2[4]+" "+comp2[5]+"\n")
						elif(comp1[1] in deleted and lamb_tot > 0):
							l = math.pow((surface_tot * math.pow((2*RM/RI), 1/2) / (2*math.pi*lamb_tot)), (2/3))
							r = lamb_tot*math.pow(l, 1/2)/ math.pow(2*RM/RI, .5)
							x = 0.0
							y = 0.0
							z = 0.0
							for comp in tobecondensed:
								x = x + float(comp[2])
								y = y + float(comp[3])
								z = z + float(comp[4])
							#print(x, y, z)
							if((x-float(comp1[2]) > 0)):
								theta = np.arctan((y-float(comp1[3]))/(x-float(comp1[2])))
							else:
								theta = 0
							if(math.pow((z-float(comp1[4])), 2) > 0):
								phi = np.arctan(math.pow(((x-float(comp1[2]))**2 + (y-float(comp1[3]))**2), 1/2)/ math.pow((z-float(comp1[4])), 2))
							else:
								phi = 0
							x = l*math.cos(theta)*math.sin(phi) + float(comp1[2])
							y = l*math.sin(theta)*math.sin(phi) + float(comp1[3])
							z = l*math.cos(phi) + float(comp1[4])
							output_file.write(comp1[0]+" "+deleted[comp1[1]]+" "+str(x)+" "+str(y)+" "+str(z)+" "+str(r)+"\n")
							tobecondensed = []
							lamb_tot = 0
							surface_tot = 0
						else:
							lamb_tot = 0
							surface_tot = 0
							output_file.write(line)
					elif(comp1[1] in deleted):
						print(comp1[1])
						output_file.write(comp1[0]+" "+deleted[comp1[1]]+" "+comp1[2]+" "+comp1[3]+" "+comp1[4]+" "+comp1[5]+"\n")
					else:
						#check if it has the same radius as the next branch before deciding to write to output 

						output_file.write(line)
			# elif(type1 == "dc"):#condenses branches with same radius and minimum electronic length of .01 lambda [DC]
			# 	dc = dc_factor * math.sqrt(float(comp2[5]))
			# 	if(len(comp1) == 6):
			# 		if(comp1[5] == comp2[5]):#if the radius is the same

			# 			len_comp1 = (math.pow(float(comp1[2]),2.0)+math.pow(float(comp1[3]),2.0)+math.pow(float(comp1[4]),2.0))/ac #electronic length of compartment 1
			# 			len_comp2 = (math.pow(float(comp2[2]),2.0)+math.pow(float(comp2[3]),2.0)+math.pow(float(comp2[4]),2.0))/ac #electronic length of compartment 2
			# 			#print(len_comp1+len_comp2)
			# 			if((len_comp2+len_comp1) < lamb):#if it is less then the designated lambada value then condense branch
			# 				output_file.write(comp2[0]+" "+comp1[1]+" "+comp2[2]+" "+comp2[3]+" "+comp2[4]+" "+comp2[5]+"\n")
			# 			else:

			# 				output_file.write(line)
			# 		else:
			# 			#check if it has the same radius as the next branch before deciding to write to output file
			# 			line_num = input_file.index(line)
			# 			future = input_file[line_num+1].split()
			# 			if(future[5] == comp2[5]):
			# 				k = 1#filler
			# 			else:
			# 				output_file.write(line)

		elif("/" in comp2[0] or "*" in comp2[0]):#for comments and global variables
			output_file.write(line)


def main():

	#array of variables 
	variables = [type1, rm, ri, cm, f, lamb]

	#reads p file
	input_file = open(in_name, 'r').readlines()
	output_file = open(out_name, 'w')


	#sets up arg parser for all the variables 
	parser = argparse.ArgumentParser()
	parser.add_argument('--type', choices={'ac', 'dc', '0'}, default='radii')
	parser.add_argument('--rm', default=rm)
	parser.add_argument('--ri', default=ri)
	parser.add_argument('--cm', default=cm)
	parser.add_argument('--f', default=f)
	parser.add_argument('--lamb', default=lamb)

	#takes values from arg parser and adds them to the variable array 
	h = parser.parse_args()
	variables[0] = h.type
	variables[1] = h.rm
	variables[2] = h.ri
	variables[3] = h.cm
	variables[4] = h.f
	variables[5] = h.lamb


	condenser(input_file, output_file, variables[0], variables[1], variables[2], variables[3], variables[4])


main()


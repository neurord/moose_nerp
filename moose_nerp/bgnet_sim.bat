
####################################### whole basal ganglia network simulations ##############################
#repeat simulations with (a) FSI inputs to SPN gaba2 (Erev=-80) instead of gaba (and reduce num_conn to 1 to compensate), and fix SPN gaba shortage
#		    	     the goal is for lower FSI firing to allow faster or earlier SPN firing
#                        (b) smaller asymmetry in inhibition to D1 SPN
#                        (c) 20% larger weight from D2 to GPe
#python3 bg_net/multisim.py --trials 10 --stoptask True --fb_npas 3 --fb_lhx 5 -dur 0.05 -stn 73 -ramp 0.3 -ctx 55 -t 3.0
#python3 bg_net/multisim.py --trials 10 --stoptask True --fb_npas 3 --fb_lhx 5 -dur 0.05 -stn 73 -ramp 0.5 -ctx 30 -t 3.0
#python3 bg_net/multisim.py --trials 10 --stoptask True --fb_npas 0 --fb_lhx 5 -dur 0.05 -stn 73 -ramp 0.3 -ctx 55 -t 3.0 
#python3 bg_net/multisim.py --trials 10 --stoptask True --fb_npas 0 --fb_lhx 5 -dur 0.05 -stn 73 -ramp 0.5 -ctx 30 -t 3.0

#python3 bg_net/multisim.py --trials 10 --stoptask True --fb_npas 3 --fb_lhx 0 -dur 0.05 -stn 73 -ramp 0.3 -ctx 55 -t 3.0 
#python3 bg_net/multisim.py --trials 10 --stoptask True --fb_npas 3 --fb_lhx 0 -dur 0.05 -stn 73 -ramp 0.5 -ctx 30 -t 3.0
#python3 bg_net/multisim.py --trials 10 --stoptask True --fb_npas 0 --fb_lhx 0 -dur 0.05 -stn 73 -ramp 0.3 -ctx 55 -t 3.0
#python3 bg_net/multisim.py --trials 10 --stoptask True --fb_npas 0 --fb_lhx 0 -dur 0.05 -stn 73 -ramp 0.5 -ctx 30 -t 3.0

#python3 bg_net/multisim.py --trials 10 --stoptask 0 --fb_npas 0 --fb_lhx 0 -stn 28.0 -ctx 10.0 -t 4.0 
#python3 bg_net/multisim.py --trials 10 --stoptask 0 --fb_npas 3 --fb_lhx 0 -stn 28.0 -ctx 10.0 -t 4.0
#python3 bg_net/multisim.py --trials 10 --stoptask 0 --fb_npas 0 --fb_lhx 5 -stn 28.0 -ctx 10.0 -t 4.0 
#python3 bg_net/multisim.py --trials 10 --stoptask 0 --fb_npas 3 --fb_lhx 5 -stn 28.0 -ctx 10.0 -t 4.0

#python3 bg_net/multisim.py --trials 10 --stoptask 0 --fb_npas 3 --fb_lhx 0 -stn 28.0 -ctx 10.0 -t 4.0 --FSI '00' 
#python3 bg_net/multisim.py --trials 10 --stoptask 0 --fb_npas 3 --fb_lhx 5 -stn 28.0 -ctx 10.0 -t 4.0 --FSI '00'

#python3 bg_net/multisim.py --trials 7 --stoptask True --fb_npas 3 --fb_lhx 5 -dur 0.1 -stn 73 -ramp 0.3 -ctx 50
#python3 bg_net/multisim.py --trials 7 --stoptask True --fb_npas 3 --fb_lhx 5 -dur 0.1 -stn 73 -ramp 0.5 -ctx 25

#python3 bg_net/multisim.py --trials 3 --stoptask 0 --fb_npas 0 --fb_lhx 0 -stn 28.0 -ctx 10.0 -t 1.2 &
#python3 bg_net/multisim.py --trials 3 --stoptask 0 --fb_npas 3 --fb_lhx 0 -stn 28.0 -ctx 10.0 -t 1.2 &
#python3 bg_net/multisim.py --trials 3 --stoptask 0 --fb_npas 0 --fb_lhx 5 -stn 28.0 -ctx 10.0 -t 1.2 &
#python3 bg_net/multisim.py --trials 3 --stoptask 0 --fb_npas 3 --fb_lhx 5 -stn 28.0 -ctx 10.0 -t 1.2 --FSI '10' &
#python3 bg_net/multisim.py --trials 3 --stoptask 0 --fb_npas 3 --fb_lhx 0 -stn 28.0 -ctx 10.0 -t 1.2 --FSI '10' &

 

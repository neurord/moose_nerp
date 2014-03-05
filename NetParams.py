#NetParams.py

netsizeX=3
netsizeY=3
fractionD1=0.5
spacing=25e-6
MSNconnSpaceConst=95e-6
###############Can be expanded with connection prob from FS quite easily
D1from={'same':95e-6,'diff':95e-6}
D2from={'same':95e-6,'diff':95e-6}
SpaceConst={'D1':D1from,'D2':D2from}

# m/sec - GABA and the Basal Ganglia by Tepper et al
cond_vel=0.8
mindelay=1e-3

infile='A4B4jit1ms.npz'
confile='NetConn'+infile
outspikefile='MSNout'+infile

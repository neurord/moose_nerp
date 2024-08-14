import glob
import os
filenames=glob.glob('*exp50.txt')

for fname in filenames:
    outfname=os.path.splitext(fname)[0]+'_dist.txt'
    outfile = open(outfname, 'w')
    outfile.write('seed  mean_dist  std_dist cluster dist')
    with open(fname) as fopen:
        for line in fopen:
            if line.startswith('Adding additional inputs from BLA'):
                outfile.write(line.split('[')[-1].split(']')[0]+'\n')
            elif line.startswith('Input Path Distance'):
                outfile.write(line.split('=')[1].split('count')[0])
            elif line.startswith('clustered stim for seed'):
                outfile.write(line.split('seed')[-1][0:-1])
    outfile.close()

//UNITS: micros for x,y,d dia, SI otherwise
*absolute
*asymmetric
*cartesian
*origin 0     0       0

*set_global EREST_ACT   -0.060

*set_compt_param RM	5
*set_compt_param RA	5
*set_compt_param CM	0.007
*set_compt_param ELEAK	-0.056


soma            none            0       0       0      13.4


axon 	soma 	-40 0 0 2.25


p0b1  			soma      	16.1  0  0  1.429
p0b1b1			p0b1		103.8  0  0  1.25
p0b1b1b1		p0b1b1		125.8  0  0  1.364
p0b1b1b2		p0b1b1		242.9  0  0  0.991
p0b1b1b2b1		p0b1b1b2	302.1  0  0  0.966
p0b1b1b2b1b1		p0b1b1b2b1	316  0  0  1.256
p0b1b1b2b1b1b1		p0b1b1b2b1b1	322  0  0  1.172
p0b1b1b2b1b1b2		p0b1b1b2b1b1	325.7  0  0  0.913
p0b1b1b2b1b2		p0b1b1b2b1	329.8  0  0  0.859
p0b1b1b2b2		p0b1b1b2	292.8  0  0  0.753
p0b1b2			p0b1		210.5  0  0  0.700

p1			soma		166  0  0  1.430
p1b1			p1		191.4  0  0  1.268
p1b1b1			p1b1		195.2  0  0  1.048
p1b1b2			p1b1		277  0  0  1.228
p1b1b2b1		p1b1b2		290.8  0  0  0.697
p1b1b2b2		p1b1b2		293.8  0  0  0.660
p1b2			p1		231.9  0  0  0.622
p1b2b1			p1b2		262.7  0  0  0.498
p1b2b1b1		p1b2b1		271.5  0  0  0.465
p1b2b1b2		p1b2b1		277.5  0  0  0.472
p1b2b2			p1b2		289  0  0  0.428

p2b2			soma		61.1  0  0  2.078
p2b2b1			p2b2		84.2  0  0  1.519
p2b2b1b1		p2b2b1		287.6  0  0  0.481
p2b2b1b2		p2b2b1		153.8  0  0  1.490
p2b2b1b2b1		p2b2b1b2	554  0  0  0.533
p2b2b1b2b2		p2b2b1b2	161.5  0  0  1.651
p2b2b1b2b2b1		p2b2b1b2b2	308  0  0  0.443
p2b2b1b2b2b2		p2b2b1b2b2	242.4  0  0  1.036
p2b2b1b2b2b2b1		p2b2b1b2b2b2	281.3  0  0  0.572
p2b2b1b2b2b2b2		p2b2b1b2b2b2	289.8  0  0  0.790
p2b2b1b2b2b2b2b1	p2b2b1b2b2b2b2	316.5  0  0  0.730
p2b2b1b2b2b2b2b2	p2b2b1b2b2b2b2	307  0  0  0.795
p2b2b2			p2b2		350.9  0  0  1.070
p2b2b2b1		p2b2b2		402.8  0  0  0.765
p2b2b2b1b1		p2b2b2b1	412.8  0  0  0.436
p2b2b2b1b2		p2b2b2b1	434.8  0  0  0.776
p2b2b2b2		p2b2b2		463.7  0  0  0.596


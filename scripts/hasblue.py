import PIL.Image, sys

img = PIL.Image.open(open(sys.argv[1]))
width = img.size[0]
for i,p in enumerate(img.getdata()):
	if i % width == 0:
		sys.stdout.write('\n')
	sys.stdout.write('%02s' % (p))
sys.stdout.write('\n')

print img.mode
pt,pd = img.palette.getdata()
print pt
print 'pallete len:',len(pd)
for i in range(len(pd)/3):
	s = pd[i*3:i*3+3]
	if s != '\x00\x00\x00':
		print i,repr(s)

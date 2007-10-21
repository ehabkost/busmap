import horarios

import sys


fh = sys.stdout
for pto,dias,apartir,horas in horarios.parse_hor_html(sys.stdin.read()):
	fh.write("Ponto: %s - %s\nValido a partir de: %s\n\n" \
			% (pto,dias,apartir))
	l = 0
	for sp,h in horas:
		if sp: bold='*'
		else: bold=''

		s = "%s%s " % (bold, h)

		# break lines
		l += len(s)
		if l > 80:
			l = len(s)
			s = '\n' + s
		fh.write(s)
	fh.write("\n\n\n")

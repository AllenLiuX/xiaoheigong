import os
import sys

if os.path.isfile('/usr/bin/pdftotext'):
	pass
else:
	sys.exit("Did not detect correctly installed xpdf. Please follow install instructions at: https://github.com/ecatkins/xpdf_python.")

import os
import sys

# if on mac, it should be /usr/local/bin/pdftotext
# if on linux, it should be /usr/bin/pdftotext
if os.path.isfile('/usr/local/bin/pdftotext'):
	pass
else:
	sys.exit("Did not detect correctly installed xpdf. Please follow install instructions at: https://github.com/ecatkins/xpdf_python.")

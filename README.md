* This is a script for the preparation of data for Mapflow plugin *

The mapflow models require 8-bit RBG images.
The preprocessing of the 16-bit and\or multispectal data can be carried out with your own tools, but we recommend
to use our script for better results.


* Requirements *

Python 3.4


* Installation *

Open terminal in this folder and run
```bash
pip install -r requirements.txt
'''


* Running *

```bash
python to8bit.py {{input}} {{output}} [--channels {R G B}]
'''
input, output - absolute or relative paths to input and output tif files
--channels - optional argument to specify the R,G,B channel positions in the file. Defaults to "1 2 3"
Example, running the data preprocessing for multispectral image where red is channel 4, green - channel 3, blue - channel 2:

```bash
python to8bit.py ./input.tif ./output.tif --channels 4 3 2
'''


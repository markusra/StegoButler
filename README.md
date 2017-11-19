# StegoButler

StegoButler is a tool that automates the bulk creation of steganography with [OpenStego](https://github.com/syvaidya/openstego) and the analysis of the resulting stego files using [StegExpose](https://github.com/b3dk7/StegExpose).

### Requirements

StegoButler needs [Python 2.7.x](https://www.python.org/downloads/) in order to work.

### Installation

Install all required Python modules with:

```
pip install -r requirements.txt
```

### Usage
Run the tool with:

```
python StegoButler.py
```

You can modify which cover and message files OpenStego will use to create stego files using the global variables:

```
messageFolder       = "messageFiles/"
messageFiles        = ["text1.txt"]

coverFolder         = "images/"
coverFileSizes      = ["", "@0,8x", "@0,6x", "@0,4x", "@0,2x"]
coverFiles          = ["beach", "candy", "car", "eagle", "fruit", "hong_kong", "man", "sculpture", "skyscraper",
                      "vegetables"]
```

## License

GNU General Public License 2.0 (GPL) (see ```LICENSE``` file)

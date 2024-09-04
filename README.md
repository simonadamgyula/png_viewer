# PNG viewer in python
![Screenshot of running app](https://github.com/simonadamgyula/png_viewer/blob/cab580f5ca7209e68af53cb41025fd86fd8295b2/screenshot.png)

This project was made for me to learn how png encoding worked

## Usage
1. Install the pygame module (``` pip install pygame ```)
2. Run ``` poetry install ```, than ``` peotry shell ``` to install dependencies, and go to the virtual environment shell.
3. Run ``` main.py ```

The viewer can read png-s with all color types that are non-interlaced and have less than 16 bit color depth, which should be most of them, but not all. So if you run into an error it's likely do to that.

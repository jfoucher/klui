## Klui 

Klui is a terminal based interface to the [klipper](https://www.klipper3d.org) 3D printer firmware, or rather the [moonraker](https://github.com/Arksine/moonraker) server that often runs alongside it.

I started working on this to be able to control my printer from an old computer I have lying around, with which using the mainsail web UI is a chore because it's so slow.

Hopefully this will be better.

Install dependencies by running `pip install -r requirements.txt`

You can connect to any moonraker server with it, just run it like so :

`python3 main.py 192.168.1.44`

replacing 192.168.1.44 by the ip or server name of your moonraker server.

## Features

- View all the reported temperatures and change their targets, for both heaters and temperature fans.
- Home X, Y and Z axes (I do not have another type of printer to test)
- View the position of X Y and Z axes
- Do a quad gantry leveling procedure if your printer supports it
- Show the status of the printer (printing or not, homed, QGL, filament sensors, steppers active, system load)
- Press F1 in the app to view some help text

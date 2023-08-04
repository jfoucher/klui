## Klui 

Klui is a terminal based interface to the klipper 3D printer firmware, or rather the moonraker server that often runs alongside it.

I started working on this to be able to control my computer from an old computer I have lying around, with which using the mainsail web UI is a chore because it's so slow.

Hopefully this will be better.

Install dependencies by running `pip install -r requirements.txt`

You can connect to any moonraker server with it, just run it like so :

`python3 main.py 192.168.1.44`

replacing 192.168.1.44 by the ip or server name of your moonraker server.

For now the only thing that you can do is see and control the heater temperatures.

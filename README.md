# Trash Items Counter

This is a simple pet-project. It's counting items in your trash folder and prints it to the 4-digits 7-segment display. It is working on *Linux* and *Windows*.

> It can also counts files in any directory provided by -d flag

By using this code you can create your own device, that will display anything you need, so feel free to try it.

## Hardware

As a hardware I am using *Arduino Nano* and *TM1637* green display.

## Linux

### Usage

If you want to run it manually then you have to provide either *username* or *directory*.

To provide username use: `python3 src/Counter.py -u $USER`

To provide directory use: `python3 src/Counter.py -d <directory>`

You can also specify port device connected to by using `-p` flag.

Example: `python3 src/Counter.py -d <directory> -p /dev/ttyUSB1`

By default */dev/ttyUSB0* is using.

If you want to run it as a daemon service (see below) but with custom flag options then change `ExecStart` item in the [trash-items-counter@.service](Linux/trash-items-counter@.service)

### Installing

Run the next commands:

```bash
cd Linux
sudo pip3 install pyserial pyinotify
chmod +x install.sh
sudo ./install.sh
```

### Running

To enable running scipt on startup run the following:

```bash
sudo systemctl enable trash-items-counter@$USER.service
```

If you want to start it only now run this instead:

```bash
sudo systemctl start trash-items-counter@$USER.service
```

### Stopping

```bash
sudo systemctl stop trash-items-counter@$USER.service
```

## Windows

### Installing

To run program on startup follow the next steps:

1. Create a shorcut for *[Counter.bat](Windows/Counter.bat)*
2. Hit *Win+R* and type *shell:startup*
3. Copy shortcut to the openned Strartup folder

## Lego

Use [instruction](Lego/instruction.html) to build your Lego corpus.

## Image

![](Corpus.jpg)

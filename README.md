# Linux

## Installing

Run the next commands:

```bash
cd Linux
sudo pip3 install pyserial pyinotify
chmod +x install.sh
sudo ./install.sh
```

## Running

To enable running scipt on startup run the following:

```bash
sudo systemctl enable trash-items-counter@$USER.service
```

If you want to start it only now run this instead:

```bash
sudo systemctl start trash-items-counter@$USER.service
```

## Stopping

```bash
sudo systemctl stop trash-items-counter@$USER.service
```

# Windows

## Installing

To run program on startup follow the next steps:

1. Create a shorcut for *[Counter.bat](Windows/Counter.bat)*
2. Hit *Win+R* and type *shell:startup*
3. Copy shortcut to the openned Strartup folder

# Lego

Use [instruction](Lego/instruction.html) to build your Lego corpus.

# Images

![](Corpus.jpg)

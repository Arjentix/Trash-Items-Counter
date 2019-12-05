# Linux

## Installing

Run the next commands:

```bash
cd Linux
chmod +x install.sh
sudo ./install.sh
```

## Running

To enable running scipt on startup run the following:

```bash
sudo systemctl enable trash-items-counter@$USER.service
```

If you want start it only now run this instead:

```bash
sudo systemctl start trash-items-counter@$USER.service
```

## Stopping

```bash
sudo systemctl stop trash-items-counter@$USER.service
```

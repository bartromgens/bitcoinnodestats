# bitcoinnodestats
[![Dependency Status](https://gemnasium.com/badges/github.com/bartromgens/bitcoinnodestats.svg)](https://gemnasium.com/github.com/bartromgens/bitcoinnodestats)

A basic Bitcoin node status and statistics web application.

Based on [Django](https://www.djangoproject.com/), [python-bitcoinlib](https://github.com/petertodd/python-bitcoinlib),  [D3js](https://github.com/mbostock/d3), and [bootstrap](https://github.com/twbs/bootstrap).  
Requires Python 3.3+.

### Demo

**[bitcoinnodestats.romgens.com](http://bitcoinnodestats.romgens.com)**

### Features
- Current node status overview
- Charts of peer count, upload and download history
- Save node status snapshots at given time intervals to a sqlite database

### Installation (Linux)

##### Download and Install
Get the code and enter the project directory,  
```
$ git clone https://github.com/bartromgens/bitcoinnodestats.git
$ cd bitcoinnodestats
```

Install in a local environment (creates a Python 3 virtualenv and a sqlite database),  
```$ ./install.sh```

##### Schedule status snapshots (cronjob)
Create a cronjob to record node status every n minutes,  
```
$ crontab -e
```  
To create a status record every hour, add the following line and replace the placeholders with your project location,  
```
0 * * * * source /home/<user>/<projectdir>/env/bin/activate && python /home/<user>/<projectdir>/manage.py runcrons > /home/<user>/<projectdir>/cronjob.log 2>&1
```  
Warning: you may need to define `SHELL=/bin/bash` at the top of your crontab for the command to work. 

Please create a [new issue](https://github.com/bartromgens/bitcoinnodestats/issues/new) if you have any problems with the installation.

### Run
Run the simple Django web server (not for production) for a given IP and port,  
```
$ ./run.sh 127.0.0.1:8000
```

Visit http://127.0.0.1:8000 in your browser to view your node stats.

### Configuration
`bitcoinnodestats/local_settings.py` contains some local settings that you may want or need to change if you run it on a production server.

`BITCOIN_CONF_FILE` is the location of your `bitcoin.conf`, only needed if it is not in the default location. 

`DEBUG` should be set to False on a production server.  

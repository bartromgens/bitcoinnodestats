# bitcoinnodestats

A basic bitcoin node status and statistics web application.

Shows charts with connection count, outgoing/incoming data, and upload/download speeds versus time.  
Stores node status snapshots in a sqlite database to preserve data after node restart.

Based on [Django](https://www.djangoproject.com/), [python-bitcoinlib](https://github.com/petertodd/python-bitcoinlib), and [D3js](https://github.com/mbostock/d3).

### Demo

**[bitcoinnodestats.romgens.com](http://bitcoinnodestats.romgens.com)**

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
```$ crontab -e```  
To create a status record every 10 minutes, add the following line and replace the placeholders with your project location,  
```*/10 * * * * source /home/<user>/<projectdir>/env/bin/activate && python /home/<user>/<projectdir>/manage.py runcrons > /home/<user>/<projectdir>/cronjob.log 2>&1```  
Warning: you may need to define `SHELL=/bin/bash` at the top of your crontab for the command to work. 

Please create a ticket if you have any problems with the installation.

### Run
Run the simple Django web server (not for production) for a given IP and port,  
```$ ./run.sh 127.0.0.1:8000```

Visit http://127.0.0.1:8000 in your browser to view your node stats.  
Note that it will takes some time before enough data is stored for the charts. 

### Configuration
`bitcoinnodestats/local_settings.py` contains some local settings that you may want or need to change if you run it on a production server.

`BITCOIN_CONF_FILE` is the location of your 'bitcoin.conf', only needed if it is not in the default location. 

`DEBUG` should be set to False on a production server.  

### TODO
- Users can change the plot date range
- Users can change plot detail
- Responsive plots (rescale on window resize)
- ...

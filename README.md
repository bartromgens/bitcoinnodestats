# bitcoinnodestats

A basic and light bitcoin node status and statistics web application.

Shows charts with connection count, outgoing/incoming data, and upload/download speeds versus time.  
Stores node status snapshots in a sqlite database to preserve data after node restart.

Based on [Django](https://www.djangoproject.com/), [python-bitcoinlib](https://github.com/petertodd/python-bitcoinlib), and [D3js](https://github.com/mbostock/d3).

### Installation (Linux)
Get the code and enter the project directory,  
```
$ git clone https://github.com/bartromgens/bitcoinnodestats.git
$ cd bitcoinnodestats
```

Install in a local environement (creates a Python 3 virtualenv and a sqlite database),  
```$ ./install.sh```

Run the simple Django web server (not for production) for a given IP and port,  
```$ ./run.sh 127.0.0.1:8000```

Create a cronjob to update the data every n minutes,  
```$ crontab -e```  
and add the following line at the end and replace the placeholders with your project location,  
```*/5 * * * * source /home/<user>/<projectdir>/env/bin/activate && python /home/<user>/<projectdir>/manage.py runcrons > /home/<user>/<projectdir>/cronjob.log 2>&1```

Visit http://127.0.0.1:8000 in your browser to view your node stats. Note that it will takes some time before enough data is stored for the charts. 

Please create a ticket if you have any problems with the installation.

### TODO
- Change UTC to local time
- Improve tooltip readability
- Make update interval configurable 
- Make plot detail configurable
- ...

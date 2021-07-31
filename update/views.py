from django.shortcuts import render

# Create your views here.
def status_route():
	''' Node Configuration '''
	script = 'main.py'
	ingest_type = os.environ['INGEST_TYPE']
	active_status = 0 #lookup process
	active_version = 0 #lookup process
	active_web_version = 0 #lookup process
	for process in psutil.process_iter():
		if process.cmdline() == ['python', f'{script}']:
			active_status = "Running"
		else:
			active_status = "Not Detected"
	''' TIME '''
	delta = datetime.now().replace(microsecond=0) - datetime.fromtimestamp(psutil.boot_time())
	uptime = str(delta)
	now = datetime.now()
	active_time = now.strftime("%b/%d/%Y %H:%M:%S")
	''' PERFORMANCE '''
	load_avg = f"{psutil.getloadavg()[0]}, {psutil.getloadavg()[1]}, {psutil.getloadavg()[2]}" #(0.18, 0.11, 0.1)
	''' NETWORK '''
	netinfo = psutil.net_if_addrs() #wlan0 -- needs to be in config
	netip = str(netinfo["wlan0"][0])
	ip = re.search('(\d+\.\d+\.\d+\.\d*)', netip)
	ip_address = ip.group(1)
	hostname = socket.gethostname()
	#check nslookup forward and reverse
	''' UNDER SYSTEM '''
	kernel_cmd = subprocess.run(["uname", "-r"], capture_output=True, text=True)
	kernel = kernel_cmd.stdout
	operating_system_cmd = subprocess.run(["lsb_release", "-ds"], capture_output=True, text=True)
	operating_system = operating_system_cmd.stdout
	py_version = ".".join(map(str, sys.version_info[:3]))
	with open('/proc/1/cgroup', 'rt') as container_detect:
		if "docker" in container_detect.read():
			container_type = "Docker"
		elif "kubepods" or "kubepod" in container_detect.read():
			container_type = "Kubernetes"
		elif "lxc" in container_detect.read():
			container_type = "LXC"

	return ({
		"Ingest Type": f"{ingest_type}",
		"Status": f"{active_status}",
		"Version": f"{active_version}",
		"API Version": f"{active_web_version}",
		"Uptime": f"{uptime}",
		"Time": f"{active_time}",
		"Load Average": f"{load_avg}",
		"IP Address": f"{ip_address}",
		"Hostname": f"{hostname}",
		"Platform": f"{container_type}", 
		"Kernel": f"{kernel}",
		"Operating System": f"{operating_system}",
		"Python Version": f"{py_version}"
		})

#######
# CONVERT FROM FLASK
#######
@app.route('/stopstart', methods=["GET"])
def stopstart():
	if process.cmdline() == ['python', 'main.py']:
		flash("Stopping Now!", "info")
		check_call(["pkill", "-9", "-f", main.py])
		return redirect(request.url)
	else:
		flash("Starting Now!", "info")
		subprocess.run("sudo python3 ~/nhl-led-scoreboard/src/main.py --led-gpio-mapping=adafruit-hat --led-brightness=60 --led-slowdown-gpio=2 --updatecheck=True")
		return redirect(request.url)

@app.route('/reload', methods=["GET"])
def reload():
	flash("Reloading Now!", "info")
	os.execl(sys.executable, '"{}"'.format(sys.executable), *sys.argv)
	time.sleep(3)
	return redirect(request.url)

@app.route('/reset', methods=["GET"])
def reset():
	flash("Resetting Now!", "info")
	killer = check_call(["pkill", "-9", "-f", main.py])
	if killer.stdout == 0:
		#upgrade to subprocess command
		#os.system("sudo python3 ~/nhl-led-scoreboard/src/main.py --led-gpio-mapping=adafruit-hat --led-brightness=60 --led-slowdown-gpio=2 --updatecheck=True")
		subprocess.run("sudo python3 ~/nhl-led-scoreboard/src/main.py --led-gpio-mapping=adafruit-hat --led-brightness=60 --led-slowdown-gpio=2 --updatecheck=True")
		time.sleep(3)
		return redirect(request.url)
	else:
		flash("Failed to kill process", "error")
		return redirect(request.url)

@app.route('/restart', methods=["GET"])
def restart():
	flash("Restarting in 3 Seconds!", "info")
	os.system("shutdown /r /t 3")
	return redirect(request.url)
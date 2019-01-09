import threading
from ._base import BaseMonitor
from ._moverpositionmonitor import MoverPositionMonitor


def _start_monitor(*args,**kwargs):
	m = kwargs.get('monitor')(*args,**kwargs)
	m.run()
	return m


def launch_monitor_as_thread(*args,**kwargs):
	t = threading.Thread(target=_start_monitor,args=args,kwargs=kwargs)
	daemon = kwargs.get('daemon',True) #set as daemon unless explicitly told not to
	t.setDaemon(daemon)
	t.start()
	return t


if __name__ == "__main__":
	import time
	t = launch_monitor_as_thread(monitor=BaseMonitor,function=print,parameters={'args':['derp'],'kwargs':{'end':'\t'}},sleeptime=1)
	time.sleep(5)
	print('fin')
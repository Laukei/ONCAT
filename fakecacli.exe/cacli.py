import sys
import sqlite3
import math
import time


def create_db():
	try:
		idcode = 'INTEGER PRIMARY KEY AUTOINCREMENT'
		states_dict = {
		'id':idcode,
		'pos1':'INTEGER',
		'pos2':'INTEGER',
		'pos3':'INTEGER',
		'rvl1':'INTEGER',
		'rvl2':'INTEGER',
		'rvl3':'INTEGER',
		'time':'INTEGER'
		}
		states = ''
		for key in ['id','pos1','pos2','pos3','rvl1','rvl2','rvl3','time']:
			states += '{} {},\n'.format(key,states_dict[key])
		states = states[:-2]

		db = connect_db()
		cur = db.cursor()
		db.execute('CREATE TABLE cacli('+states+')')
		db.commit()
		db.close()
		_set_values(None)

	except sqlite3.OperationalError:
		pass


def _get_values():
	db = connect_db()
	c = db.cursor()
	c.execute('SELECT id, pos1, pos2, pos3, rvl1, rvl2, rvl3, time FROM cacli ORDER BY id DESC LIMIT 1')
	return list(c.fetchone())
	
def POS(addr,ch):
	vals = _get_values()
	return 'POS: {}\nRVL: {}'.format(int(vals[int(addr)]),vals[int(addr)+3])

def EXT(addr,ch,type_,temp,dir,freq,rel,trqfr=None):
	return 'STATUS : USING EXTERNAL INPUT'

def MOV(addr,ch,type_,temp,dir_,freq,rel,steps,trqfr=None):
	vals = _get_values()
	direction = -1 if int(dir_) == 0 else 1
	vals[int(addr)] += (direction * int(freq) * int(rel) * int(steps)) / float(1e6)
	if vals[int(addr)] > 460:
		vals[int(addr)] = 460
	if vals[int(addr)] < 0:
		vals[int(addr)] = 0
	vals[int(addr)+3] = int((math.sin(vals[int(addr)]*6.28)+1)/2 * 255)
	_set_values(vals)
	return 'STATUS : MOVE'

def STP(addr):
	return 'STATUS : STOP'

def STS(addr):
	vals = _get_values()
	if time.time() - vals[7] > 1:
		return 'STATUS : STOP\nFAILSAFE STATE: 0x0'
	else:
		return 'STATUS : MOVE\nFAILSAFE STATE: 0x0'

def INFO(addr,ch):
	return 'TYPE : CA1801\nTAG  : NONE'

def RST(addr,ch):
	vals = _get_values()
	vals[int(addr)] = 0
	vals[int(addr)+3] = 0
	_set_values(vals)
	return 'Counter for CH{} has been reset to zero'.format(addr)

def OEMC(addr,ch,type_,temp,dir_,freq):
	while True:
		pass

def DESC(addr):
	return 'Version : CADM2\nAvailable Channels: 1'

def FBEN(pgain,type_,temp,trqfr=None):
	return 'STATUS : POSITION CONTROL ENABLED'

def FBXT():
	return 'STATUS : POSITION CONTROL DISABLED'

def FBCS(sp1,sp2,sp3):
	return 'STATUS : POSITION CONTROL SET'

def FBES():
	return 'STATUS : POSITION CONTROL STOPPED'

def FBFE(dir_,filter,zero):
	return 'STATUS : POSITION CONTROL FIND ENDSTOP'

def FBST():
	vals = _get_values()
	return 'STATUS : POSITION CONTROL INQUIRY\nENABLED: 1\nBUSY:0\nPOS1:{}\nPOS2:{}\nPOS3:{}\nERR1:0\nERR2:0\nERR3:0'.format(vals[1],vals[2],vals[3])


def _set_values(previous,**kwargs):
	if previous == None:
		pos1 = 0
		pos2 = 0
		pos3 = 0
		rvl1 = 0
		rvl2 = 0
		rvl3 = 0
	else:
		pos1 = kwargs.get('pos1',previous[1])
		pos2 = kwargs.get('pos2',previous[2])
		pos3 = kwargs.get('pos3',previous[3])
		rvl1 = kwargs.get('rvl1',previous[4])
		rvl2 = kwargs.get('rvl2',previous[5])
		rvl3 = kwargs.get('rvl3',previous[6])
	time_ = int(time.time())
	db = connect_db()
	c = db.cursor()
	c.execute('INSERT INTO cacli(pos1,pos2,pos3,rvl1,rvl2,rvl3,time) VALUES(?,?,?,?,?,?,?)',
			(pos1,pos2,pos3,rvl1,rvl2,rvl3,time_))
	db.commit()
	db.close()


def connect_db():
	db = sqlite3.connect('cacli.db')
	return db


def process_input(argv):
	create_db()
	args = argv[:]
	try:
		args.pop(0)
		if '@' in args[0]:
			args.pop(0)
		return args
	except IndexError:
		error()


def error(*args,**kwargs):
	return 'Unable to comply'


def handler(args):
	called_func = globals().get(args[0],error)
	print(called_func(*args[1:]))


def main():
	handler(process_input(sys.argv))



if __name__ == "__main__":
	main()
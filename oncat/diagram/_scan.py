import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.transforms as transforms
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

XOPT_MAX = 5.0 #mm
YOPT_MAX = 5.0 #mm

class Scan:
	def __init__(self,Xopt=None,Yopt=None,limits={},**kwargs):
		'''
		arguments: *X, *Y, *Xopt, *Yopt, *limits, **kwargs
		'''
		super().__init__()
		self._Xopt_max = kwargs.get('Xopt_max',XOPT_MAX)
		self._Yopt_max = kwargs.get('Yopt_max',YOPT_MAX)
		self._Xopt = Xopt if Xopt is not None else self._Xopt_max/2.0
		self._Yopt = Yopt if Yopt is not None else self._Yopt_max/2.0

		self._fig, self._ax = plt.subplots()
		self._canvas = FigureCanvas(self._fig)
		self._ax.set_xlim(0,self._Xopt_max)
		self._ax.set_ylim(0,self._Yopt_max)
		self._ax.set_xlabel('Xopt (mm)')
		self._ax.set_ylabel('Yopt (mm)')
		self._ax.grid(True)

		self._ax_line, = self._ax.plot([self._Xopt],[self._Yopt],'rx')

		self._limits = limits if limits != {} else kwargs.get('limits',{})
		self.set_limits(limits)
		

	def set_attocube_position(self,Xopt,Yopt):
		'''
		arguments: Xopt, Yopt

		moves position indicator at Xopt, Yopt
		'''
		self._Xopt = Xopt
		self._Yopt = Yopt
		self._ax_line.set_xdata([self._Xopt])
		self._ax_line.set_ydata([self._Yopt])
		#self._canvas.draw_idle()
		#self._canvas.flush_events()s


	def set_limits(self,limits):
		'''
		arguments: limits

		takes dict of limits of form:
			{'Xopt_max':float,
			'Yopt_max':float,
			'Xopt_min':float,
			'Yopt_min':float}
		and applies overlapping squares to these
		'''
		self._ax.patches = []
		self._ax_limits = []
		self._Xopt_max_limit = (limits.get('Xopt_max',self._Xopt_max),self._Xopt_max)
		self._Yopt_max_limit = (limits.get('Yopt_max',self._Yopt_max),self._Yopt_max)
		self._Xopt_min_limit = (limits.get('Xopt_min',0),0)
		self._Yopt_min_limit = (limits.get('Yopt_min',0),0)

		if self._Yopt_max_limit[0] != self._Yopt_max_limit[1]:
			self._ax_limits.append(Rectangle(
				(0,self._Yopt_max_limit[0]),self._Xopt_max,self._Yopt_max-self._Yopt_max_limit[0],fill=True,color='grey'))
		if self._Yopt_min_limit[0] != self._Yopt_min_limit[1]:
			self._ax_limits.append(Rectangle(
				(0,0),self._Xopt_max,self._Yopt_min_limit[0],fill=True,color='grey'))
		if self._Xopt_max_limit[0] != self._Xopt_max_limit[1]:
			self._ax_limits.append(Rectangle(
				(self._Xopt_max_limit[0],self._Yopt_min_limit[0]),self._Xopt_max-self._Xopt_max_limit[0],self._Yopt_max_limit[0]-self._Yopt_min_limit[0],fill=True,color='grey'))
		if self._Xopt_min_limit[0] != self._Xopt_min_limit[1]:
			self._ax_limits.append(Rectangle(
				(0,self._Yopt_min_limit[0]),self._Xopt_min_limit[0],self._Yopt_max_limit[0]-self._Yopt_min_limit[0],fill=True,color='grey'))

		for item in self._ax_limits:
			self._ax.add_patch(item)

	def canvas(self):
		return self._canvas

	def fig(self):
		return self._fig

	def show(self):
		self._fig.show()


	def save(self,filename=None):
		if filename == None:
			filename = 'savefile.png'
		self._fig.savefig(filename)


def main():
	limits = {'Yopt_max':3.3}
	d = Scan(limits=limits)
	d.save('test1.png')
	d.set_attocube_position(.100,.100)
	d.save('test3.png')

if __name__ == "__main__":
	main()
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.transforms as transforms
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.axes._axes import _make_inset_locator

XOPT_MAX = 5.0 #mm
YOPT_MAX = 5.0 #mm
X_MAX = 51.5 #mm
Y_MAX = 51.5 #mm
X_SCALE = X_MAX/490 #mm per point
Y_SCALE = Y_MAX/467 #mm per point

class Diagram:
	def __init__(self,X=None,Y=None,Xopt=None,Yopt=None,limits={},**kwargs):
		'''
		arguments: *X, *Y, *Xopt, *Yopt, *limits, **kwargs
		'''
		super().__init__()
		self._Xopt_max = kwargs.get('Xopt_max',XOPT_MAX)
		self._Yopt_max = kwargs.get('Yopt_max',YOPT_MAX)
		self._X_max = kwargs.get('X_max',X_MAX)
		self._Y_max = kwargs.get('Y_max',Y_MAX)
		self._X_scale = kwargs.get('X_scale',X_SCALE)
		self._Y_scale = kwargs.get('Y_scale',Y_SCALE)
		self._X = X if X is not None else self._X_max/2.0
		self._Y = Y if Y is not None else self._Y_max/2.0
		self._Xopt = Xopt if Xopt is not None else self._Xopt_max/2.0
		self._Yopt = Yopt if Yopt is not None else self._Yopt_max/2.0

		self._fig, self._ax = plt.subplots()
		self._canvas = FigureCanvas(self._fig)
		self._trans = transforms.blended_transform_factory(self._ax.transData, self._ax.transData)
		self._ax2 = self._ax.inset_axes(
			(self._X-self._Xopt_max/2.0,self._Y-self._Yopt_max/2.0,self._Xopt_max,self._Yopt_max),
			transform=self._trans
			)
		self._fig.add_axes(self._ax2)
		self._ax.set_xlim(0,self._X_max)
		self._ax.set_ylim(0,self._Y_max)
		self._ax.set_xlabel('X (mm)')
		self._ax.set_ylabel('Y (mm)')
		self._ax.grid(True)

		self._ax2_line, = self._ax2.plot([self._Xopt],[self._Yopt],'rx')

		self._ax2.set_xlim(0,self._Xopt_max)
		self._ax2.set_ylim(0,self._Yopt_max)

		self._limits = limits if limits != {} else kwargs.get('limits',{})
		self.set_limits(limits)


	def set_janssen_position(self,X,Y):
		'''
		arguments: X, Y

		moves inset figure to position at X, Y; converts using self._X_scale and self._Y_scale
		'''
		self._X = X * self._X_scale
		self._Y = Y * self._Y_scale
		self._ax2.set_axes_locator(_make_inset_locator((self._X-self._Xopt_max/2.0,self._Y-self._Yopt_max/2.0,self._Xopt_max,self._Yopt_max),self._ax.transData,self._ax))
		

	def set_attocube_position(self,Xopt,Yopt):
		'''
		arguments: Xopt, Yopt

		moves position indicator at Xopt, Yopt
		'''
		self._Xopt = Xopt
		self._Yopt = Yopt
		self._ax2_line.set_xdata([self._Xopt])
		self._ax2_line.set_ydata([self._Yopt])
		self._canvas.draw()
		self._canvas.flush_events()


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
		self._ax2.patches = []
		self._ax2_limits = []
		self._Xopt_max_limit = (limits.get('Xopt_max',self._Xopt_max),self._Xopt_max)
		self._Yopt_max_limit = (limits.get('Yopt_max',self._Yopt_max),self._Yopt_max)
		self._Xopt_min_limit = (limits.get('Xopt_min',0),0)
		self._Yopt_min_limit = (limits.get('Yopt_min',0),0)

		if self._Yopt_max_limit[0] != self._Yopt_max_limit[1]:
			self._ax2_limits.append(Rectangle(
				(0,self._Yopt_max_limit[0]),self._Xopt_max,self._Yopt_max-self._Yopt_max_limit[0],fill=True,color='grey'))
		if self._Yopt_min_limit[0] != self._Yopt_min_limit[1]:
			self._ax2_limits.append(Rectangle(
				(0,0),self._Xopt_max,self._Yopt_min_limit[0],fill=True,color='grey'))
		if self._Xopt_max_limit[0] != self._Xopt_max_limit[1]:
			self._ax2_limits.append(Rectangle(
				(self._Xopt_max_limit[0],self._Yopt_min_limit[0]),self._Xopt_max-self._Xopt_max_limit[0],self._Yopt_max_limit[0]-self._Yopt_min_limit[0],fill=True,color='grey'))
		if self._Xopt_min_limit[0] != self._Xopt_min_limit[1]:
			self._ax2_limits.append(Rectangle(
				(0,self._Yopt_min_limit[0]),self._Xopt_min_limit[0],self._Yopt_max_limit[0]-self._Yopt_min_limit[0],fill=True,color='grey'))

		for item in self._ax2_limits:
			self._ax2.add_patch(item)

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
	d = Diagram(limits=limits)
	d.save('test1.png')
	d.set_janssen_position(300,300)
	d.save('test2.png')
	d.set_attocube_position(.100,.100)
	d.save('test3.png')

if __name__ == "__main__":
	main()
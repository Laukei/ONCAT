import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.patches import Rectangle
import matplotlib.transforms as transforms

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
		self.__Xopt_max = kwargs.get('Xopt_max',XOPT_MAX)
		self.__Yopt_max = kwargs.get('Yopt_max',YOPT_MAX)
		self.__X_max = kwargs.get('X_max',X_MAX)
		self.__Y_max = kwargs.get('Y_max',Y_MAX)
		self.__X_scale = kwargs.get('X_scale',X_SCALE)
		self.__Y_scale = kwargs.get('Y_scale',Y_SCALE)
		self.__X = X if X is not None else self.__X_max/2.0
		self.__Y = Y if Y is not None else self.__Y_max/2.0
		self.__Xopt = Xopt if Xopt is not None else self.__Xopt_max/2.0
		self.__Yopt = Yopt if Yopt is not None else self.__Yopt_max/2.0

		self.__fig, self.__ax = plt.subplots()
		self.__trans = transforms.blended_transform_factory(self.__ax.transData, self.__ax.transData)
		self.__ax2 = self.__ax.inset_axes(
			(self.__X-self.__Xopt_max/2.0,self.__Y-self.__Yopt_max/2.0,self.__Xopt_max,self.__Yopt_max),
			transform=self.__trans
			)
		self.__fig.add_axes(self.__ax2)
		self.__ax.set_xlim(0,self.__X_max)
		self.__ax.set_ylim(0,self.__Y_max)
		self.__ax.set_xlabel('X (mm)')
		self.__ax.set_ylabel('Y (mm)')
		self.__ax.grid(True)

		self.__ax2.plot([self.__Xopt],[self.__Yopt],'rx')

		self.__ax2.set_xlim(0,self.__Xopt_max)
		self.__ax2.set_ylim(0,self.__Yopt_max)

		self.__limits = limits if limits != {} else kwargs.get('limits',{})
		self.set_limits(limits)


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
		self.__ax2.patches = []
		self.__ax2_limits = []
		self.__Xopt_max_limit = (limits.get('Xopt_max',self.__Xopt_max),self.__Xopt_max)
		self.__Yopt_max_limit = (limits.get('Yopt_max',self.__Yopt_max),self.__Yopt_max)
		self.__Xopt_min_limit = (limits.get('Xopt_min',0),0)
		self.__Yopt_min_limit = (limits.get('Yopt_min',0),0)

		if self.__Yopt_max_limit[0] != self.__Yopt_max_limit[1]:
			self.__ax2_limits.append(Rectangle(
				(0,self.__Yopt_max_limit[0]),self.__Xopt_max,self.__Yopt_max-self.__Yopt_max_limit[0],fill=True,color='grey'))
		if self.__Yopt_min_limit[0] != self.__Yopt_min_limit[1]:
			self.__ax2_limits.append(Rectangle(
				(0,0),self.__Xopt_max,self.__Yopt_min_limit[0],fill=True,color='grey'))
		if self.__Xopt_max_limit[0] != self.__Xopt_max_limit[1]:
			self.__ax2_limits.append(Rectangle(
				(self.__Xopt_max_limit[0],self.__Yopt_min_limit[0]),self.__Xopt_max-self.__Xopt_max_limit[0],self.__Yopt_max_limit[0]-self.__Yopt_min_limit[0],fill=True,color='grey'))
		if self.__Xopt_min_limit[0] != self.__Xopt_min_limit[1]:
			self.__ax2_limits.append(Rectangle(
				(0,self.__Yopt_min_limit[0]),self.__Xopt_min_limit[0],self.__Yopt_max_limit[0]-self.__Yopt_min_limit[0],fill=True,color='grey'))

		for item in self.__ax2_limits:
			self.__ax2.add_patch(item)


	def show(self):
		plt.show()



def main():
	limits = {'Yopt_max':3.3,'Yopt_min':1,'Xopt_min':1,'Xopt_max':3}
	d = Diagram(limits=limits)
	d.show()
	print('derp')
	limits = {'Yopt_max:':3.3}
	print('derp')
	d.set_limits(limits)
	print('derp')
	d.show()

if __name__ == "__main__":
	main()
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax2 = fig.add_axes([.7,.7,.2,.2])
ax2.set_position([.1,.1,.2,.2])
ax.set_title('Using regular Axes')
print(ax2.get_position())
plt.show()

fig, ax = plt.subplots()
ax2 = ax.inset_axes([.7,.7,.2,.2])
ax2.set_position([.1,.1,.2,.2])
ax.set_title('Using Axes.inset_axes')
print(ax2.get_position())
plt.show()

#hacky fix:
from matplotlib.axes._axes import _make_inset_locator
fig, ax = plt.subplots()
ax2 = ax.inset_axes([.7,.7,.2,.2])
ax2.set_axes_locator(_make_inset_locator([.1,.1,.2,.2],fig.transFigure,ax))
ax2.
print(ax2.get_position())
plt.show()
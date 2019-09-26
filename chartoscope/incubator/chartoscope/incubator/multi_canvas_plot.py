from tkinter import Tk, Button
import numpy as np
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def plotthem():
    plt.figure(1)
    plt.clf()
    x = np.arange(0.0,3.0,0.01)
    y = np.sin(2*np.pi*x+random.random())
    plt.plot(x,y)
    plt.gcf().canvas.draw()

    plt.figure(2)
    plt.clf()
    x = np.arange(0.0,3.0,0.01)
    y = np.tan(2*np.pi*x+random.random())
    plt.plot(x,y)
    plt.gcf().canvas.draw()

root = Tk()

b = Button(root, text="Plot", command = plotthem)
b.grid(row=0, column=0)

# init figures
fig1 = plt.figure()

canvas1 = FigureCanvasTkAgg(fig1, master=root)
#toolbar = NavigationToolbar2TkAgg(canvas1, root)
canvas1.get_tk_widget().grid(row=0,column=1)
#toolbar.grid(row=1,column=1)

fig2 = plt.figure()
canvas2 = FigureCanvasTkAgg(fig2, master=root)
#toolbar = NavigationToolbar2TkAgg(canvas2, root)
canvas2.get_tk_widget().grid(row=0,column=2)
#toolbar.grid(row=1,column=2)


root.mainloop()
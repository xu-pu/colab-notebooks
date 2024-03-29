import numpy as np
from abc import abstractmethod
import matplotlib.pyplot as plt
from matplotlib import animation
from IPython.display import HTML, Video
from dynamics.dynamic_system import DynamicSystem


class PlottableSystem(DynamicSystem):

    @property
    @abstractmethod
    def title(self) -> str:
        pass

    @property
    @abstractmethod
    def bounding_box(self) -> np.ndarray:
        """return (xmin, xmax, ymin, ymax)"""
        pass

    @abstractmethod
    def y2pt(self, y) -> np.ndarray:
        pass

    def vy2vpt(self, vy):
        t, ydim = vy.shape
        assert (ydim == self.ydim)
        return np.array([self.y2pt(vy[i, :]) for i in range(t)])

    def plot(self, vy, fps: int, legend=None, filename=None):
        anim = self.animate(vy, fps, legend)
        if filename is not None:
            anim.save(filename, writer=animation.FFMpegWriter(fps=fps))
            return Video(filename, embed=True)
        else:
            return HTML(anim.to_jshtml())

    def animate(self, vy, fps: int, legend) -> animation.FuncAnimation:
        if type(vy) == np.ndarray:
            vy = [vy, ]
        tspan, ydim = vy[0].shape
        assert (ydim == self.ydim)

        if type(legend) == str:
            legend = [legend, ]

        assert (legend is None or len(legend) == len(vy))

        trajs = [self.vy2vpt(traj) for traj in vy]

        # First set up the figure, the axis, and the plot element we want to animate
        fig, ax = plt.subplots()

        xmin, xmax, ymin, ymax = self.bounding_box
        plt_width = xmax - xmin
        plt_height = ymax - ymin
        ratio = 0.1

        ax.set_aspect('equal')
        ax.set_xlim((xmin, xmax))
        ax.set_ylim((ymin, ymax))
        ax.set_title(self.title)
        timestamp = ax.text(
            xmin + plt_width * ratio,
            ymax - plt_height * ratio,
            't=0s'
        )

        lines = [ax.plot([], [], lw=1, marker="o")[0] for i in trajs]

        if legend is not None:
            for i, line in enumerate(lines):
                line.set_label(legend[i])
            ax.legend(loc='upper right')

        # initialization function: plot the background of each frame
        def init():
            for line in lines:
                line.set_data([], [])
                return lines + [timestamp, ]

        # animation function. This is called sequentially
        def animate(t):
            for idx, line in enumerate(lines):
                pts = trajs[idx][t, :]
                line.set_data(pts[:, 0], pts[:, 1])
            timestamp.set_text('t=%.2fs' % (t/fps))
            return lines + [timestamp, ]

        # call the animator. blit=True means only re-draw the parts that have changed.
        anim = animation.FuncAnimation(
            fig,
            animate,
            init_func=init,
            frames=tspan,
            interval=1000/fps,
            blit=True
        )

        plt.close()

        return anim

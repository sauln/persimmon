import numpy as np
import matplotlib.pyplot as plt

__all__ = ["plot_diagrams", "bottleneck_matching", "wasserstein_matching"]


def plot_diagrams(
    diagrams,
    plot_only=None,
    title=None,
    xy_range=None,
    labels=None,
    colormap="default",
    size=20,
    ax_color=np.array([0.0, 0.0, 0.0]),
    diagonal=True,
    lifetime=False,
    legend=True,
    show=False,
    ax=None
):
    """A helper function to plot persistence diagrams. 

    Parameters
    ----------
    diagrams: ndarray (n_pairs, 2) or list of diagrams
        A diagram or list of diagrams. If diagram is a list of diagrams, 
        then plot all on the same plot using different colors.
    plot_only: list of numeric
        If specified, an array of only the diagrams that should be plotted.
    title: string, default is None
        If title is defined, add it as title of the plot.
    xy_range: list of numeric [xmin, xmax, ymin, ymax]
        User provided range of axes. This is useful for comparing 
        multiple persistence diagrams.
    labels: string or list of strings
        Legend labels for each diagram. 
        If none are specified, we use H_0, H_1, H_2,... by default.
    colormap: string, default is 'default'
        Any of matplotlib color palettes. 
        Some options are 'default', 'seaborn', 'sequential'. 
        See all available styles with

        .. code:: python

            import matplotlib as mpl
            print(mpl.styles.available)

    size: numeric, default is 20
        Pixel size of each point plotted.
    ax_color: any valid matplotlib color type. 
        See [https://matplotlib.org/api/colors_api.html](https://matplotlib.org/api/colors_api.html) for complete API.
    diagonal: bool, default is True
        Plot the diagonal x=y line.
    lifetime: bool, default is False. If True, diagonal is turned to False.
        Plot life time of each point instead of birth and death. 
        Essentially, visualize (x, y-x).
    legend: bool, default is True
        If true, show the legend.
    show: bool, default is False
        Call plt.show() after plotting. If you are using self.plot() as part 
        of a subplot, set show=False and call plt.show() only once at the end.
    """

    ax = ax or plt.gca()
    plt.style.use(colormap)

    xlabel, ylabel = "Birth", "Death"

    if labels is None:
        # Provide default labels for diagrams if using self.dgm_
        labels = [
            "$H_0$",
            "$H_1$",
            "$H_2$",
            "$H_3$",
            "$H_4$",
            "$H_5$",
            "$H_6$",
            "$H_7$",
            "$H_8$",
        ]

    if not isinstance(diagrams, list):
        # Must have diagrams as a list for processing downstream
        diagrams = [diagrams]

    if plot_only:
        diagrams = [diagrams[i] for i in plot_only]
        labels = [labels[i] for i in plot_only]

    if not isinstance(labels, list):
        labels = [labels] * len(diagrams)

    # Construct copy with proper type of each diagram
    # so we can freely edit them.
    diagrams = [dgm.astype(np.float32, copy=True) for dgm in diagrams]

    # find min and max of all visible diagrams
    concat_dgms = np.concatenate(diagrams).flatten()
    has_inf = np.any(np.isinf(concat_dgms))
    finite_dgms = concat_dgms[np.isfinite(concat_dgms)]

    # clever bounding boxes of the diagram
    if not xy_range:
        # define bounds of diagram
        ax_min, ax_max = np.min(finite_dgms), np.max(finite_dgms)
        x_r = ax_max - ax_min

        # Give plot a nice buffer on all sides.
        # ax_range=0 when only one point,
        buffer = 1 if xy_range == 0 else x_r / 5

        x_down = ax_min - buffer / 2
        x_up = ax_max + buffer

        y_down, y_up = x_down, x_up
    else:
        x_down, x_up, y_down, y_up = xy_range

    yr = y_up - y_down

    if lifetime:

        # Don't plot landscape and diagonal at the same time.
        diagonal = False

        # reset y axis so it doesn't go much below zero
        y_down = -yr * 0.05
        y_up = y_down + yr

        # set custom ylabel
        ylabel = "Lifetime"

        # set diagrams to be (x, y-x)
        for dgm in diagrams:
            dgm[:, 1] -= dgm[:, 0]

        # plot horizon line
        ax.plot([x_down, x_up], [0, 0], c=ax_color)

    # Plot diagonal
    if diagonal:
        ax.plot([x_down, x_up], [x_down, x_up], "--", c=ax_color)

    # Plot inf line
    if has_inf:
        # put inf line slightly below top
        b_inf = y_down + yr * 0.95
        ax.plot([x_down, x_up], [b_inf, b_inf], "--", c="k", label=r"$\infty$")

        # convert each inf in each diagram with b_inf
        for dgm in diagrams:
            dgm[np.isinf(dgm)] = b_inf

    # Plot each diagram
    for dgm, label in zip(diagrams, labels):

        # plot persistence pairs
        ax.scatter(dgm[:, 0], dgm[:, 1], size, label=label, edgecolor="none")

        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

    ax.set_xlim([x_down, x_up])
    ax.set_ylim([y_down, y_up])
    ax.set_aspect('equal', 'box')

    if title is not None:
        ax.set_title(title)

    if legend is True:
        ax.legend(loc="lower right")

    if show is True:
        plt.show()


def bottleneck_matching(I1, I2, matchidx, D, labels=["dgm1", "dgm2"], ax=None):
    """ Visualize bottleneck matching between two diagrams

    Parameters
    ===========

    I1: array
        A diagram
    I2: array
        A diagram
    matchidx: tuples of matched indices
        if input `matching=True`, then return matching
    D: array
        cross-similarity matrix
    labels: list of strings
        names of diagrams for legend. Default = ["dgm1", "dgm2"], 
    ax: matplotlib Axis object
        For plotting on a particular axis.


    Examples
    ==========

    bn_matching, (matchidx, D) = persim.bottleneck(A_h1, B_h1, matching=True)
    persim.bottleneck_matching(A_h1, B_h1, matchidx, D)

    """

    plot_diagrams([I1, I2], labels=labels, ax=ax)
    cp = np.cos(np.pi / 4)
    sp = np.sin(np.pi / 4)
    R = np.array([[cp, -sp], [sp, cp]])
    if I1.size == 0:
        I1 = np.array([[0, 0]])
    if I2.size == 0:
        I2 = np.array([[0, 0]])
    I1Rot = I1.dot(R)
    I2Rot = I2.dot(R)
    dists = [D[i, j] for (i, j) in matchidx]
    (i, j) = matchidx[np.argmax(dists)]
    if i >= I1.shape[0] and j >= I2.shape[0]:
        return
    if i >= I1.shape[0]:
        diagElem = np.array([I2Rot[j, 0], 0])
        diagElem = diagElem.dot(R.T)
        plt.plot([I2[j, 0], diagElem[0]], [I2[j, 1], diagElem[1]], "g")
    elif j >= I2.shape[0]:
        diagElem = np.array([I1Rot[i, 0], 0])
        diagElem = diagElem.dot(R.T)
        plt.plot([I1[i, 0], diagElem[0]], [I1[i, 1], diagElem[1]], "g")
    else:
        plt.plot([I1[i, 0], I2[j, 0]], [I1[i, 1], I2[j, 1]], "g")


def wasserstein_matching(I1, I2, matchidx, palette=None, labels=["dgm1", "dgm2"], colors=None, ax=None):
    """ Visualize bottleneck matching between two diagrams

    Parameters
    ===========

    I1: array
        A diagram
    I2: array
        A diagram
    matchidx: tuples of matched indices
        if input `matching=True`, then return matching
    labels: list of strings
        names of diagrams for legend. Default = ["dgm1", "dgm2"], 
    ax: matplotlib Axis object
        For plotting on a particular axis.

    Examples
    ==========

    bn_matching, (matchidx, D) = persim.wasserstien(A_h1, B_h1, matching=True)
    persim.wasserstein_matching(A_h1, B_h1, matchidx, D)

    """

    cp = np.cos(np.pi / 4)
    sp = np.sin(np.pi / 4)
    R = np.array([[cp, -sp], [sp, cp]])
    if I1.size == 0:
        I1 = np.array([[0, 0]])
    if I2.size == 0:
        I2 = np.array([[0, 0]])
    I1Rot = I1.dot(R)
    I2Rot = I2.dot(R)
    for index in matchidx:
        (i, j) = index
        if i >= I1.shape[0] and j >= I2.shape[0]:
            continue
        if i >= I1.shape[0]:
            diagElem = np.array([I2Rot[j, 0], 0])
            diagElem = diagElem.dot(R.T)
            plt.plot([I2[j, 0], diagElem[0]], [I2[j, 1], diagElem[1]], "g")
        elif j >= I2.shape[0]:
            diagElem = np.array([I1Rot[i, 0], 0])
            diagElem = diagElem.dot(R.T)
            plt.plot([I1[i, 0], diagElem[0]], [I1[i, 1], diagElem[1]], "g")
        else:
            plt.plot([I1[i, 0], I2[j, 0]], [I1[i, 1], I2[j, 1]], "g")

    plot_diagrams([I1, I2], labels=labels, ax=ax)

class Barcode():
    def __init__(self, diagrams):
        '''
        parameters:
        ===========
            diagrams: list-like
                typically the output of ripser(nodes)['dgms']

        examples:
        ===========

        n = 300
        t = np.linspace(0, 2 * np.pi, n)
        noise = np.random.normal(0, 0.1, size=n)

        data = np.vstack([((3+d) * np.cos(t[i]+d), (3+d) * np.sin(t[i]+d)) for i, d in enumerate(noise)])
        diagrams = ripser(data)

        bc = Barcode(diagrams['dgms'])
        bc.plot_barcode()
        '''
        if not isinstance(diagrams, list):
            diagrams = [diagrams]

        if len(diagrams) == 2:
            self.plot_barcode = self._plot_H0_H1

        else:
            self.plot_barcode = self._plot_Hn

        self.diagrams = diagrams

    def _plot_H0_H1(self, **kwargs):
        '''
        parameters:
        ===========
            figsize: tuple
                figure size, default=(6,6)

            show: boolean
                show the figure via plt.show()

            export_png: boolean
                write image to png data, returned as io.BytesIO() instance, default=False
                
            **kwargs: artist paramters for the barcodes, defaults:
                c='grey'
                linestyle='-'
                linewidth=0.5
                dpi=100 (for png export)

        returns:
        ===========
            list of png exports or []
        '''
        import io

        fsize = kwargs.get('figsize', (6, 6))
        show = kwargs.get('show', True)
        export = kwargs.get('export_png', False)
        dpi = kwargs.get('dpi', 100)

        out = []

        fig, ax = plt.subplots(2, 1, figsize=fsize)

        for dim, diagram in enumerate(self.diagrams):
            self._plot_many_bars(dim, diagram, dim, ax, **kwargs)

        if export:
            fp = io.BytesIO()
            plt.savefig(fp, dpi=dpi)
            fp.seek(0)

            out += [fp]

        if show:
            plt.show()

        return out

    def _plot_Hn(self, **kwargs):
        '''
        parameters:
        ===========
            figsize: tuple
                figure size, default=(6,6)

            show: boolean
                show the figure via plt.show()

            export_png: boolean
                write image to png data, returned as io.BytesIO() instance, default=False
                
            **kwargs: artist paramters for the barcodes, defaults:
                c='grey'
                linestyle='-'
                linewidth=0.5
                dpi=100 (for png export)

        returns:
        ===========
            list of png exports or []
        '''
        import io
        
        fsize = kwargs.get('figsize', (6, 4))
        show = kwargs.get('show', True)
        export = kwargs.get('export_png', False)
        dpi = kwargs.get('dpi', 100)

        out = []

        for dim, diagram in enumerate(self.diagrams):
            fig, ax = plt.subplots(1, 1, figsize=fsize)

            self._plot_many_bars(dim, diagram, 0, [ax], **kwargs)

            if export:
                fp = io.BytesIO()
                plt.savefig(fp, dpi=dpi)
                fp.seek(0)

                out += [fp]

            if show:
                plt.show()

        return out

    def _plot_many_bars(self, dim, diagram, idx, ax, **kwargs):
        number_of_bars = len(diagram)
        print("Number of bars in dimension %d: %d" % (dim, number_of_bars))

        if number_of_bars > 0:
            births = np.vstack([(elem[0], i) for i, elem in enumerate(diagram)])
            deaths = np.vstack([(elem[1], i) for i, elem in enumerate(diagram)])

            inf_bars = np.where(np.isinf(deaths))[0]
            max_death = deaths[np.isfinite(deaths[:, 0]), 0].max()

            number_of_bars_fin = births.shape[0] - inf_bars.shape[0]
            number_of_bars_inf = inf_bars.shape[0]

            _ = [self._plot_a_bar(ax[idx], birth, deaths[i], max_death, **kwargs) for i, birth in enumerate(births)]

        # the line below is to plot a vertical red line showing the maximal finite bar length
        ax[idx].plot([max_death, max_death], [0, number_of_bars - 1],
            c='r',
            linestyle='--',
            linewidth=0.5)

        title = "H%d barcode: %d finite, %d infinite" % (dim, number_of_bars_fin, number_of_bars_inf)
        ax[idx].set_title(title, fontsize=9)
        ax[idx].set_yticks([])

        ax[idx].spines['right'].set_visible(False)
        ax[idx].spines['left'].set_visible(False)
        ax[idx].spines['top'].set_visible(False)

    @staticmethod
    def _plot_a_bar(ax, birth, death, max_death, c='gray', linestyle='-', linewidth=0.5, **kwargs):
        if np.isinf(death[0]):
            death[0] = 1.05 * max_death
            ax.plot(death[0], death[1],
                c=c,
                markersize=4,
                marker='>')

        ax.plot([birth[0], death[0]], [birth[1], death[1]], 
            c=c,
            linestyle=linestyle,
            linewidth=linewidth)


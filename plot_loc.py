#!/usr/bin/env python3
import re # for regular expressions
import os
import sys
import csv
import datetime
import math
#import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.dates as mdates
import matplotlib.ticker as mticker


# Check out https://github.com/bokeh/bokeh/pull/4868/files to see if toggling on/off is possible

# OR try interactive mode: https://matplotlib.org/stable/users/interactive.html
# let python run in background and enable / disable lines with user input

DATA_folder = "./results/"
PLOT_folder = "./plots/"

CSV_delim = ';'

## Plotting globals:
FigSize = (16, 9)
GridLineWidth = 2
PlotLineWidth = 5
DrawStyle = "default" #"steps-post"#"default"
LabelFontSize = 15
AxisTickSize = 12
AxisYScale = 'log' # 'linear'
AxisYScale = 'linear'
AxisXScale = 'linear' # 'log'  Better don't touch since x-axis is Time here


def date_filter(date_):
    return date_.year >= 2017


def filter_xy(x, y):
    if len(x) != len(y):
        raise AttributeError
    new_x = []
    new_y = []
    for i in range(len(x)):
        if date_filter(x[i]):
            new_x.append(x[i])
            new_y.append(y[i])
    return new_x, new_y
    


### dictionary to match purpose to CSV header
h_dict = {
        "date" : "Date",
        "loc": "LOC",
        }

plot_set = set([
        #"deal.II",
        #"Eigen",
        #"fleur",
        "Ginkgo",
        #"Heat",
        #"hypre",
        #"git",
        #"LAMMPS",
        #"LAPACK",
        "MFEM",
        #"Nest",
        #"petsc",
        "Slate",
        "SuperLU",
        #"Elemental",
        #"Trilinos",
        #"Blitz",
        #"Ghost",
        "uBLAS",
        "KBLAS-gpu",
        #"KBLAS-cpu",
        #"clBLAS",
        #"FLENS",
        #"SuiteSparse",
        #"BootCMatch",
        #"AMGCL",
        #"DUNE-ISTL",
        "BLOPEX",
        #"EVSL",
        #"Spectra",
        #"Dense_HODLR",
        #"H2Lib",
        #"hmat-oss",
        "STRUMPACK",
        #"GetFEM",
        "Kokkos Kernels",
    ])

name_label_translate = {
        "ExampleName": "ExampleLabelName",
    }

def read_csv(path):
    """
    Opens the CSV file in 'path' and returns 2 values:
    1. A list of data entries The key is the date of the benchmark, the value is the list of a list
       of column entries of the csv file
    2. The key is the same as in h_dict, the value is the index of the row
       array / list for the correesponding key
    """
    if path == None or not path:
        raise Exception("No filename specified! Unable to read file.")
    with open(path, 'r') as f:
        #print("The csv file <{}> is opened".format(path))
        csv_f = csv.reader(f, delimiter=CSV_delim, skipinitialspace=True)
        header = next(csv_f)
        #print("CSV header: {}".format(header))
        
        i_dict = {}
        for key, val in h_dict.items():
            for i in range(len(header)):
                if header[i] == val:
                    i_dict[key] = i
        #print("Resulting index dictionary: {}".format(i_dict))

        data = []

        for r in csv_f:
            data.append(r)
    
    return data, i_dict


############################### Actual Plotting ###############################
### Color definition
myblue    = (0, 0.4470, 0.7410);
myorange  = (0.8500, 0.3250, 0.0980);
myyellow  = (0.9290, 0.6940, 0.1250);
mymagenta = (0.4940, 0.1840, 0.5560);
mygreen   = (0.4660, 0.6740, 0.1880);
mycyan    = (0.3010, 0.7450, 0.9330);
myred     = (0.6350, 0.0780, 0.1840);
myblack   = (0.2500, 0.2500, 0.2500);
mybrown   = (0.6500, 0.1600, 0.1600);



def create_fig_ax():
    """
    Creates a tuple of figure and axis for future plots.
    The size, the visibility of the grid and the log-scale of x and y is preset
    """
    fig = Figure(figsize=FigSize) # Properly garbage collected
    ax = fig.add_subplot()
    #fig, ax = plt.subplots(figsize=FigSize) # NOT garbage collected!
    grid_minor_color = (.9, .9, .9)
    grid_major_color = (.8, .8, .8)
    ax.grid(True, which="major", axis="both", linestyle='-', linewidth=GridLineWidth, color=grid_major_color)
    ax.grid(True, which="minor", axis="both", linestyle=':', linewidth=GridLineWidth, color=grid_minor_color)
    #ax.loglog()
    ax.set_yscale(AxisYScale)
    ax.set_xscale(AxisXScale)
    return fig, ax


def plot_figure(fig, file_name, plot_prefix = ""):
    """Plots the given figure fig as various formats with a base-name of file_name.
    PLOT_folder will be used as the filder for the file; plot_prefix will be the
    prefix of each file."""

    file_path = PLOT_folder + plot_prefix + file_name
    p_bbox = "tight"
    p_pad = 0
    p_dpi = 300  # Only useful for non-scalable formats
    with PdfPages(file_path+".pdf") as export_pdf:
        export_pdf.savefig(fig, dpi=p_dpi, bbox_inches=p_bbox, pad_inches=p_pad)
    fig.savefig(file_path+".svg", dpi=p_dpi, bbox_inches=p_bbox, pad_inches=p_pad, format="svg")
    fig.savefig(file_path+".png", dpi=p_dpi, bbox_inches=p_bbox, pad_inches=p_pad, format="png")



def print_help():
    print("Usage: {} [option]\n".format(sys.argv[0])
        + "Options and arguments:\n"
        + "-h:     Print this help\n"
        + "--help: Print this help\n"
        + "--list: Print the list of candidates for plotting\n"
        + "--all:  Prints all candidates\n"
        + "No argument means plot."
         )

if __name__ == "__main__":
    print_list = False
    print_all = False
    if len(sys.argv) == 2 and (sys.argv[1] == "--help" or sys.argv[1] == "-h"):
        print_help()
        exit(0)
    elif len(sys.argv) == 2 and sys.argv[1] == "--list":
        print_list = True
    elif len(sys.argv) == 2 and sys.argv[1] == "--all":
        print_all = True
    elif len(sys.argv) != 1:
        print_help()
        exit(1)
    
    # Change to the directory where the script is placed
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Make sure the plot folder exists
    if not os.path.exists(PLOT_folder):
        os.makedirs(PLOT_folder)

    # Read only the files that do not have the date ending
    dir_list = os.listdir(DATA_folder)
    expr = re.compile("^.+_\\d{8,8}_\\d{4,4}.csv$")

    csv_list = []

    for el in dir_list:
        if expr.match(el):
            continue
        elif el.endswith(".csv"):
            csv_list.append(el)

    # Sort the list:
    csv_list.sort(key=lambda e: e.upper())

    if (print_list):
        print("plot_set = set([")
        indent = 4 * " "
        dindent = 8 * " "
        for el in csv_list:
            print('{}"{}",'.format(dindent, el[:-len(".csv")]))
        print(indent + "])")
        exit(0)

    fig, ax = create_fig_ax()

    plot_lines = []
    
    for csv_file in csv_list:
        name = csv_file[:-len(".csv")]
        plot_name = name
        if name in name_label_translate:
            plot_name = name_label_translate[name]

        if not print_all and name not in plot_set:
            continue

        input_csv = os.path.abspath(DATA_folder + csv_file)
        data, i_dict = read_csv(input_csv)

        x_date = []
        y_loc = []
        for row in data:
            x_date.append(datetime.datetime.strptime(row[i_dict["date"]],
                "%Y-%m-%dT%H:%M:%S%z"))
            y_loc.append(int(row[i_dict["loc"]]))

        x_date, y_loc = filter_xy(x_date, y_loc)
        
        plot_lines.append(ax.plot(x_date, y_loc,
                                  marker='',
                                  linewidth=PlotLineWidth,
                                  drawstyle=DrawStyle,
                                  #color=myblue,
                                  label=plot_name))
    
    # Format dates properly. For details:
    # https://matplotlib.org/stable/gallery/ticks_and_spines/date_concise_formatter.html
    locator = mdates.AutoDateLocator(minticks=3)
    formatter = mdates.ConciseDateFormatter(locator)
    #formatter.formats = ['%Y', '%b', '%d', '%H:%M', '%H:%M', '%S.%f']
    #formatter.zero_formats = ['', '%Y', '%b', '%d-%b', '%H:%M', '%H:%M']
    #formatter.offset_formats = ['', '%Y', '%Y-%b', '%Y-%b-%d', '%Y-%b-%d', '%Y-%b-%d %H:%M']
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    
    ax.tick_params(axis='x', labelsize=AxisTickSize)
    ax.tick_params(axis='y', labelsize=AxisTickSize)
    
    ax.set_xlabel("Time", fontsize=LabelFontSize)
    ax.set_ylabel("Lines of code", fontsize=LabelFontSize)
    
    ax.legend(loc="upper left", ncol=math.ceil(len(plot_lines) / 20), fontsize=LabelFontSize)

    #plt.ion()
    #plt.show()
    plot_figure(fig, "LoC_evolution")

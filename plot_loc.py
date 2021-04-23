#!/usr/bin/env python3
import os
import sys
import csv
import datetime
#import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.dates as mdates
import matplotlib.ticker as mticker


plot_folder = "./plots/"

CSV_delim = ';'
LineWidth = 5
DrawStyle = "steps-post"#"default"


### dictionary to match purpose to CSV header
h_dict = {
        "date" : "Date",
        "loc": "LOC",
        }

plot_list = [
        {
            "name": "Ginkgo",
            "file": "result/Ginkgo_20210422_0440.csv",
        },
        {
            "name": "Heat",
            "file": "result/Heat_20210423_1640.csv",
        },
    ]

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

### Other globals
LineWidth = 1
MarkerSize = 8



def create_fig_ax():
    """
    Creates a tuple of figure and axis for future plots.
    The size, the visibility of the grid and the log-scale of x and y is preset
    """
    fig = Figure(figsize=(10, 4)) # Properly garbage collected
    ax = fig.add_subplot()
    #fig, ax = plt.subplots(figsize=(10, 4)) # NOT garbage collected!
    grid_minor_color = (.9, .9, .9)
    grid_major_color = (.8, .8, .8)
    ax.grid(True, which="major", axis="both", linestyle='-', linewidth=1, color=grid_major_color)
    ax.grid(True, which="minor", axis="both", linestyle=':', linewidth=1, color=grid_minor_color)
    #ax.loglog()
    return fig, ax


def plot_figure(fig, file_name, plot_prefix = ""):
    """Plots the given figure fig as various formats with a base-name of file_name.
    plot_folder will be used as the filder for the file; plot_prefix will be the
    prefix of each file."""

    file_path = plot_folder + plot_prefix + file_name
    p_bbox = "tight"
    p_pad = 0
    p_dpi = 300  # Only useful for non-scalable formats
    with PdfPages(file_path+".pdf") as export_pdf:
        export_pdf.savefig(fig, dpi=p_dpi, bbox_inches=p_bbox, pad_inches=p_pad)
    fig.savefig(file_path+".svg", dpi=p_dpi, bbox_inches=p_bbox, pad_inches=p_pad, format="svg")
    fig.savefig(file_path+".png", dpi=p_dpi, bbox_inches=p_bbox, pad_inches=p_pad, format="png")



if __name__ == "__main__":
    """
    if len(sys.argv) != 2 or sys.argv[1] == "--help" or sys.argv[1] == "-h":
        print("Usage: {} <csv_file>".format(sys.argv[0]))
        exit(1)
    """
    if len(sys.argv) != 1:
        print("This script does not support arguments!")
        exit(1)
    
    # Change to the directory where the script is placed
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Make sure the plot folder exists
    if not os.path.exists(plot_folder):
        os.makedirs(plot_folder)

    fig, ax = create_fig_ax()
    
    for p_dict in plot_list:
        input_csv = os.path.abspath(p_dict["file"])
        data, i_dict = read_csv(input_csv)

        x_date = []
        y_loc = []
        for row in data:
            x_date.append(datetime.datetime.strptime(row[i_dict["date"]],
                "%Y-%m-%dT%H:%M:%S%z"))
            y_loc.append(int(row[i_dict["loc"]]))

        
        ax.plot(x_date, y_loc,
            marker='',
            linewidth=LineWidth,
            drawstyle=DrawStyle,
            #color=myblue,
            label=p_dict["name"])
    
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
    ax.set_xlabel("Time")
    ax.set_ylabel("Lines of code")
    ax.legend(loc="lower right")

    plot_figure(fig, "LoC_evolution")

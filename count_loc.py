#!/usr/bin/env python3

import os
import subprocess
from datetime import datetime


TMP_storage = "/tmp/loc_count"
OUT_dir = "./result"
CSV_delim = ";"
LOG_delim = ";"
OUT_delim = ";"


"""
git log options:
--merges (shows merge commits only)

--pretty=format:%ad;%H;

--date=iso-strict (changes the output format of the dates without day name)
"""

ginkgo_info = {
        "name": "Ginkgo",
        "url": "https://github.com/ginkgo-project/ginkgo.git",
        "add_cloc_args": ["--force-lang=cuda,hpp.inc"],
        "langs": ["C", "C++", "C/C++ Header", "CUDA"],
        "branch": "develop",
        }

git_repositories = [ginkgo_info,
        ]

def decode(b_str):
    return b_str.decode("utf-8")

class CmdOutput:
    def __init__(self, sp_completed_process):
        self.ret_code = sp_completed_process.returncode
        self.output = self.format_output_(sp_completed_process.stdout)
        self.error = self.format_output_(sp_completed_process.stderr)

    def format_output_(self, out):
        f_list = decode(out).split('\n')
        while(len(f_list) and f_list[-1] == ''):
            f_list.pop()
        return f_list


def run_cmd(cmd, allow_failure=False):
    sp = subprocess.run(cmd, capture_output=True)
    if not allow_failure:
        #print("Output:\n{}\nError:\n{}\n".format(sp.stdout, sp.stderr))
        sp.check_returncode()
    return CmdOutput(sp)


def call_cloc(info_dict):
    cmd = ["cloc",
              "--quiet",
              "--csv",
              "--csv-delimiter={d}".format(d=CSV_delim),
              "--exclude-dir=build", #.git is always ignored by default
          ]
    if "add_cloc_args" in info_dict:
        cmd.extend(info_dict["add_cloc_args"])
    cmd.append("./") # already in correct directory

    # Run cloc command
    output = run_cmd(cmd).output

    # format output
    data_start = 0
    while data_start < len(output) and output[data_start] == '':
        data_start += 1
    data_start += 1 # Also drop the header of the CSV output
    loc_table = []
    for line in output[data_start:]:
        loc_table.append(line.split(CSV_delim))
    language_idx = 1
    loc_idx = -1

    # Add only the specified languages
    loc = 0
    if "langs" in info_dict and info_dict["langs"]:
        for line in output[data_start:]:
            row = line.split(CSV_delim)
            if len(row) > 1 and row[language_idx] in info_dict["langs"]:
                loc += int(row[loc_idx])
    #No languages specified -> use the SUM entry
    else:
        for line in output[data_start:]:
            row = line.split(CSV_delim)
            # If the delimiter was not properly used for SUM, use the ',' separator
            if len(row) == 1:
                row = row[0].split(',')
            if row[language_idx] != "SUM":
                continue
            else:
                loc = int(row[loc_idx])
                break

    return loc


def own_print(out_file, string):
    out_file.write(string + '\n')
    print(string)

if __name__ == "__main__":
    # Change to the directory where the script is placed
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    if not os.path.exists(OUT_dir):
        os.makedirs(OUT_dir)
    OUT_dir = os.path.abspath(OUT_dir)

    # Make sure the plot folder exists
    if not os.path.exists(TMP_storage):
        os.makedirs(TMP_storage)
    # Change to temporary directory
    os.chdir(TMP_storage)

    sp = run_cmd(["cloc", "--version"])
    cloc_version = sp.output[0]
    print("cloc version: {}".format(cloc_version))
    sp = run_cmd(["git", "--version"])
    git_version = sp.output[0].split(' ')[-1]
    print("git version: {}".format(git_version))

    for idict in git_repositories:
        now = datetime.now()
        date_suffix = now.strftime("_%Y%m%d_%H%M")
        out_file = OUT_dir + "/" + idict["name"] + date_suffix + ".csv"
        with open(out_file, "w") as output_file:
            own_print(output_file, "Date{d}Commit Hash{d}LOC".format(d=OUT_delim))
            run_cmd(["git", "clone", idict["url"], idict["name"]], True)
            os.chdir(idict["name"])

            run_cmd(["git", "checkout", idict["branch"]])
            log_out = run_cmd(["git", "log",
                                 "--merges",
                                 "--date=iso-strict",
                                 "--pretty=format:%ad{d}%H{d}%s".format(d=LOG_delim),
                              ])
            for line in log_out.output:
                spl = line.split(LOG_delim)
                date = spl[0]
                commit = spl[1]

                # check out specific commit and count locs
                run_cmd(["git", "checkout", commit])
                loc = call_cloc(idict)
                own_print(output_file, "{}{d}{}{d}{}".format(date, commit, loc, d=OUT_delim))

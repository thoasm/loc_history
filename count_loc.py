#!/usr/bin/env python3

import os
import subprocess
import shutil
from datetime import datetime


TMP_storage = "/tmp/loc_count"
OUT_dir = "./result"
CSV_delim = ";"
LOG_delim = ";"
OUT_delim = ";"

CLOC_binary = "cloc"
GIT_binary = "git"

default_languages = [
        "C", "C++", "C/C++ Header", "CUDA",
        "Assembly",
        "CMake", "make",
        "Java", "C#", "Scala",
        "Python", "Cython", "Perl",
        "Bourne Shell", "Bourne Again Shell", "zsh",
        "Fortran 77", "Fortran 90", "Fortran 95",
        "Go", "MATLAB", "Julia", "Mathematica", "R",
        "Pascal",
        "Visual Basic", "JavaScript", "TypeScript", "PHP",
    ]


# If all languages of `cloc` should be considered, add the dictionary entry
# "langs": "ALL"

git_repositories = {
#    "Ginkgo": {
#        "url": "https://github.com/ginkgo-project/ginkgo.git",
#        "add_cloc_args": ["--force-lang=cuda,hpp.inc"],
#        "langs": default_languages,
#        "branch": "develop",
#        },
#    "Heat": { "url": "https://github.com/helmholtz-analytics/heat.git", },
#    "Nest": { "url": "https://github.com/nest/nest-simulator.git", },
#    "fleur": { "url": "https://iffgit.fz-juelich.de/fleur/fleur.git", },
#    "Tensorflow": { "url": "https://github.com/helmholtz-analytics/heat.git", },
#
#    "STXXL": { "url": "https://github.com/stxxl/stxxl.git", },
#    "Thrill": { "url": "https://github.com/thrill/thrill.git", },
#    "TLX": { "url": "https://github.com/tlx/tlx.git", },
#    "KaHIP": { "url": "https://github.com/schulzchristian/KaHIP.git", },
#    "KaHyPar": { "url": "https://github.com/SebastianSchlag/kahypar.git", },
#    "KaMIS": { "url": "https://github.com/sebalamm/KaMIS.git", },
#    "NetworKit": { "url": "https://github.com/networkit/networkit.git", },
#    "sdsl-lite": { "url": "https://github.com/simongog/sdsl-lite.git", },
#    #"TBTrader": { "url": "https://github.com/bingmann/tbtrader.git", },
#    "Glowing-Bear": { "url": "https://github.com/glowing-bear/glowing-bear.git", },
#    # Algebra
#    "LAPACK": { "url": "https://github.com/Reference-LAPACK/lapack.git", },
    "OpenBLAS": { "url": "https://github.com/xianyi/OpenBLAS.git", },
    "ScaLAPACK": { "url": "https://github.com/Reference-ScaLAPACK/scalapack.git", },
    "DBCSR": { "url": "https://github.com/cp2k/dbcsr.git", },
    "Eigen": { "url": "https://github.com/eigenteam/eigen-git-mirror.git", },
    "Armadillo": { "url": "https://gitlab.com/conradsnicta/armadillo-code.git", },
    "Elemental": { "url": "https://github.com/elemental/Elemental.git", },
    #"Slate": { "url": "https://icl.utk.edu/slate/", },

    # Graphs
    "OGDF": { "url": "https://github.com/ogdf/ogdf.git", },
    "GraphChi": { "url": "https://github.com/GraphChi/graphchi-cpp.git", },
    "Ligra": { "url": "https://github.com/jshun/ligra.git", },
    # Bio
    "SeqAN": { "url": "https://github.com/seqan/seqan.git", },
    "genesis": { "url": "https://github.com/lczech/genesis.git", },
    "Treerecs": { "url": "https://gitlab.inria.fr/Phylophile/Treerecs.git", },
    "RAxML-ng": { "url": "https://github.com/amkozlov/raxml-ng.git", },
    # Solving
    "CVC4": { "url": "https://github.com/CVC4/CVC4.git", },
    "MiniSAT": { "url": "https://github.com/niklasso/minisat.git", },
    # Etc
    #"Parsec": { "url": "http://icl.utk.edu/parsec/", },
    "Charm++": { "url": "https://github.com/UIUC-PPL/charm.git", },
    "HPX": { "url": "https://github.com/STEllAR-GROUP/hpx.git", },
    "osrm-backend": { "url": "https://github.com/Project-OSRM/osrm-backend.git", },
    "CP2K": { "url": "https://github.com/cp2k/cp2k.git", },
    "root": { "url": "https://github.com/root-project/root.git", },
    
    # BIG projects
#    "Giraph": { "url": "https://github.com/apache/giraph.git", },
#    "NetworkX": { "url": "https://github.com/networkx/networkx.git", },
#    "PyTorch": { "url": "https://github.com/pytorch/pytorch.git", },
#    "mlpack": { "url": "https://github.com/mlpack/mlpack.git", },
#    "Z3": { "url": "https://github.com/Z3Prover/z3.git", },
#    "folly": { "url": "https://github.com/facebook/folly.git", },
#    "git": { "url": "https://github.com/git/git.git", },
#    "Mesos": { "url": "https://github.com/apache/mesos.git", },
#    "OpenMPI": { "url": "https://github.com/open-mpi/ompi.git", },
#    "MPICH": { "url": "https://github.com/pmodels/mpich.git", },
#    "X10": { "url": "https://github.com/x10-lang/x10.git", },
#    "Spark": { "url": "https://github.com/apache/spark.git", },
#    "Flink": { "url": "https://github.com/apache/flink.git", },
#    "Hadoop": { "url": "https://github.com/apache/hadoop.git", },
#    "Storm": { "url": "https://github.com/apache/storm.git", },
#    "Tensorflow": { "url": "https://github.com/tensorflow/tensorflow.git", },
#    "Arrow": { "url": "https://github.com/apache/arrow.git", },
#    "TuriCreate": { "url": "https://github.com/apple/turicreate.git", },
#    "DBeaver": { "url": "https://github.com/dbeaver/dbeaver.git", },
#    "QuantLib": { "url": "https://github.com/lballabio/quantlib.git", },
#    "RocksDB": { "url": "https://github.com/facebook/rocksdb.git", },
#    "emacs": { "url": "https://github.com/emacs-mirror/emacs.git", },
#    "LLVM": { "url": "https://github.com/llvm/llvm-project.git", },
#    "gcc": { "url": "https://github.com/gcc-mirror/gcc.git", },
#    "Linux": { "url": "https://github.com/torvalds/linux.git", },
    #"Linux": { "url": "https://github.com/torvalds/linux.git", },
    # Not supported bc not relying on merges
    #"GCC": { "url": "https://github.com/gcc-mirror/gcc.git", },
    #"LLVM": { "url": "https://github.com/llvm/llvm-project.git", }
    }

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
    cmd = [CLOC_binary,
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
    loc_sum = 0
    filter_langs = []
    use_all = ("langs" in info_dict and isinstance(info_dict["langs"], str) and info_dict["langs"] == "ALL")
    
    if "langs" not in info_dict:
        filter_langs = default_languages
    # Use the languages specified in `info_dict["langs"]`
    elif not use_all:
        filter_langs = info_dict["langs"]
    # ALL languages specified -> use the SUM entry
    for line in output[data_start:]:
        row = line.split(CSV_delim)
        # If the delimiter was not properly used, try the ',' separator
        if len(row) == 1:
            row = row[0].split(',')
        if len(row) > 1 and row[language_idx] in filter_langs:
            loc += int(row[loc_idx])
        if len(row) > 1 and row[language_idx] == "SUM":
            loc_sum = int(row[loc_idx])

    if use_all:
        loc = loc_sum

    return loc, loc_sum


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

    try:
        sp = run_cmd([CLOC_binary, "--version"])
    except FileNotFoundError as e:
        print("`{}` binary not found. ".format(CLOC_binary)
              + "Please change the `CLOC_binary` "
              + "variable to point to the correct binary of "
              + "https://github.com/AlDanial/cloc")
        exit(1)

    cloc_version = sp.output[0]
    print("cloc version: {}".format(cloc_version))
    
    try:
        sp = run_cmd([GIT_binary, "--version"])
    except FileNotFoundError as e:
        print("`{}` binary not found. ".format(GIT_binary)
              + "Please change the `GIT_binary` "
              + "variable to point to the correct git binary.")
        exit(1)

    git_version = sp.output[0].split(' ')[-1]
    print("git version: {}".format(git_version))

    for name, idict in git_repositories.items():
        now = datetime.now()
        date_suffix = now.strftime("_%Y%m%d_%H%M")
        out_file_tmp = OUT_dir + "/" + name + date_suffix + ".csv"
        out_file = OUT_dir + "/" + name + ".csv"
        original_branch = ""
        with open(out_file_tmp, "w") as output_file:
            own_print(output_file, "Date{d}Commit Hash{d}LOC{d}Total LOC".format(d=OUT_delim))
            run_cmd([GIT_binary, "clone", idict["url"], name], True)
            os.chdir(name)
            #log_out = run_cmd([GIT_binary, "log", "-1", "--pretty=format:%H"])
            branch_out = run_cmd([GIT_binary, "branch", "--show-current"])
            original_branch = branch_out.output[0]

            if "branch" in idict:
                run_cmd([GIT_binary, "checkout", idict["branch"]])
            log_out = run_cmd([GIT_binary, "log",
                                 "--merges", # Only lists merge commits
                                 "--first-parent", # Only lists merge commits into current branch
                                 "--date=iso-strict",
                                 "--pretty=format:%ad{d}%H{d}%s".format(d=LOG_delim),
                              ])
            for line in log_out.output:
                spl = line.split(LOG_delim)
                date = spl[0]
                commit = spl[1]

                # check out specific commit and count locs
                run_cmd([GIT_binary, "checkout", commit])
                loc, loc_sum = call_cloc(idict)
                own_print(output_file, "{}{d}{}{d}{}{d}{}".format(date, commit, loc, loc_sum, d=OUT_delim))
            # At the end, go back to the original state
            run_cmd([GIT_binary, "checkout", original_branch])
        shutil.copyfile(out_file_tmp, out_file)
        os.chdir(TMP_storage)
        #shutil.rmtree(name, False) # remove directory recursively, throw on error

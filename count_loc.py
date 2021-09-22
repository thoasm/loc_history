#!/usr/bin/env python3

import os
import subprocess
import shutil
from datetime import datetime
import time


TMP_storage = "/tmp/loc_count"
OUT_dir = "./results"
OUT_dir_tmp = "./results/tmp"

# Internal delimiters (never seen in output)
CSV_delim = "," # In cloc-version 1.9, only ',' works properly as a delimiter
LOG_delim = ";"
# Output delimiter (both in file and to cout)
OUT_delim = ";"

CLOC_binary = "cloc"
GIT_binary = "git"
PRINT_DEBUG = True


default_languages = [
        "C", "C++", "C/C++ Header", "CUDA",
        "Assembly",
        "CMake", "make",
        "Java", "C#", "Scala",
        "Python", "Cython", "Perl",
        "Bourne Shell", "Bourne Again Shell", "zsh",
        "Fortran 77", "Fortran 90", "Fortran 95",
        "Go", "MATLAB", "Julia", "Mathematica", "R",
        # "Pascal" is shown for .inc files, internally, it is "PHP/Pascal"
        # (see `cloc --explain PHP/Pascal` or `cloc --show-ext=inc`
        "Pascal", "PHP/Pascal",     
        "Visual Basic", "JavaScript", "TypeScript", "PHP",
    ]


# TODO
# - Add automatic discovery when "--merges" does not work (less than 100?
#   commits) and switch to interval usage (maybe evendetermine the interval
#   automatically)


# If all languages of `cloc` should be considered, add the dictionary entry
# "langs": "ALL"

git_repositories = {
    # Note: Running everything in this list takes more than 24 hrs (on Linux),
    #       which is why it is recommended to comment out parts
    #"delete_me": {"""
    # """}
    "Blitz": { "url": "https://github.com/blitzpp/blitz.git", },
    "Ghost": { "url": "https://bitbucket.org/essex/ghost.git", "day_interval": 15, "all_commits": True, },
    "uBLAS": { "url": "https://github.com/boostorg/ublas.git", "day_interval": 15, "all_commits": True, },
    "KBLAS-gpu": { "url": "https://github.com/ecrc/kblas-gpu.git", "all_commits": True, },
    "KBLAS-cpu": { "url": "https://github.com/ecrc/kblas-cpu.git", "all_commits": True, },
    "clBLAS": { "url": "https://github.com/clMathLibraries/clBLAS.git", "all_commits": True, },
    "FLENS": { "url": "https://github.com/michael-lehn/FLENS.git", "all_commits": True, },
    "SuiteSparse": { "url": "https://github.com/DrTimothyAldenDavis/SuiteSparse.git", "all_commits": True, },
    "BootCMatch": { "url": "https://github.com/bootcmatch/BootCMatch.git", "all_commits": True, },
    "AMGCL": { "url": "https://github.com/ddemidov/amgcl.git", "day_interval": 15, "all_commits": True, },
    "DUNE-ISTL": { "url": "https://github.com/dune-project/dune-istl.git", },
    "BLOPEX": { "url": "https://bitbucket.org/joseroman/blopex.git", "all_commits": True, },
    "EVSL": { "url": "https://github.com/eigs/EVSL.git", "all_commits": True, },
    "Spectra": { "url": "https://github.com/yixuan/spectra.git", "all_commits": True, },
    "Dense_HODLR": { "url": "https://github.com/amiraa127/Dense_HODLR.git", "all_commits": True, },
    "H2Lib": { "url": "https://github.com/H2Lib/H2Lib.git", "all_commits": True, },
    "hmat-oss": { "url": "https://github.com/jeromerobert/hmat-oss.git", "all_commits": True, },
    "STRUMPACK": { "url": "https://github.com/pghysels/STRUMPACK.git", "all_commits": True, },
    "GetFEM": { "url": "https://git.savannah.nongnu.org/git/getfem.git", "day_interval": 90, "all_commits": True, },
    "Ginkgo_Container": { "url": "git@gitlab.com:ginkgo-project/ginkgo-containers.git" },
    "Ginkgo": {
        "url": "https://github.com/ginkgo-project/ginkgo.git",
        "add_cloc_args": ["--force-lang=cuda,hpp.inc"],
        #"langs": default_languages,
        #"branch": "develop",
        },
    "Heat": { "url": "https://github.com/helmholtz-analytics/heat.git", },
    "Nest": { "url": "https://github.com/nest/nest-simulator.git", },
    "fleur": { "url": "https://iffgit.fz-juelich.de/fleur/fleur.git", },
    "LAMMPS": { "url": "https://github.com/lammps/lammps.git", "day_interval": 15, },
    "Trilinos": { "url": "https://github.com/trilinos/Trilinos.git", "day_interval": 15, },
    "MFEM": { "url": "https://github.com/mfem/mfem.git", },
    "deal.II": { "url": "https://github.com/dealii/dealii.git", "day_interval": 15, },
    "SuperLU": { "url": "https://github.com/xiaoyeli/superlu.git", "all_commits": True, },
    "hypre": { "url": "https://github.com/hypre-space/hypre.git", },
    "petc": { "url": "https://gitlab.com/petsc/petsc.git", "day_interval": 15, },
    "Slate": { "url": "https://bitbucket.org/icl/slate.git", },
    "MAGMA": {"url": "https://bitbucket.org/icl/magma.git", },

    "STXXL": { "url": "https://github.com/stxxl/stxxl.git", },
    "Thrill": { "url": "https://github.com/thrill/thrill.git", },
    "TLX": { "url": "https://github.com/tlx/tlx.git", },
    "KaHIP": { "url": "https://github.com/schulzchristian/KaHIP.git", },
    "KaHyPar": { "url": "https://github.com/SebastianSchlag/kahypar.git", },
    "KaMIS": { "url": "https://github.com/sebalamm/KaMIS.git", "all_commits": True, },
    "NetworKit": { "url": "https://github.com/networkit/networkit.git", },
    "sdsl-lite": { "url": "https://github.com/simongog/sdsl-lite.git", },
    #"TBTrader": { "url": "https://github.com/bingmann/tbtrader.git", },
    "Glowing-Bear": { "url": "https://github.com/glowing-bear/glowing-bear.git", },
    # Algebra
    "LAPACK": { "url": "https://github.com/Reference-LAPACK/lapack.git", },
    "OpenBLAS": { "url": "https://github.com/xianyi/OpenBLAS.git", "day_interval": 15, },
    "ScaLAPACK": { "url": "https://github.com/Reference-ScaLAPACK/scalapack.git", "all_commits": True, },
    "DBCSR": { "url": "https://github.com/cp2k/dbcsr.git", },
    "Eigen": { "url": "https://gitlab.com/libeigen/eigen.git", "day_interval": 15, "all_commits": True, },
    "Armadillo": { "url": "https://gitlab.com/conradsnicta/armadillo-code.git", "all_commits": True, },
    "Elemental": { "url": "https://github.com/elemental/Elemental.git", },

    # Graphs
    "OGDF": { "url": "https://github.com/ogdf/ogdf.git", "all_commits": True, },
    "GraphChi": { "url": "https://github.com/GraphChi/graphchi-cpp.git", },
    "Ligra": { "url": "https://github.com/jshun/ligra.git", },
    # Bio
    "SeqAN": { "url": "https://github.com/seqan/seqan.git", },
    "genesis": { "url": "https://github.com/lczech/genesis.git", },
    "Treerecs": { "url": "https://gitlab.inria.fr/Phylophile/Treerecs.git", "all_commits": True, },
    "RAxML-ng": { "url": "https://github.com/amkozlov/raxml-ng.git", },
    # Solving
    "CVC4": { "url": "https://github.com/CVC4/CVC4.git", },
    "MiniSAT": { "url": "https://github.com/niklasso/minisat.git", },
    # Etc
    #"Parsec": { "url": "http://icl.utk.edu/parsec/", },
    "Charm++": { "url": "https://github.com/UIUC-PPL/charm.git", },
    "HPX": { "url": "https://github.com/STEllAR-GROUP/hpx.git", },
    "osrm-backend": { "url": "https://github.com/Project-OSRM/osrm-backend.git", },
    "CP2K": { "url": "https://github.com/cp2k/cp2k.git", "day_interval": 15, "all_commits": True, },
    "root": { "url": "https://github.com/root-project/root.git", },
    
    # BIG projects
    "Giraph": { "url": "https://github.com/apache/giraph.git", "all_commits": True, },
    "NetworkX": { "url": "https://github.com/networkx/networkx.git", },
    "PyTorch": { "url": "https://github.com/pytorch/pytorch.git", },
    "mlpack": { "url": "https://github.com/mlpack/mlpack.git", },
    "Z3": { "url": "https://github.com/Z3Prover/z3.git", },
    "folly": { "url": "https://github.com/facebook/folly.git", "all_commits": True, },
    "git": { "url": "https://github.com/git/git.git", "day_interval": 15, },
    "Mesos": { "url": "https://github.com/apache/mesos.git", "day_interval": 15, "all_commits": True, },
    "OpenMPI": { "url": "https://github.com/open-mpi/ompi.git", "day_interval": 15, },
    "MPICH": { "url": "https://github.com/pmodels/mpich.git", },
    "X10": { "url": "https://github.com/x10-lang/x10.git", "day_interval": 15, "all_commits": True, },
    "Spark": { "url": "https://github.com/apache/spark.git", },
    "Flink": { "url": "https://github.com/apache/flink.git", },
    "Hadoop": { "url": "https://github.com/apache/hadoop.git", },
    "Storm": { "url": "https://github.com/apache/storm.git", "day_interval": 15, },
    "Tensorflow": { "url": "https://github.com/tensorflow/tensorflow.git", "day_interval": 15, },
    "Arrow": { "url": "https://github.com/apache/arrow.git", "day_interval": 15, "all_commits": True, },
    "TuriCreate": { "url": "https://github.com/apple/turicreate.git", "day_interval": 60, "all_commits": True, },
    "DBeaver": { "url": "https://github.com/dbeaver/dbeaver.git", },
    "QuantLib": { "url": "https://github.com/lballabio/quantlib.git", },
    "RocksDB": { "url": "https://github.com/facebook/rocksdb.git", },
    "emacs": { "url": "https://github.com/emacs-mirror/emacs.git", "day_interval": 60, },
    "LLVM": { "url": "https://github.com/llvm/llvm-project.git", "day_interval": 60, "all_commits": True, },
    "gcc": { "url": "https://github.com/gcc-mirror/gcc.git", "day_interval": 60, "all_commits": True, },
    "Linux": { "url": "https://github.com/torvalds/linux.git", "day_interval": 365, },
    }

def decode(b_str):
    return b_str.decode("utf-8", "backslashreplace")

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
    if not os.path.exists(OUT_dir_tmp):
        os.makedirs(OUT_dir_tmp)
    OUT_dir_tmp = os.path.abspath(OUT_dir_tmp)

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
        out_file_tmp = OUT_dir_tmp + "/" + name + date_suffix + ".csv"
        out_file = OUT_dir + "/" + name + ".csv"
        original_branch = ""
        with open(out_file_tmp, "w") as output_file:
            if "url" not in idict:
                os.chdir(TMP_storage) # need to change dir since we skip the for
                continue
            run_cmd([GIT_binary, "clone", idict["url"], name], True)
            os.chdir(name)
            # --show-current only supported by git >= 2.22
            # git_show_current_branch = [GIT_binary, "branch", "--show-current"]
            git_show_current_branch = [GIT_binary, "symbolic-ref", "--short", "HEAD"]
            branch_out = run_cmd(git_show_current_branch, True)
            if len(branch_out.output) < 1:
                os.chdir(TMP_storage)
                shutil.rmtree(name, False) # remove directory recursively, throw on error
                run_cmd([GIT_binary, "clone", idict["url"], name], False)
                os.chdir(name)
            
            run_cmd([GIT_binary, "pull"], False)
            branch_out = run_cmd(git_show_current_branch)
            original_branch = branch_out.output[0]

            if "branch" in idict:
                run_cmd([GIT_binary, "checkout", idict["branch"]])
                run_cmd([GIT_binary, "pull"], False)
            log_list = []
            log_out = run_cmd([GIT_binary, "log",
                                 "--merges", # Only lists merge commits
                                 "--first-parent", # Only lists merge commits into current branch
                                 "--date=iso-strict",
                                 "--pretty=format:%ad{d}%H{d}%s".format(d=LOG_delim),
                              ])
            all_log_out = run_cmd([GIT_binary, "log",
                                  "--date=iso-strict",
                                  "--pretty=format:%ad{d}%H{d}%s".format(d=LOG_delim),
                                  ])
            if PRINT_DEBUG:
                begin = time.time()
                loc, loc_sum = call_cloc(idict)
                end = time.time()
                #own_print(output_file,
                print("Repo: {}\nTime: {} s\n".format(name, end-begin)
                      +"loc = {} ({})\n".format(loc, loc_sum)
                      +"num_commits: {}\ntotal_commits: {}"
                           .format(len(log_out.output), len(all_log_out.output)))
                print("Last commit: " + all_log_out.output[-1])

            if "all_commits" in idict and idict["all_commits"]:
                log_list = all_log_out.output
            else:
                log_list = log_out.output
            if "day_interval" in idict:
                log_list.sort(reverse=True) # Sort, so time goes backwards linearly
            own_print(output_file, "Date{d}Commit Hash{d}LOC{d}Total LOC".format(d=OUT_delim))

            #"""
            last_date = ""
            for line in log_list:
                spl = line.split(LOG_delim)
                date = spl[0]
                commit = spl[1]
                if last_date:
                    end_date = len("YYYY-MM-DD")
                    # Note: we look at the commits current -> last
                    prev_date = datetime.fromisoformat(last_date[:end_date])
                    cur_date = datetime.fromisoformat(date[:end_date])
                    difference = prev_date - cur_date
                    if "day_interval" in idict and difference.days < idict["day_interval"]:
                        #print("Skipping {}".format(line))
                        continue
                
                last_date = date
                

                # check out specific commit and count locs
                run_cmd([GIT_binary, "checkout", commit])
                loc, loc_sum = call_cloc(idict)
                own_print(output_file, "{}{d}{}{d}{}{d}{}".format(date, commit, loc, loc_sum,
                                                                  d=OUT_delim))
            #"""

            # At the end, go back to the original state
            run_cmd([GIT_binary, "checkout", original_branch])
        shutil.copyfile(out_file_tmp, out_file)
        os.chdir(TMP_storage)
        #shutil.rmtree(name, False) # remove directory recursively, throw on error

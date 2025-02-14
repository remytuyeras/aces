import sys
import json
import os
import random
import time
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(1, "./")
import pyaces as pyc

def save_data_to_jsonl(data, filename):
    with open(filename, 'w') as f:
        for line in data:
            f.write(json.dumps(line) + "\n")

def load_data_from_jsonl(filename):
    data = []
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            for line in f:
                data.append(json.loads(line))
    return data

def compute_and_save_times():
    axis_upperbound = 30
    add_data = []
    mult_data = []

    for n_tmp in range(2, axis_upperbound+1, 2):
        repartition = pyc.Repartition(n=n_tmp, p=2, upperbound=47601551)
        repartition.construct()
        for N_tmp in range(2, axis_upperbound+1, 2):
            for deg_u_tmp in range(2, axis_upperbound+1, 2):

                print(f"Compute for ({n_tmp,N_tmp,deg_u_tmp})")
                ac = pyc.ArithChannel(p=4, N=N_tmp, deg_u=deg_u_tmp, repartition=repartition)
                public = ac.publish(publish_levels=True)
                bob = pyc.ACES(**public, debug=False)
                alg = pyc.ACESAlgebra(**public, debug=False)

                # Add operation
                print("Add...")
                times = []
                for _ in range(30):
                    m1 = random.randrange(ac.p)
                    m2 = random.randrange(ac.p)
                    cip1 = bob.encrypt(m1)
                    cip2 = bob.encrypt(m2)
                    t0 = time.time()
                    cip_add = alg.add(cip1, cip2)
                    times.append(time.time() - t0)
                add_data.append((n_tmp, N_tmp, deg_u_tmp, np.mean(times)))

                # Mult operation
                print("Mult...")
                times = []
                for _ in range(30):
                    m1 = random.randrange(ac.p)
                    m2 = random.randrange(ac.p)
                    cip1 = bob.encrypt(m1)
                    cip2 = bob.encrypt(m2)
                    t0 = time.time()
                    cip_mult = alg.mult(cip1, cip2)
                    times.append(time.time() - t0)
                mult_data.append((n_tmp, N_tmp, deg_u_tmp, np.mean(times)))

    # Save results to JSONL
    save_data_to_jsonl(add_data, ".aces.speed.add.jsonl")
    save_data_to_jsonl(mult_data, ".aces.speed.mult.jsonl")

import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

def plot_performance(data, operation):
    # Prepare data for plotting
    variables = ['n_tmp', 'N_tmp', 'deg_u_tmp']

    avg_times: dict[str,dict[int,list]] = {var: {} for var in variables}
    for n_tmp, N_tmp, deg_u_tmp, avg in data:
        avg_times['n_tmp'].setdefault(n_tmp, [])
        avg_times['N_tmp'].setdefault(N_tmp, [])
        avg_times['deg_u_tmp'].setdefault(deg_u_tmp, [])

        avg_times['n_tmp'][n_tmp].append(avg)
        avg_times['N_tmp'][N_tmp].append(avg)
        avg_times['deg_u_tmp'][deg_u_tmp].append(avg)

    # Calculate mean and standard error for each variable
    mean_times: dict[str,list] = {var: [] for var in variables}
    stde_times: dict[str,list] = {var: [] for var in variables}
    for var in variables:
        avg_times_var = {k:v for k,v in sorted(avg_times[var].items(), key=lambda x: x[0])}
        for xval, yvals in avg_times_var.items():
            mean_times[var].append((xval, round(1000 * np.mean(yvals), 2)))
            stde_times[var].append((xval, round(1000 * np.std(yvals) / np.sqrt(len(yvals)), 2)))  # Standard error

    # Plot average time with standard error using bar plots
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))

    bar_width = 0.3  # Bar width
    opacity = 0.8    # Transparency of the bars

    for idx, var in enumerate(variables):
        x_vals, y_vals = zip(*sorted(mean_times[var], key=lambda x: x[0]))
        _, y_errs = zip(*sorted(stde_times[var], key=lambda x: x[0]))
        
        # Create bar plot with error bars
        ax.bar(
            np.array(x_vals) + idx * bar_width,  # Offset x values for each variable
            y_vals,
            bar_width,
            yerr=y_errs,
            label=f"Avg time vs {var}",
            capsize=5,
            alpha=opacity,
            align='center'
        )

    ax.set_title(f'Performance for {operation} in ms')
    ax.set_xlabel('Variable')
    ax.set_ylabel('Average Time (ms)')
    ax.legend()
    plt.tight_layout()  # Adjust the plot to make sure everything fits nicely
    plt.show()

if __name__ == "__main__":
    compute = len(sys.argv) > 1 and sys.argv[1].lower() == "compute"
    
    if compute:
        compute_and_save_times()

    # If files exist, load data
    add_data = load_data_from_jsonl(".aces.speed.add.jsonl")
    mult_data = load_data_from_jsonl(".aces.speed.mult.jsonl")

    if add_data:
        plot_performance(add_data, "Add")
    if mult_data:
        plot_performance(mult_data, "Mult")

import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def read_json_file(filename):
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON file '{filename}'.")
        return None


def generate_multiple_boxplots(data, labels, title, y_axis = "Milliseconds"):
    fig, ax = plt.subplots()
    ax.boxplot(data)
    ax.set_xticklabels(labels)
    ax.set_xlabel('Groups')
    ax.set_ylabel(y_axis)
    ax.set_title(title)
    plt.xticks(rotation=15)

def search_json_array(data, searched):
    # Iterate through the array
    for item in data:
        # Check if the 'name' attribute of the item matches the searched value
        if item.get('name') == searched:
            return item  # Return the matching item
    return None  # If no matching item found, return None


def calculate_statistics(data):
    """
    Calculate statistics (minimum, maximum, median, standard deviation, mean, and coefficient of variation) of a dataset.

    Parameters:
        data (array-like): The dataset for which to calculate the statistics.

    Returns:
        tuple: A tuple containing the calculated statistics rounded to 2 decimal places.
    """
    minimum = np.round(np.min(data), 2)
    maximum = np.round(np.max(data), 2)
    mean = np.round(np.mean(data), 2)
    median = np.round(np.median(data), 2)
    std_dev = np.round(np.std(data), 2)
    
    if mean > 0:
        cv = np.round(std_dev / mean, 2)
    else:
        cv = -1
    
    return minimum, maximum, median, std_dev, mean, cv

def extract_mean_values(statistics_table, backend):
    """
    Extracts all values from the "Arithmetic Mean" column for a benchmark with a specific name.

    Parameters:
        csv_file (str): The path to the CSV file containing the benchmark data.
        backend (str): The name of the benchmark to filter.

    Returns:
        list: A list containing all values from the "Arithmetic Mean" column for the specified benchmark.
    """
    try:
        
        # Filter rows based on the benchmark name
        filtered_df = statistics_table[statistics_table['Backend'] == backend]
        
        # Extract values from the "Arithmetic Mean" column
        mean_values = filtered_df['Arithmetic Mean'].tolist()
        result_dict = filtered_df.set_index('Benchmark')['Arithmetic Mean'].to_dict()

        return result_dict
    except Exception as e:
        print(f"Error occurred while extracting mean values: {e}")
        return None

def add_durations_to_global_array(datasets, datasetLabels, benchmark_name):
    # Iterate through JSON array
    allDurations = []
    allLabels = []
    global statistics_table
    for (data, backend) in zip(datasets, datasetLabels):
        item = search_json_array(data, benchmark_name)
        if item == None:
            continue
        # Access effekt.durations of each item and add to allDurations
        effekt_durations = item.get('effekt', {}).get('durations', [])
        this_name = item.get("name")
        assert benchmark_name == this_name or benchmark_name == None, f"benchmarkname = {benchmark_name}, this_name = {this_name} in {backend}"

        allDurations.append(effekt_durations)
        allLabels.append(backend)
        minimum, maximum, median, std, mean, cv = calculate_statistics(data=effekt_durations)
        statistics_table = statistics_table._append({'Backend': backend,"Benchmark": this_name, 'Minimum': minimum,
                                                    'Maximum': maximum, 'Arithmetic Mean': mean, "Standard Deviation": std,
                                                    'Median': median, "Coefficient of Variation": cv}, ignore_index=True)

    return allDurations, allLabels

def normalize_data_to_awfy():
    """
    Normalize the data points to the values corresponding to 'awfy-javascript'.

    Parameters:
        data (dict): A dictionary where keys are backend names and values are lists of performance values.

    Returns:
        dict: A dictionary where keys are backend names and values are lists of normalized performance values.
    """
    data = {}
    for i in all_data_labels:
        data[i] = extract_mean_values(statistics_table, i)

    normalized_data = {}
    
    # Find the index of 'awfy-javascript' in the list of keys
    awfy_index = list(data.keys()).index('awfy-javascript')
    
    # Extract the performance values of 'awfy-javascript'
    awfy_values = data['awfy-javascript']
    
    # Normalize the performance values of all backends to 'awfy-javascript'
    for backend, values in data.items():
        newvalues = {}
        for k,v in values.items():
            newvalues[k] = v/awfy_values[k]
        normalized_data[backend] = newvalues
    return normalized_data

def plot_mean_performance_by_benchmark(df):
    # Get unique benchmarks and their positions
    benchmarks = df['Benchmark'].unique()
    benchmark_positions = {benchmark: i for i, benchmark in enumerate(benchmarks)}

    unique_backends = df['Backend'].unique()
    # Set up the figure
    plt.figure(figsize=(10, 6))

    # Plot each backend's data points with the same color
    for backend in unique_backends:
        backend_data = df[df['Backend'] == backend]
        x_values = [benchmark_positions[benchmark] for benchmark in backend_data['Benchmark']]
        y_values = backend_data['Relative']
        plt.scatter(x_values, y_values, label=backend)

    # Set x-axis labels and tick positions
    plt.xticks(range(len(benchmarks)), benchmarks, rotation=30)
    plt.xlabel('Benchmark')
    plt.subplots_adjust(right=0.75)  # Adjust the right margin
    # Set y-axis label
    plt.ylabel('Relative durchschnittliche Performanz')
    plt.ylim(min(df['Relative']) - 0.1, max(df['Relative']) + 0.1)
    # Add legend
    plt.legend(title='Backend', bbox_to_anchor=(1.05, 1), loc='upper left')

    # Add grid
    plt.grid(True)

    # Set title
    plt.title("Normalisierte Performanz pro Benchmark und Backend")

  
    plt.savefig("fasteffekt_scatter_normalized.png")

def analyze_overall():
    normalized_benchmark_means_by_backend = normalize_data_to_awfy()
    listof_datapoints = [list(pointdict.values()) for pointdict in list(normalized_benchmark_means_by_backend.values())]
    generate_multiple_boxplots(
        listof_datapoints,
        normalized_benchmark_means_by_backend.keys(),
        "Normalized mean performance",
        "Relative to awfy-javascript")

    cumulative_perf_by_benchmark_backend = pd.DataFrame(columns=['Backend', 'Benchmark', 'Relative'])
    i = 0
    for benchmark in benchmark_names:
        for backend, means in normalized_benchmark_means_by_backend.items():
            benchmark_mean = -1
            if benchmark in means:
                benchmark_mean = means[benchmark]
            cumulative_perf_by_benchmark_backend = cumulative_perf_by_benchmark_backend._append({
                "Backend": backend, "Benchmark": benchmark, 'Relative': benchmark_mean
            }, ignore_index=True)
        i = i + 1
    cumulative_perf_by_benchmark_backend.to_csv(f"fasteffekt_mean_performance_by_benchmark.csv", index=False)
    plot_mean_performance_by_benchmark(cumulative_perf_by_benchmark_backend)

    plt.savefig(f"fasteffekt_mean_performance_normalized.png")


    normalized_statistics_KPI = pd.DataFrame(columns=['Backend', 'Minimum', 'Maximum', 'Median', "Standard Deviation", "Coefficient of Variation" ,'Arithmetic Mean',])


    for backend, means in normalized_benchmark_means_by_backend.items():
        minimum, maximum, median, std_dev, mean, cv = calculate_statistics(list(means.values()))
        normalized_statistics_KPI = normalized_statistics_KPI._append({'Backend': backend,'Minimum': minimum,
                                                    'Maximum': maximum, 'Arithmetic Mean': mean, "Standard Deviation": std_dev,
                                                    'Median': median, "Coefficient of Variation": cv}, ignore_index=True)

    normalized_statistics_KPI.to_csv(f"fasteffekt_mean_performance_KPI.csv", index=False)



js_effekt = read_json_file("./fasteffekt500_js.json")
monadic = read_json_file("./fasteffekt500_monadic.json")
callcc = read_json_file("./fasteffekt500_callcc.json")
lift = read_json_file("./fasteffekt500_lift.json")
js_awfy =  read_json_file("./fasteffekt500_javascript_awfy.json")

statistics_table = pd.DataFrame(columns=['Backend', "Benchmark",'Minimum', 'Maximum', 'Median', "Standard Deviation", "Coefficient of Variation" ,'Arithmetic Mean',])

all_data_labels = ["awfy-javascript","effekt-javascript", "effekt-monadic", "effekt-callcc",
                                                             "effekt-lift"]
columnIdx = 0
def draw_save_boxplot(name):
    durations, labels = add_durations_to_global_array([js_awfy,js_effekt, monadic, callcc, lift],
                                                         all_data_labels,
                                                            name)
    generate_multiple_boxplots(durations, labels, name)

    filename = f"fasteffekt_boxplot_{name}.png"
    plt.savefig(filename)


benchmark_names = ["permute", "nbody", "list", "mandelbrot", "bounce", "towers", "sieve", "storage", "queens", ]
for i in benchmark_names:
    draw_save_boxplot(i)

statistics_table.to_csv(f"fasteffekt_benchmarks_KPI.csv", index=False)

analyze_overall()



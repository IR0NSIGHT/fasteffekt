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
        
        return mean_values
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
        normalized_values = [np.round(value / awfy_values[i]) for i, value in enumerate(values)]
        normalized_data[backend] = normalized_values
    
    return normalized_data

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

statistics_table.to_csv(f"fasteffekt_keyvalues.csv", index=False)

normalized_benchmark_means_by_backend = normalize_data_to_awfy()
generate_multiple_boxplots(
    normalized_benchmark_means_by_backend.values(),
    normalized_benchmark_means_by_backend.keys(),
    "Normalized mean performance",
    "Relative to awfy-javascript")

filename = f"fasteffekt_mean_performance_normalized.png"
plt.savefig(filename)



import csv

'''Note from Evan, 07/07/2025:
This extremely niche script is being uploaded to my GitHub to help future GSFC Optics employees who 
find themselves needing to export data from the MicroVu, and are frustrated that the manufacturer
tools don't provide more customization options. I acknowledge there are some ways in which this script 
could be optimized to improve readability, but doing so is not in the cards at the moment.

The purpose of this script is to take the .csv file output by InSpec and rearrange the contents into 
a [GroupName, PointName, X, Y, Z] format, which can be easily imported to Spatial Analyzer, while 
using as few external packages as possible. Make sure to read the how-to Word document that is located
in the GitHub repo, or printed out alongside the MicroVu, to make sure you have exported your MicroVu
data properly.
'''

# Set to True to use a hardcoded filepath, or False to be presented with a pop-up window asking you to select a file
use_hardcoded_filepath = False

# Determine the filepath of the .csv file to be analyzed
if use_hardcoded_filepath is True:
    filepath = r"C:\Users\ebray\OneDrive - NASA\Python Programs\InSpec to SA\Sample Exported MicroVu Data.csv"
else:
    # Make a pop-up window that asks you where the files are located.
    import tkinter
    from tkinter.filedialog import askopenfilename
    root_window = tkinter.Tk()
    filepath = askopenfilename()
    root_window.destroy()

# Parse the original file and tidy things up
print(f'...Reading input data from {filepath}\n')
input_data = open(filepath).read().split('\n')  # Open the input file and break the contents into lines
print('Total lines read: ', len(input_data))
input_data = [element.replace('"', '') for element in input_data]  # Remove all the double quotes and replace them with single quotes
input_data = [element.split(',') for element in input_data]  # Break each line into individual elements
input_data = [row for row in input_data if row[0] != '']  # Remove the rows that contain a blank as the first element. Typically only the last line, for some reason.

# Process data for individual points
# InSpec exports data from individual points differently than for features that consist of many (x,y,z) points, 
# so we have to give those lines some special treatment
i = 0
while i < len(input_data):  # Because we're going to be inserting elements to the input_data array in real time, and we don't know a priori how many, we use a while loop.
    # If a point feature consists of a single measurement (as opposed to the best-fit measurement of many points) it will consist of 4 elements. 
    # This is the only time I've found this condition to be true.
    if len(input_data[i]) == 4: 
        input_data.insert(i + 1, input_data[i][1:]) # Insert a new row beneath the current one that consists of just the (x,y,z) coordinates.
        input_data[0] = [input_data[0][0]] # Change this row to be whatever name you named this point in InSpec
    i += 1

# Rows in the input file can take on several forms. For exmaple, a best-fit diameter of a circle, the name of a feature, or raw (X,Y,Z) ordered pairs. 
# Thankfully, these rows are always organized in the same order. So we start by making a little function that checks if a row consists of an (X,Y,Z) ordered pair


def is_this_row_a_coordinate(row):
    """
    Check if a row represents a valid 3-element coordinate. Returns True or False.

    A valid coordinate row must:
      - Contain exactly 3 elements.
      - Each element must be convertible to a float.
    """
    if len(row) != 3:
        return False
    try:
        return all(isinstance(float(element), float) for element in row)
    except (ValueError, TypeError):
        return False


# And now we run this function on every row of input_data. We'll refer to this array later. 
is_this_line_a_coordinate = [is_this_row_a_coordinate(row) for row in input_data]

# Create an output filename that is the same as the input, but with an extra string added to the end
output_filename = filepath[:-4] + ' - converted for SA.csv'  
print(f'...Creating output file at {output_filename}\n')

counter = 1  # We'll use a counter to keep track of how many points each feature is composed of. This is because each point in an SA point group must have a unique name.
feature_names = []  # A place to keep track of unique feature names

# Create the output file and prepare it for writing
with open(output_filename, mode='w', newline='') as file:  

    # Initialize the writer tool
    csv_writer = csv.writer(file, delimiter=',', quotechar='"')  

    # Loop through every line of the input file
    for i in range(len(input_data)):

        if is_this_line_a_coordinate[i] is False:  # If it's not a coordiante, then this row begins with the name of the feature that you gave it in InSpec. Record that name.
            most_recent_name = ' '.join(input_data[i][0].split(':')[0].split(' ')[1:])        
            counter = 1  # Reset the counter to 1
            feature_names.append(most_recent_name)
        else:  # Then this line must be a 3D coordinate. Compose a line that we'll append to the output .csv file
            line_to_add = [most_recent_name] + ['pt' + str(counter)] + input_data[i]  # Format the line to append in [GroupName, PointName, X, Y, Z] style
            csv_writer.writerow(line_to_add)  # Append the point information to the .csv file
            counter += 1  # Increase the counter by one

# Remove the repeats in the feature_names array
feature_names = list(set(feature_names))[1:]

print(f'Total number of features: {len(feature_names)}')            
print(f'Total number of points: {sum(is_this_line_a_coordinate)}')            
print('===== SUCCESS =====')
print('\a')  # Make a "ding" sound

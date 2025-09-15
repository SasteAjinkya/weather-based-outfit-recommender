# Let's create a Flask web application structure that mirrors your Tkinter functionality
# I'll generate the complete file structure with HTML templates, CSS, JavaScript, and Flask routes

import os

# Create the directory structure
directories = [
    'templates',
    'static/css',
    'static/js',
    'static/images',
    'static/icons'
]

for directory in directories:
    os.makedirs(directory, exist_ok=True)
    
print("Directory structure created:")
for directory in directories:
    print(f"  {directory}/")
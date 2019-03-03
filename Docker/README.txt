# HOW TO RUN THE DOCKER FILE:

# buil the docker container
# run the following line:

docker build -t group35 .

# run our program inside the container:
# change PATH to your current directory 
# run the following line:

docker run -it --rm -v "PATH":/app group35 SATsolver.py

# output.txt contains all True assigned variables
# sudoku-rules.txt contains the game rules
# sudoku-example.txt the initial constrains
# have fun ;)
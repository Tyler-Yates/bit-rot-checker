# Bit Rot Checker
Files can "rot" over time on a hard drive.
This project can be run periodically to validate that files are free from rot.

## How It Works
This program takes in a list of paths to check.
Every file under each path is processed (though some can be ignored through configuration).

When this program processes a file it has never seen before, it records data about that file in the database.
This is the "source of truth" when it comes to bit rot.
If this file deviates from this recorded data at any point in the future, it will be considered bit rot.
For privacy, the file path is hashed using SHA-256.
The CRC-32 and size of the file are also recorded.

If the program processes a file it has already seen before, it compares the data of the file on disk with what is found in the database.
If there is a difference, the file fails its verification and is logged.
You can find the logs for this program under the `logs` directory in the root of this project.

In case of interruptions, a recency dictionary is saved on disk.
Files that have been checked recently (timeframe is configurable) and passed verification will be skipped.

## Configuration
You will need to create a `config.json` file in the root of this project.
You can use the `config_example.json` file for a starting point:
```bash
cp config_example.json config.json
```

Fill out your computer-specific information in the `config.json` file.
This file should be ignored by git.

To customize this program's behavior, edit the file `bitrotchecker/src/constants.py`.

## Running
To run the program, you will first need to create and set up a virtual environment.
Run the following from the root of this project:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Now, run the program:
```bash
venv/bin/python -m bitrotchecker
```

## Development and Testing
To develop and test this program, you will need additional dependencies in your virtual environment:
```bash
pip install -r requirements.dev
```

You can run tests using Tox.
Tox will also automatically format the code.
```bash
tox
```

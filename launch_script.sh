#!/bin/bash
cd src
python -m robocorp.tasks run main.py -- --search_term $1 --months $2
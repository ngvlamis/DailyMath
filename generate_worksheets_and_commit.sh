#!/bin/bash

# Exit the script if any command fails
set -e

# Change to the target directory
cd /$HOME/DailyMath/

# Run python script to generator worksheets
python3 WorksheetGenerator/DailyMath_Worksheet_Generator.py

# Check to make sure git recognizes  changes
if [ -n "$(git status --porcelain)" ]; then
    # Add all changes
    git add .

    # Commit changes
    git commit -m "Automated commit: Re-generate worksheets"

    # Push changes to the remote repository
    git push origin main  # Push changes to main branch
else
    echo "No changes to commit."
fi
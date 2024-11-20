#!/bin/bash

# Exit the script if any command fails
set -e

# Change to the target directory
cd $HOME/GitHub/DailyMath/WorksheetGenerator/

# Activate the virtual environment
source $HOME/GitHub/DailyMath/WebsiteGenerator/.venv/bin/activate || exit 1  # Ensure virtualenv is activated

# Switch to correct git branch
git switch gh-pages

# Run python script to generator worksheets
python3 DailyMath_Worksheet_Generator.py

# Check to make sure git recognizes changes
if [ -n "$(git status --porcelain)" ]; then

    cd ..

    # Add all changes to worksheets
    git add worksheets/

    # Commit changes
    git commit -m "Automated commit: Re-generate worksheets"

    # Push changes to the remote repository
    git push origin gh-pages  # Push changes to testing-again branch

else
    echo "No changes to commit."
fi

# Deactivate the virtual environment
deactivate || exit 1  # Exit the virtual environment
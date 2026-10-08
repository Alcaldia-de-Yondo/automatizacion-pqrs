
# Create virtual environment
python -m venv .venv

# Activate the virtual environment
. .venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip

# Install production dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Install the package in editable mode
pip install -e .

# Install type stubs
pip install pandas-stubs types-openpyxl


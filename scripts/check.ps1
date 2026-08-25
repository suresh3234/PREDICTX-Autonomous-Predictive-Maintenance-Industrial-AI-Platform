Write-Host "Running project checks..."

python -m pytest
python -m ruff check .
python -m black --check .

Write-Host "Checks completed."
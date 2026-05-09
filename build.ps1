param(
    [string]$Python = ".\.venv\Scripts\python.exe"
)

& $Python -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --noconsole `
    --name HadesIIModUI `
    --distpath dist `
    --workpath build `
    --specpath build `
    src\main.py

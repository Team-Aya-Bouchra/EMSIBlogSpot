Add-Type -AssemblyName System.IO.Compression.FileSystem

$source  = 'c:\xampp\htdocs\EMSIBlogSpot'
$dest    = 'c:\xampp\htdocs\EMSIBlogSpot_submission.zip'
$exclude = @('venv', '__pycache__', 'scratch', '.git', 'node_modules')
$excludeFiles = @('credentials.md', 'db.sqlite3', 'make_zip.ps1', 'EMSIBlogSpot_submission.zip')
$excludeExt  = @('.pyc', '.pyo')

# Remove old zip if it exists
if (Test-Path $dest) { Remove-Item $dest }

$zip = [System.IO.Compression.ZipFile]::Open($dest, 'Create')

$files = Get-ChildItem -Path $source -Recurse -File

foreach ($file in $files) {
    $rel = $file.FullName.Substring($source.Length).TrimStart('\')
    $parts = $rel -split '\\'

    # Check if any path component is in the excluded dirs list
    $skip = $false
    foreach ($part in $parts) {
        if ($part -in $exclude) { $skip = $true; break }
    }

    # Check excluded filenames
    if ($file.Name -in $excludeFiles) { $skip = $true }

    # Check excluded extensions
    if ($file.Extension -in $excludeExt) { $skip = $true }

    if (-not $skip) {
        $entryName = 'EMSIBlogSpot\' + $rel
        Write-Host "Adding: $entryName"
        [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $file.FullName, $entryName, 'Optimal') | Out-Null
    }
}

$zip.Dispose()
Write-Host ""
Write-Host "Done! Submission zip created at: $dest"

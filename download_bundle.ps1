# Download all pinned wheels for the offline Linux/cp310 bundle.
# pip's --platform matching is literal, so every manylinux glibc level
# from the target baseline (2.31) down to 2.5 must be listed explicitly.
$ErrorActionPreference = 'Continue'
$dest  = Join-Path $PWD 'vllm_transformers_offline_bundle'
$log   = Join-Path $PWD 'pip-download.log'
New-Item -ItemType Directory -Force -Path $dest | Out-Null

$platformArgs = @()
foreach ($minor in 31..5) { $platformArgs += @('--platform', "manylinux_2_${minor}_x86_64") }
$platformArgs += @('--platform', 'manylinux2014_x86_64')
$platformArgs += @('--platform', 'manylinux2010_x86_64')
$platformArgs += @('--platform', 'manylinux1_x86_64')

"[start] $(Get-Date -Format s)  platforms=$($platformArgs.Count / 2)" | Out-File -FilePath $log -Encoding utf8

pip download --no-deps -r .\requirements.lock @platformArgs `
  --python-version 3.10 --implementation cp --only-binary=:all: `
  --retries 10 --timeout 60 `
  --dest $dest 2>&1 | Tee-Object -FilePath $log -Append

"[exit] $LASTEXITCODE  $(Get-Date -Format s)" | Tee-Object -FilePath $log -Append

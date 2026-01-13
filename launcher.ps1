$env:PYTHONUTF8 = '1'
[System.Console]::OutputEncoding = [System.Text.Encoding]::UTF8

#설정 파일 넣거나 추가하는 곳 ↓↓↓
C:\manga-image-translator\venv\Scripts\python.exe -m manga_translator local `
    --config-file C:\manga-image-translator\config.json `
    --overwrite `
    --context-size 5 `
    --attempts 10 `
    -i C:\manga-image-translator\manga `
    --pre-dict C:\manga-image-translator\dict\manga_predict.txt `
    --post-dict C:\manga-image-translator\dict\manga_postdict.txt `
    --format png `
    --use-gpu `
    --font-path C:\manga-image-translator\fonts\Arial-Unicode-Regular.ttf `
    `
    2>&1 | ForEach-Object {
        $line = $_.ToString()
        if ($line -match 'ERROR:|Traceback|Exception|Error code:|error:') {
            Write-Host $line -ForegroundColor Red
        }
        else {
            Write-Host $line
        }
        Add-Content -Path 'C:\manga-image-translator\translation_log.txt' -Value $line -Encoding UTF8
    }

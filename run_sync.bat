@echo off
echo Bookmark Sync to Notion を開始します...
echo 実行時刻: %date% %time%

rem カレントドライブをバッチファイルのあるドライブに変更
%~d0
rem バッチファイルのある場所のsrcフォルダに移動
cd "%~dp0src"

rem Pythonの実行を試みる
echo Pythonスクリプトを実行中...
python main.py

if %ERRORLEVEL% EQU 0 (
    echo 同期が正常に完了しました。
) else (
    echo エラーが発生しました。
)

echo ログを確認してください。
pause
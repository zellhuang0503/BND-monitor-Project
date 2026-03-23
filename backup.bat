@echo off
echo ==============================================
echo [BND Monitor] 開始執行每日報告自動備份任務
echo 備份時間: %date% %time%
echo ==============================================

cd /d "C:\Users\zellh\Coding Projects\BND monitor Project"

:: 1. 備份到本地端資料夾 (Vault)
echo [本地備份] 正在複製報告中...
if not exist "C:\Users\zellh\BND Moniter Vault" mkdir "C:\Users\zellh\BND Moniter Vault"
xcopy "reports\*" "C:\Users\zellh\BND Moniter Vault\" /Y /I /E > nul
echo [本地備份] 報告已成功複製到 BND Moniter Vault！

:: 2. 備份到 GitHub 上
echo.
echo [雲端備份] 正在推播至 GitHub...
git add reports/ index.html
git commit -m "Auto backup reports: %date% %time%"
git push origin main

echo.
echo ==============================================
echo 雙重備份 (GitHub + 本地 Vault) 均已完成！
echo ==============================================
timeout /t 5 > nul
exit

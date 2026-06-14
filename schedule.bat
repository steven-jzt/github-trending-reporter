@echo off
set DIR=%~dp0

powershell -NoProfile -Command "$a = New-ScheduledTaskAction -Execute '%DIR%run_daily.bat'; $t = New-ScheduledTaskTrigger -Daily -At 09:00; Register-ScheduledTask -TaskName 'GitHubTrendingDaily' -Action $a -Trigger $t -Force"
powershell -NoProfile -Command "$a = New-ScheduledTaskAction -Execute '%DIR%run_weekly.bat'; $t = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 09:00; Register-ScheduledTask -TaskName 'GitHubTrendingWeekly' -Action $a -Trigger $t -Force"
powershell -NoProfile -Command "$a = New-ScheduledTaskAction -Execute '%DIR%run_monthly.bat'; $t = New-ScheduledTaskTrigger -Monthly -DaysOfMonth 1 -At 09:00; Register-ScheduledTask -TaskName 'GitHubTrendingMonthly' -Action $a -Trigger $t -Force"
echo Scheduled tasks registered:
echo   GitHubTrendingDaily  - every day at 09:00
echo   GitHubTrendingWeekly - every Monday at 09:00
echo   GitHubTrendingMonthly - 1st of each month at 09:00
pause

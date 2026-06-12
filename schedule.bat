@echo off
powershell -NoProfile -Command "$a = New-ScheduledTaskAction -Execute 'python' -Argument 'C:\Users\steve\Desktop\抓取提交\main.py daily'; $t = New-ScheduledTaskTrigger -Daily -At 09:00; Register-ScheduledTask -TaskName 'GitHubTrendingDaily' -Action $a -Trigger $t -Force"
powershell -NoProfile -Command "$a = New-ScheduledTaskAction -Execute 'python' -Argument 'C:\Users\steve\Desktop\抓取提交\main.py weekly'; $t = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 09:00; Register-ScheduledTask -TaskName 'GitHubTrendingWeekly' -Action $a -Trigger $t -Force"
echo Done
pause

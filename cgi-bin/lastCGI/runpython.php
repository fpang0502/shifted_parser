<?php
$output = shell_exec("python /var/www/html/shiftedenergy.com/setpoint/api/automategreen/powercontroller/python-cron/cgi-bin/alldata.py 2>&1");
print $output;
$output = shell_exec("python /var/www/html/shiftedenergy.com/setpoint/api/automategreen/powercontroller/python-cron/cgi-bin/increments.py 2>&1");
print $output;
?>

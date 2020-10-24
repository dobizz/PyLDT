# PyLDT
Python Automation for PLDT Fibr ONU Router

# Usage
Run script
```
python3 PyLDT.py
```
Current script contains a PyLDT Python class for configuring your PLDT Fibr ONU Router and does the following things:

1. Check if https://192.168.1.1/fh is available and accepting requests.
2. Logon using `fibersuperadmin` credentials and enable `telnet`, `webadmin switch`, and  `omci debug`.
3. Connect to the modem via `telnet` on `port 22` and `disable AP isolation` so that you can use all of the LAN ports of your router.

##### Best used as a crontab task in Linux or scheduled task in Windows. 

# Assumptions
1. The ipv4 address of your router is 192.168.1.1 and is reachable from the device running this software
2. You are the owner or have authority over the router
3. There are no firewalls or restrictions that prevent or block you from reaching port 22 of the router

# Dependencies
## ChromeBrowser
Download Google Chrome Browser https://www.google.com/intl/en/chrome/

## ChromeDriver
Download your version of ChromeDriver https://chromedriver.chromium.org/

Make sure that the path to the chromedriver executable is included in the system path.

## Python Pakages
Install all the required Python packages
```
pip install -r requirements.txt
```

### Available Telnet Commands

#### User Exec Mode
```
Login: gepon
Password: gepon

User>
```

##### Command List
 0. clear
 1. enable
 2. exit
 3. help
 4. list
 5. ping {[-t]}*1 {[-count] <1-65535>}*1 {[-size] <1-6400>}*1 {[-waittime] <1-255>}*1 {[-ttl] <1-255>}*1 {[-pattern] <user_pattern>}*1 {[-i] <A.B.C.C>}*1 <A.B.C.D>
 6. quit
 7. show history
 8. show idle-timeout
 9. show ip
10. show services
11. show syscontact
12. show syslocation
13. terminal length <0-512>
14. who
15. who am i


#### Global Config Mode
From User Exec Mode key in `enable` and type the correct password to enter Global Config Mode
```
User>
User> enable
Password: *****

Config# _
```

##### Command List
 0. cd [..|device|service|switch|codec|dsp|protocol|pon|gpon|omci|wlan|tr069|wan|igmp|gponl3|oam|ntp|mld|web]
 1. clear
 2. download ftp [system|config]  <A.B.C.D> <username> <password> <filename>
 3. erase {startup-config}*1
 4. exit
 5. help
 6. list
 7. quit
 8. reboot
 9. resettings
10. save {configuration}*1
11. show cpu use
12. show flash use
13. show history
14. show memory use
15. show running-config
16. show startup-config
17. show time
18. show version
19. upload ftp config  <A.B.C.D> <username> <password> <filename>
20. upload ftp syslog  <A.B.C.D> <username> <password> <filename>

#### Debug Mode
From User Exec Mode or Global Config Mode key in `ddd` to enter Debug Mode
```
User>
User> ddd
WRI(DEBUG_H)> _
```

```
Config#
Config# ddd
WRI(DEBUG_H)> _
```

##### Command List
 0. active section [0|1]
 1. bobtest read_regs slave_addr <0-255> begin_addr <0-255> count <1-32>
 2. bobtest write_regs slave_addr <0-255> begin_addr <0-255> count <1-32> value1 <0-255> {value2 <0-255>}*1  {value3 <0-255>}*1 {value4 <0-255>}*1 {value5 <0-255>}*1 {value6 <0-255>}*1 {value7 <0-255>}*1 {value8 <0-255>}*1 {value9 <0-255>}*1 {value10 <0-255>}*1 {value11 <0-255>}*1 {value12 <0-255>}*1 {value13 <0-255>}*1 {value14 <0-255>}*1 {value15 <0-255>}*1 {value16 <0-255>}*1 {value17 <0-255>}*1 {value18 <0-255>}*1 {value19 <0-255>}*1 {value20 <0-255>}*1 {value21 <0-255>}*1 {value22 <0-255>}*1 {value23 <0-255>}*1 {value24 <0-255>}*1 {value25 <0-255>}*1 {value26 <0-255>}*1 {value27 <0-255>}*1 {value28 <0-255>}*1 {value29 <0-255>}*1 {value30 <0-255>}*1 {value31 <0-255>}*1 {value32 <0-255>}*1
 3. clear
 4. commit section [0|1]
 5. config ploam_log [enable| disable]
 6. config test clear_all_gemport_cnt
 7. config test mib_del_hi_tcont_alloc [0|1]
 8. config test web_acl_mode port <0-3> mode <0-2> type <0-2>
 9. config test web_acl_rule port <0-3> is_ipv6 <0-1> vid <0-4095>
10. config upgrade_window_size <3characters>
11. control opticalgenerator [enable|disable|off] {mode [hf0101 |lf0101 |mix |user |prbs7|prbs15|prbs23|prbs31]}*1
12. control test up_optical_tx [auto| always_on | off] {tx_level [high |low]}*1
13. debug cli_msg id <id>
14. debug cli_msg send_buf <buf>
15. delete onuhw version
16. dumpenv
17. exit
18. fandebug [enable|disable]
19. fhdrv_kdrv_i2c read <0-10> <0-255> <0-255> <0-255>
20. fhdrv_kdrv_i2c write <0-10> <0-255> <0-255> <0-255>
21. get image status
22. get nvram <name>
23. get saveflags status
24. get system status
25. get upgrade mem mode
26. get version info
27. get web [user|admin] username <name>
28. help
29. i2c read <ADDR> <REG>
30. i2c write <ADDR> <REG> <VALUE>
31. list
32. mibreset
33. optdebug [enable|disable]
34. output redirect
35. printenv env_key [fhsnoui|FHSNOUI|ethaddr]
36. quit
37. read gpio <0-256>
38. read i2c device page <0-255> addr <0-255>
39. run [local_config]
40. run [omci_tl]
41. set bar code [pcb|bosa] <barcode>
42. set catv rf offset <offset>
43. set console [on|off|reboot_on|reboot_off]
44. set default-printf-to [disable|console|telnet|all]
45. set electricfan run temperature <0-100> stop temperature <0-100>
46. set nvram <NAME> <VALUE>
47. set onuhw version <onuhw>
48. set opt rxpoweradjust1 min <rxmin> max <rxmax> offset <rxoffset>
49. set opt rxpoweradjust2 min <rxmin> max <rxmax> offset <rxoffset>
50. set optoutpower level <0-2>
51. set optoutpower offset <outoffset>
52. set optpoll [enable|disable]
53. set ponrate_config_switch <0-1>
54. set upgrade mem mode <0-255>
55. set web [user|admin] username <name> password <value>
56. set web default [user|admin] username <name> password <value>
57. setbuttondebug [disable|enable|ver|start]
58. setleddebug [disable|enable|on|off]
59. setlog [omci|none] [old|pkt|timer|conf|temp|info|none|warning]
60. setpmlog <0-1>
61. setusbdebug
62. shell
63. show [ponrate_config_switch]
64. show bar code [pcb|bosa]
65. show debugversion
66. show electricfan work temperature
67. show flash use
68. show history
69. show optoutpower level
70. show optoutpower offset
71. show optrxpower adjust
72. show power supply
73. show prbs_bist_error_state
74. show rf power
75. show test web_acl_mode port <0-3>
76. show test web_acl_rule port <0-3>
77. show upgrade_window_size
78. test led <index> <status>
79. tshell
80. updateenv [fhsnoui|FHSNOUI|ethaddr] <VALUE>
81. upload ftp any  <A.B.C.D> <username> <password> <path> <filename>
82. write gpio <0-256> <0-1>
83. write i2c device page <0-255> addr <0-255> value <0-255>


# Disclaimer

Use at your own risk. In no event shall we be liable to you or any third parties for any special, punitive, incidental, indirect or consequential damages of any kind, or any damages whatsoever, including, without limitation, those resulting from loss of use, data or profits, and on any theory of liability, arising out of or in connection with the use of this software.
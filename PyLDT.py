#!/usr/bin/python3
import re
import sys
import time
import requests
import selenium
import telnetlib
from enum import Enum
from collections import namedtuple
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options


# default credentials
HOST = '192.168.1.1'
TELNET_USER = 'gepon'
TELNET_PASS = 'gepon'
TELNET_PORT = 23
TIMEOUT = 10
FIBERHOMESUPERADMIN_USER = 'f9!6b1e1rhO3es~u!p@e#r$a%d^m*i(n'
FIBERHOMESUPERADMIN_PASS = 's)f_U+h|g{u@5h2o1q0b1l'


# Globals
USER_EXEC = b'User> '
GLOBAL_CONFIG = b'Config# '


class Privilege(Enum):
    NONE = -1
    USER = 0
    CONFIG = 1
    DEBUG = 2


class Mode(Enum):
    ON = 'enable'
    OFF = 'disable'


class PyLDT:

    def __init__(self, host, username, password, port, timeout):
        self.__host = host
        self.__user = username
        self.__pass = password
        self.level = Privilege.NONE

        try:
            self.tn = telnetlib.Telnet(self.__host, port, timeout)
            self.read_until('Login: ')
            print('Login: ')
            self.write(self.__user)
            if password:
                self.read_until(b'Password: ')
                print('Password: ')
                self.write(self.__pass)
            self.read_until(USER_EXEC)
            self.level = Privilege.USER
            print('User> ')

        except Exception as e:
            sys.exit(e)

    ### decorators ###
    def clear_terminal(func):
        def wrapper(self, *arg, **kwargs):
            self.write('clear')
            self.tn.expect([GLOBAL_CONFIG, USER_EXEC], TIMEOUT)
            x = func(self, *arg, **kwargs)
            return x
        return wrapper
    ##################


    def write(self, cmd):
        '''wrapper for telnet write'''
        self.tn.write(cmd.encode('ascii') if type(cmd) == str else cmd)
        self.tn.write(b'\n')


    def read_until(self, marker):
        '''wrapper for telnet read_until'''
        return self.tn.read_until(marker.encode('ascii') if type(marker) == str else marker, TIMEOUT).decode('ascii')


    ### User Exec Commands ###
    @clear_terminal
    def user_ping(self, host='127.0.0.1', count=5, verbose=False):
        '''User> list\n5. ping {[-t]}*1 {[-count] <1-65535>}*1 {[-size] <1-6400>}*1 {[-waittime] <1-255>}*1 {[-ttl] <1-255>}*1 {[-pattern] <user_pattern>}*1 {[-i] <A.B.C.C>}*1 <A.B.C.D>'''
        Ping = namedtuple('Ping', ('tx', 'rx', 'loss'))
        if self.level == Privilege.USER:
            self.write(f'ping -count {count} {host}')
            reply = self.read_until('packet loss')
            if verbose: print(reply)
            ping = Ping(*re.findall(r'(\d+)%* packet', reply))
        else:
            ping = Ping(None, None, None)
        return ping


    def user_show_history(self):
        '''User> list\n7. show history'''
        pass


    def user_show_idle_timeout(self):
        '''User> list\n8. show idle-timeout'''
        pass


    def user_show_ip(self):
        '''User> list\n9. show ip'''
        pass


    @clear_terminal
    def user_show_services(self):
        '''User> list\n10. show services'''
        services = None
        if self.level == Privilege.USER:
            self.write('show services')
            services = self.read_until(USER_EXEC)
        return services


    def user_show_syscontact(self):
        '''User> list\n11. show syscontact'''
        pass


    def user_show_syslocation(self):
        '''User> list\n12. show syslocation'''
        pass


    @clear_terminal
    def user_terminal_length(self, length=512):
        '''User> list\n13. terminal length <0-512>'''
        self.write(f'terminal length {length}')
        self.read_until(USER_EXEC)


    @clear_terminal
    def user_who(self):
        '''User> list\n14. who'''
        if self.level == Privilege.USER:
            self.write('who')
            reply = self.read_until('current system.')
            return reply
        else:
            print(f'Not in User> mode.')


    def user_whoami(self):
        '''User> list\n15. who am i'''
        pass


    ### Global Config Commands ###
    @clear_terminal
    def enable(self):
        '''User> list\n1. enable'''
        ### enter global config mode ###
        if self.level == Privilege.USER:
            self.write('enable')
            if self.__pass:
                self.read_until('Password: ')
                self.write(self.__pass)
            reply = self.tn.expect([b'Password: ', b'Config# '], TIMEOUT)[-1].decode('ascii')
            
            if 'Bad Password' in reply:
                sys.exit('Bad Password. Please retry.')
                
            elif 'Config#' in reply:
                print('Config#')
                self.level = Privilege.CONFIG
                return True
            else:
                return False
        elif self.level == Privilege.CONFIG:
            print('Already in Config# mode.')
            return True
        else:
            return False


    ### Config\switch# ###
    @clear_terminal
    def config_ap_isolation(self, mode=Mode.OFF):
        '''Config\switch#\n3. control port_fw_eligiblity_switch [enable|disable]'''
        ### enables inter lan communicaton ###
        if self.level == Privilege.CONFIG:
            self.write('cd switch')
            self.read_until('Config\switch# ')
            self.write(f'control port_fw_eligiblity_switch {mode.value}')
            reply = self.read_until('Config\switch# ')
            self.write('cd ..')
            self.read_until(GLOBAL_CONFIG)
            return 'Cmd success!' in reply

        else:
            print('Not in Config# mode.')
            return False


    @clear_terminal
    def config_show_lan_status(self, verbose=False):
        '''Config\switch#\n13. show lan_port_all_status'''
        if self.level == Privilege.CONFIG:
            LanState = namedtuple('LanState', 
                ('lan_port', 'port_state', 'negotioation', 'phy_link_status', 'phy_workmode', 'port_capacity', 'pause_status'))
            lan_status = []
            self.write('cd switch')
            self.read_until('Config\switch# ')
            self.write(f'show lan_port_all_status')
            reply = self.read_until('Config\switch# ')
            self.write('cd ..')
            _ = self.read_until(GLOBAL_CONFIG)
            if verbose: print(reply)
            return [LanState(*lan) for lan in re.findall(r'(\w+)\s+?(\w+)\s+?(\w+)\s+?([\w_-]+)\s+?([\w_-]+)\s+?(\w+)\s+?(\w+)', reply)[1:]]

        else:
            print('Not in Config# mode.')
            return False


    ### Config\service# ###
    @clear_terminal
    def config_service_telnet(self, mode=Mode.ON):
        '''Config\service#\n8. service telnet [enable|disable]'''
        if self.level == Privilege.CONFIG:
            self.write('cd service')
            self.read_until('Config\service# ')
            self.write(f'service telnet {mode.value}')
            reply = self.read_until('Config\service# ')
            self.write('cd ..')
            self.read_until(GLOBAL_CONFIG)
            if verbose: print(reply)
            return True

        else:
            print('Not in Config# mode.')
            return False


    def config_download_ftp(self, host, username, password, filename, system=True):
        '''Config# \n2. download ftp [system|config] <A.B.C.D> <username> <password> <filename>'''
        pass


    def config_reboot(self):
        '''Config# \n8. reboot'''
        pass


    @clear_terminal
    def config_save(self):
        '''Config# \n10. save {configuration}*1'''
        ### save config to flash ###
        if self.level == Privilege.CONFIG:
            self.write('save')
            reply = self.read_until(GLOBAL_CONFIG)
            return 'Configuration save to flash successfully.' in reply
            
        else:
            print('Not in Config# mode.')
            return False


    def config_show_cpu_use(self):
        '''Config# list\n11. show cpu use'''
        pass


    def config_show_flash_use(self):
        '''Config# list\n12. show flash use'''
        pass


    def config_show_memory_use(self):
        '''Config# list\n14. show memory use'''
        pass


    @clear_terminal
    def config_show_running(self, verbose=False):
        '''Config# list\n15. show running-config'''
        if self.level == Privilege.CONFIG:
            self.write('show running-config')
            running_config = ''
            reply = ''
            while '\nConfig#' not in reply:
                reply = self.tn.expect([b'--Press any key to continue Ctrl+b to stop--', GLOBAL_CONFIG], TIMEOUT)[-1].decode('ascii')#.replace('\r\n  --Press any key to continue Ctrl+b to stop-- \x1b[2J', '')
                reply = reply.replace('\r\n  --Press any key to continue Ctrl+b to stop-- \x1b[2J', '')
                if verbose: print(reply)
                self.write('\n')
                running_config += reply
            running_config = running_config.replace('\n\r\n  --Press any key to continue Ctrl+b to stop-- \x1b[2J', '')
            return running_config
            
        else:
            print('Not in Config# mode.')
            return False


    @clear_terminal
    def config_show_startup(self, verbose=False):
        '''Config# list\n16. show startup-config'''
        if self.level == Privilege.CONFIG:
            self.write('show startup-config')
            startup_config = ''
            reply = ''
            while '\nConfig#' not in reply:
                reply = self.tn.expect([b'--Press any key to continue Ctrl+b to stop--', GLOBAL_CONFIG], TIMEOUT)[-1].decode('ascii')
                reply = reply.replace('\r\n  --Press any key to continue Ctrl+b to stop-- \x1b[2J', '')
                if verbose: print(reply)
                self.write('\n')
                startup_config += reply
            # startup_config = startup_config.replace('\n\r\n  --Press any key to continue Ctrl+b to stop-- \x1b[2J', '')
            return startup_config
            
        else:
            print('Not in Config# mode.')
            return False


    def config_show_time(self):
        '''Config# list\n17. show time'''
        pass


    @clear_terminal
    def config_show_version(self, verbose=False):
        '''Config# list\n18. show version'''
        if self.level == Privilege.CONFIG:
            Version = namedtuple('Version', ('hw', 'sw'))
            self.write('show version')
            reply = self.read_until('\nConfig#')
            if verbose: print(reply)
            hw_ver = re.search(r'Hardware version : (.+)', reply).group(1).strip()
            sw_ver = re.search(r'Software version : (.+)', reply).group(1).strip()
            min_ver = re.search(r'Minor version : (.+)', reply).group(1).strip()
            software_version = f"{sw_ver}({min_ver})"
            return Version(hw_ver, software_version)

        else:
            print('Not in Config# mode.')
            return False
            
    def config_upload_ftp(self, host, username, password, filename):
        '''Config# list\n19. upload ftp config <A.B.C.D> <username> <password> <filename>'''
        pass


    def config_upload_ftp_syslog(self, host, username, password, filename):
        '''Config# list\n20. upload ftp syslog <A.B.C.D> <username> <password> <filename>'''
        pass
        
    ### Debug Mode ###
    '''
    User> ddd
    WRI(DEBUG_H)> shell

    # get `adminpldt` admin password
    get web admin username adminpldt

    # get `admin` user password
    get web user username admin

    Command list:
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
    '''

    def enter_debug_mode(self):
        ''' '''
        success = False
        if success:
            self.level = Privilege.DEBUG

    def get_web_password(self, username, admin_flag=False):
        '''27. get web [user|admin] username <name>'''
        cmd = 'get web {"admin" if admin_flag else "user"} username {username}'


def disable_ap_isolation():
    tel = PyLDT(host=HOST, username=TELNET_USER, password=TELNET_PASS, port=TELNET_PORT, timeout=TIMEOUT)
    tel.enable()
    tel.config_ap_isolation(Mode.OFF)


def webadmin_enable():
    chrome_options = Options()  
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Chrome(options=chrome_options)

    base_url = 'https://192.168.1.1'

    # login
    login_url = f'{base_url}/login_pldt.asp'
    driver.get(login_url)
    e = driver.find_element_by_xpath('//*[@id="User"]')
    e.send_keys(FIBERHOMESUPERADMIN_USER)
    e = driver.find_element_by_xpath('//*[@id="Passwd"]')
    e.send_keys(FIBERHOMESUPERADMIN_PASS)
    e = driver.find_element_by_xpath('//*[@id="submit"]')
    e.click()
    
    # enable switches
    enable_url = f'{base_url}/fiberhome/telnet_enable.asp'
    driver.get(enable_url)

    # telnet
    telnet_switch = driver.find_element_by_xpath('/html/body/form/table[1]/tbody/tr/td[2]/input[1]')
    telnet_switch.click()
    telnet_apply = driver.find_element_by_xpath('//*[@id="telnet_apply"]')
    telnet_apply.click()

    # webadmin
    webadmin_switch = driver.find_element_by_xpath('//*[@id="div_adminenable"]/form/table[1]/tbody/tr/td[2]/input[1]')
    webadmin_switch.click()
    webadmin_apply = driver.find_element_by_xpath('/html/body/div[1]/form/table[2]/tbody/tr/td[2]/input[1]')
    webadmin_apply.click()

    # omci debug
    omci_debug_switch = driver.find_element_by_xpath('//*[@id="div_omciDebug"]/form/table[1]/tbody/tr/td[2]/input[1]')
    omci_debug_switch.click()
    omci_debug_apply = driver.find_element_by_xpath('//*[@id="omci_apply"]')
    omci_debug_apply.click()

    menu_url = f'{base_url}/menu_pldt.asp'
    driver.get(menu_url)

    logout = driver.find_element_by_xpath('//*[@id="headerLogoutSpan"]')
    logout.click()
    driver.quit()


def webadmin_disable():
    chrome_options = Options()  
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Chrome(options=chrome_options)

    base_url = 'https://192.168.1.1'

    # login
    login_url = f'{base_url}/login_pldt.asp'
    driver.get(login_url)
    e = driver.find_element_by_xpath('//*[@id="User"]')
    e.send_keys(FIBERHOMESUPERADMIN_USER)
    e = driver.find_element_by_xpath('//*[@id="Passwd"]')
    e.send_keys(FIBERHOMESUPERADMIN_PASS)
    e = driver.find_element_by_xpath('//*[@id="submit"]')
    e.click()
    
    # enable switches
    enable_url = f'{base_url}/fiberhome/telnet_enable.asp'
    driver.get(enable_url)

    # telnet
    telnet_switch = driver.find_element_by_xpath('/html/body/form/table[1]/tbody/tr/td[2]/input[2]')
    telnet_switch.click()
    telnet_apply = driver.find_element_by_xpath('//*[@id="telnet_apply"]')
    telnet_apply.click()

    # webadmin
    webadmin_switch = driver.find_element_by_xpath('//*[@id="div_adminenable"]/form/table[1]/tbody/tr/td[2]/input[2]')
    webadmin_switch.click()
    webadmin_apply = driver.find_element_by_xpath('/html/body/div[1]/form/table[2]/tbody/tr/td[2]/input[1]')
    webadmin_apply.click()

    # omci debug
    omci_debug_switch = driver.find_element_by_xpath('//*[@id="div_omciDebug"]/form/table[1]/tbody/tr/td[2]/input[2]')
    omci_debug_switch.click()
    omci_debug_apply = driver.find_element_by_xpath('//*[@id="omci_apply"]')
    omci_debug_apply.click()

    menu_url = f'{base_url}/menu_pldt.asp'
    driver.get(menu_url)

    logout = driver.find_element_by_xpath('//*[@id="headerLogoutSpan"]')
    logout.click()
    driver.quit()


if __name__ == '__main__':
    max_tries = 5
    timeout = 30
    for trial in range(max_tries):
        try:
            reply = requests.get('https://192.168.1.1/fh', verify=False, timeout=timeout)
        except Exception as e:
            print(f'{e}. Trying again in {timeout} seconds.')
            time.sleep(timeout)
        else:
            if reply.status_code == 200:
                print('Webserver responding.')
                webadmin_enable()
                disable_ap_isolation()
                break
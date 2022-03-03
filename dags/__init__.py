# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# rock 2021-09-22 ver0.1

import os
import sys

# $Mac 開發機
mac_home = '/Users/Rock/Documents/project_file'
mac_p    = f'{mac_home}/crawl_project'
# $Centos 部署機
cen_home = '/home/Rock/Documents'
cen_p    = f'{cen_home}/crawl_project'

if os.path.exists(mac_p):
    basic_path = mac_p
    home_path  = mac_home
    venv_path  = mac_home
elif os.path.exists(cen_p):
    basic_path = cen_p
    home_path  = cen_home
    venv_path  = f'{cen_home}/data_collection'
else:
    raise ValueError('can\'t define file path, please check !!!')

sys.path.insert(0, basic_path)

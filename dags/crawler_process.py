# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
target : 資料爬取自動化流程範例
action : airflow GUI

"""
import __init__
import pendulum
from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import BranchPythonOperator, PythonOperator

basic_path = __init__.basic_path
home_path  = __init__.home_path
venv_path  = __init__.venv_path
local_tz = pendulum.timezone("Asia/Taipei")         # 設定Timezone
startDate  = datetime(2021, 9, 15, tzinfo=local_tz) # 載入

# setting dag args
default_args = {
    'owner': 'rock',                     # Who Own This Workflow
    'depends_on_past': False,            # Triggle Next After Previous Task Finish
    'start_date': startDate,             # Start From Which Date
    'email': ['example@mail.com'],       # Report to Which Email
    'email_on_failure': True,            # Error Alarm sending Email Report
    'email_on_retry': False,             # Sending Email Retry times
    'retries': 1,                        # Dag Retry times
    'retry_delay': timedelta(minutes=5)  # Delay times
}

Crawl_dag = DAG(dag_id            = 'dag_name',
                description       = 'Data Crawler Process',
                default_args      = default_args,
                schedule_interval = '0 0 * * *',                    # Start at 00:00
                tags              = ['Daily','Maintain','Crawler']) # Process Tag

# create cmd 
sour_act  = f'source {venv_path}/venv/bin/activate'                               # loading python env
crawl_cmd = f'cd {venv_path}/data_collection && scrapy crawl DataSpider'          # start crawler
etl_cmd   = f'{sour_act} && python3 {home_path}/data_collection/ETL/ETL_main.py'  # start ETL

# create job
start  = DummyOperator(task_id='start', start_date=startDate, dag=Crawl_dag)
end    = DummyOperator(task_id='end', start_date=startDate, dag=Crawl_dag)
crawl  = BashOperator(task_id='FP_Spider', bash_command=crawl_cmd, dag=Crawl_dag)
etl    = BashOperator(task_id='FP_ETL', bash_command=etl_cmd, dag=Crawl_dag)

# triggle step
start >> crawl >> etl >> end

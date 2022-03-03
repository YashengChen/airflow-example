# Airflow
###### tags: `系統`
```
專案： Airflow 自動化流程管理系統
更新日期： 2021-09-23
版本： V1
作者： Ya-Sheng Chen (Rock)
```

## 序
`Airflow`是一個工作流分配管理系統，通過有向非迴圈圖的方式管理任務流程，設定任務依賴關係和時間排程，在資料工程中，常會有繁雜的資料處理，有序且多樣條件的運行，Bash 雖然可以快速撰寫並部署自動化，但當數量變多且繁雜時，維護及除錯變得複雜繁瑣且難控管，利用Airflow 可視化介面讓控管及除錯更方便。

本篇說明如何撰寫Dags 腳本，部署自動化程式。
如未安裝Airflow 可參考 [Airflow 安裝流程](https://hackmd.io/tpALjmehRJK7s9Qk64oIdw?view)

## 啟動
- 於`local install`
    - `airflow webserver -p 8080`
    - `airflow scheduler`

- 使用`docker-compose` 安裝
    - `cd docker-compose`
    - `docker compose up`

- 使用 GUI介面管理Airflow [ http://localhost:8080/](http://localhost:8080/)

## 建立腳本Dags
 DAG 有向無環圖 `(Directed Acyclic Graph) ` 是類似氣流式的有序且相依的流程圖，並表示應該如何運行，故以此為Airflow 每項任務的流程名稱。

`example`
```
from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.sensors.external_task_sensor import ExternalTaskSensor
from airflow.operators.python_operator import BranchPythonOperator, PythonOperator

# 設定 Dags預設參數
default_args = {
    'owner': 'rock',
    'depends_on_past': False,
    'start_date': startDate,
    'email': ['rock.chen@atrustek.com'],
    'email_on_failure': True, # Error send email
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

GenPros_dag = DAG(dag_id            = 'General_Process_Yearly',
                  description       = 'General Yearly Process',
                  default_args      = default_args,
                  schedule_interval = '0 0 31 12 *',        # 每月1日 00am
                  tags              = ['Year','Maintain','Stock'])


sour_act = f'source {venv_path}/venv/bin/activate'
gbe_cmd  = f'cd {basic_path} && scrapy crawl GB_Spider'
idc_cmd  = f'cd {basic_path} && scrapy crawl IDC_Spider'

start      = DummyOperator(task_id='start', start_date=startDate, dag=GenPros_dag)
end        = DummyOperator(task_id='end', start_date=startDate, dag=GenPros_dag)
gbe_crawl  = BashOperator(task_id='GB_Spider', bash_command=gbe_cmd, dag=GenPros_dag)
idc_crawl  = BashOperator(task_id='IDC_Spider', bash_command=idc_cmd, dag=GenPros_dag)

start >> [gbe_crawl, idc_crawl] >> end
```


### 預設參數
- `parameter`:
    - **`owner`**:DAG 擁有者的名稱，如上一篇說明的，通常是負責實作這個 DAG 的人員名稱
    - **`depends_on_past`**: 每一次執行的 Task 是否會依賴於上次執行的 Task，`False`，代表上次的 Task 如果執行失敗，這次的 Task 就不會繼續執行
    - **`start_date`**: Task 從哪個日期後開始可以被 Scheduler 排入排程
    - **`email`**: 如果 Task 執行失敗的話，要寄信給哪些人的 email
    - **`email_on_failure`**: 如果 Task 執行失敗的話，是否寄信
    - **`email_on_retry`**: 如果 Task 重試的話，是否寄信
    - **`retries`**: 最多重試的次數
    - **`retry_delay`**: 每次重試中間的間隔
    - **`end_date`**: Task 從哪個日期後，開始不被 Scheduler 放入排程
    - **`execution_timeout`** : Task 執行時間的上限
    - **`on_failure_callback`**: Task 執行失敗時，呼叫的 function
    - **`on_success_callback`**: Task 執行成功時，呼叫的 function
    - **`on_retry_callback`**: Task 重試時，呼叫的 function
```
default_args = {
    'owner': 'rock',
    'depends_on_past': False,
    'start_date': datetime(2021, 09, 10),
    'email': ['example@email.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    # 'end_date': datetime(2020, 2, 29),
    # 'execution_timeout': timedelta(seconds=300),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
}
```

#### Dags object 創建

- 使用With
```
with DAG(dag_id            = v['dag_id'],
         description       = v['description'],
         default_args      = default_args,
         schedule_interval = v['schedule_interval'],
         tags              = v['tags']
) as dag:
    <do some task & workflow>
```
- create variable
```
dag1 = DAG(dag_id          = v['dag_id'],
         description       = v['description'],
         default_args      = default_args,
         schedule_interval = v['schedule_interval'],
         tags              = v['tags']
)
```

#### Dags Operators

`BashOperator` - 執行bash 指令
`PythonOperator` - 執行python function
`EmailOperator` - 寄Email
`SimpleHttpOperator` - 請求http request
`MySqlOperator`, `SqliteOperator`, `PostgresOperator`, `MsSqlOperator`, `OracleOperator`, `JdbcOperator`, etc. - 執行 sql 語法
`Sensor` - 等待 certain time, file, database row, S3 key, etc…回覆
>更多請參考 [官方文件](https://airflow.apache.org/docs/apache-airflow/1.10.1/concepts.html#operators)
```
task1 = DummyOperator(task_id='skip',   start_date=startDate, dag=dag1)
task2 = BashOperator( task_id='test1', bash_command=f'echo process Start',     dag=dag1)
```



#### schedule crontab time format
[scheduler pypi doc](https://airflow.apache.org/docs/apache-airflow/1.10.1/scheduler.html)

| preset | meaning                                            | cron |
| ------ | -------------------------------------------------- | ---- |
| `None`   | 不排程時間，利用事件`externally triggered`觸發執行 | -    |
|`@once`	| 排程一次，僅執行一次|-|	 
|`@hourly`	|每小時執行|	`0 * * * *`|
|`@daily`	|每日 `00:00` 執行	|`0 0 * * *`|
|`@weekly`	|每週日 `00:00` 執行|`0 0 * * 0`
|`@monthly`	|每月1號 `00:00`執行|`0 0 1 * *`|
|`@yearly`|	每年1/1號 `00:00`執行|`0 0 1 1 *`|

>note: Use:`schedule_interval=None`，Not use`schedule_interval='None'`

使用 [cron monitor](https://crontab.guru/) 產生相關`cron` 時間語法。

##### 父子Dag 相依性

等待 dags 完成後執行，使用ExternalTaskSensor
`from airflow.operators.sensors import ExternalTaskSensor`
[referance](https://stackoverflow.com/questions/61514887/how-to-trigger-a-dag-on-the-success-of-a-another-dag-in-airflow-using-python)
```
wait_for_dinner = ExternalTaskSensor(
    task_id='wait_for_dinner',
    external_dag_id='Parent_dag',
    external_task_id='cook_dinner',
    start_date=datetime(2020, 4, 29),
    execution_delta=timedelta(hours=1),
    timeout=3600,
)
```
#### 關閉不在GUI介面顯示 example
編輯 `airflow.cfg` 檔案
```
load_examples = False
```

#### 設定信箱回報
編輯 `airflow.cfg` 檔案
```
[smtp]
smtp_host = smtp.gmail.com
smtp_starttls = True
smtp_ssl = False
smtp_user = YOUR_EMAIL_ADDRESS
smtp_password = 16_DIGIT_APP_PASSWORD
smtp_port = 587
smtp_mail_from = YOUR_EMAIL_ADDRESS
```

> how to gmail application password ? 參考下方 附件1 `取得應用程式使用密碼`

## 參考資源
- [Airflow 官方文件](https://airflow.apache.org/docs/apache-airflow/stable/index.html)
- [Airflow pypi 文件](https://airflow.apache.org/docs/apache-airflow/1.10.1/index.html)
- [一段 Airflow 與資料工程的故事：談如何用 Python 追漫畫連載](https://leemeng.tw/a-story-about-airflow-and-data-engineering-using-how-to-use-python-to-catch-up-with-latest-comics-as-an-example.html)
- [資料科學家 L 的奇幻旅程 Vol.1 新人不得不問的 2 個問題](https://leemeng.tw/journey-of-data-scientist-L-part-1-two-must-ask-questions-when-on-board.html#%E5%84%80%E8%A1%A8%E6%9D%BF%E4%B8%8A%E7%9A%84-KPI-%E6%98%AF%E6%80%8E%E9%BA%BC%E7%94%A2%E7%94%9F%E7%9A%84%EF%BC%9F)
- [Airflow動手玩](https://zh-tw.coderbridge.com/series/c012cc1c8f9846359bb9b8940d4c10a8/posts/96bfcd7cfbc241b19f38248dac4b826e)

## 附件1 Google帳戶 `取得應用程式使用密碼`

| 步驟 | 圖示                     |
| ---- | ------------------------ |
| 右上角`應用程式icon`|<img src="https://i.imgur.com/Bfw2UUe.png" width="30"> |
|google 帳戶設定<img src="https://i.imgur.com/3rsgMPR.png" width="50"> | <img src="https://i.imgur.com/79U8qun.png" width="200">|
| `安全性設定`<br>>`登入google`|<img src="https://i.imgur.com/ukg9jNU.png" width="200"><img src="https://i.imgur.com/beG2qAP.png" width="300">|
| 開啟完`兩步驟驗證`後<br>>`應用程式密碼` ||
| 建立應用程式密碼`選取應用程式`<br>>`其他（自訂名稱）` |<img src="https://i.imgur.com/MA6IR9U.png" width="300"><img src="https://i.imgur.com/DJwDnxx.png" width="300">|

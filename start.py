# -*- coding: utf-8 -*-

import pandas as pd
import pymysql
import matplotlib.pyplot as plt

from fbprophet import Prophet

conn = pymysql.connect(host='edw_db', port=5002 ,user="clouderapp2", password="YWZlMTUxNGRjZTE0NmZh", database="dm_db")
sql = '''
select *
from
(
select FROM_UNIXTIME(floor(UNIX_TIMESTAMP(server_time) / 300) * 300, '%Y-%m-%d %H:%i:00') as ds, sum(value) as y from realtime_db.rt_safe_realtime_incursion 
where server_time like '2018-05-31%' and type = 'ear10_inst_node_cs' and name = '3,0,1' group by floor(UNIX_TIMESTAMP(server_time) / 300) * 300 
union
select FROM_UNIXTIME(floor((UNIX_TIMESTAMP(server_time)-86400) / 300) * 300, '%Y-%m-%d %H:%i:00') as ds, sum(value) as y from realtime_db.rt_safe_realtime_incursion 
where server_time like '2018-05-31%' and type = 'ear10_inst_node_cs' and name = '3,0,1' group by floor((UNIX_TIMESTAMP(server_time)-86400) / 300) * 300 
union
select FROM_UNIXTIME(floor((UNIX_TIMESTAMP(server_time)-2*86400) / 300) * 300, '%Y-%m-%d %H:%i:00') as ds, sum(value) as y from realtime_db.rt_safe_realtime_incursion 
where server_time like '2018-05-31%' and type = 'ear10_inst_node_cs' and name = '3,0,1' group by floor((UNIX_TIMESTAMP(server_time)-2*86400) / 300) * 300 
) a
order by ds asc
'''

sql = "select FROM_UNIXTIME(floor(UNIX_TIMESTAMP(server_time) / 300) * 300, '%Y-%m-%d %H:%i:00') as ds, sum(value) as y from realtime_db.rt_safe_realtime_incursion where type = 'ear10_inst_node_cs' and name = '3,0,1' group by floor(UNIX_TIMESTAMP(server_time) / 300) * 300 order by floor(UNIX_TIMESTAMP(server_time) / 300) * 300 asc"

df = pd.read_sql(sql, con=conn)

conn.close()

m = Prophet(changepoint_prior_scale=0.5)
m.fit(df)

future = m.make_future_dataframe(freq='5min', periods=288)

forecast = m.predict(future)
print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(10))

fig1 = m.plot(forecast)
fig2 = m.plot_components(forecast)

plt.show()

# 简介
小鲸卡两种后台查询格式化输出
# 文件说明
xiaojing_901.py 与 xiaojing_902.py 对应小鲸卡两个后台，两个后台的卡号不能互相查询。需在里面填入小鲸卡卡号。对应关系如下：
- 公众号：小鲸驿站IOT -> xiaojing_902.py
- 公众号：小鲸智慧IOT -> xiaojing_901.py

sct_server_send.py 为 Server 酱 Turbo 发送代码，需自行准备 sendkey 并填入
run_xiaojing.sh 为一键执行脚本，需要修改里面的文件夹路径和命令。此文件可配合 crontab 等实现定时执行查询
# 环境部署说明
需要 Python3 环境，并安装 requests 库

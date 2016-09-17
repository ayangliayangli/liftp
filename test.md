# 用户信息

        yangli 123456 配置文件路径 config/liftp.conf
        dujuan 123456 配置文件路径 config/liftp.conf
        
# config/liftp.conf

        [yangli]
        home = /data/yangli.d/
        chroot = True
        quota = 600M
<br>

        [dujuan]
        home = /data/dujuan.d/
        chroot = False
        quota = 10M
     
# 测试建议

* 没有做新建用户的接口,直接使用内置的用户吧
* 为了测试磁盘配额,建议修改一下配置文件钟的quota


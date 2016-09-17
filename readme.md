# 概要

# 基本功能

* 用户登录
* 上传文件
* 切换目录
* 显示目录下面的内容
* 下载文件
* 新建目录
* 删除目录
* 如果客户端意外关闭,支持断电续传,从百分比可以看出来

# 技术亮点

* socketserver socket
* 优化命令**没有输出**的情况
* 优化命令**输出太多**的情况
* 优化**命令执行出错**的情况
* 考虑到上传大文件出现**粘包**的情况
* 文件上传完毕后使用sha256进行**完整性校验**
* 使用 **映射** 来处理命令 hasattr getattr
* 利用**客户端障眼技术**,实现切换目录的假象 -- subprocess 每次调用都是开一个新的terminal
* 用户的密码经过sha256加密算法保存, 使用pickle保存
* 上传、下载文件 动态显示进度条 -- 百分比
* mkdir rm ll 等命令逻辑基本相同, 直接使用一个basic_server_execute 方法执行相应的命令
* 配置文件中,chroot为True的用户才可以切换到家目录以外的目录,示例钟 yangli这个用户又这个权限,dujuan没有权限



# 修复优化

* 新增 ls功能
* 修复 ls为结果空的时候报错 -- my_subprocess 返回了str, 要返回bytes才能直接发送
* 修复 ls的时候
* 新增 ll 修复ll 返回值过长引起的粘包问题
* 新增 cd 功能
* 修复 cd 根据配置文件来看是否可以查看其他目录
* 修复 cd 如果想要cd到的目录不存在,返回提示结果
* 优化 客户端显示效果 user@server pwd>>:
* 新增 mkdir
* 新增 rm 使用的时候不要加 -rf 参数,代码会默认加上
* 修复 ls 报错问题, 是服务器端给客户端回传size的时候类型转换问题
* 新增 put get
* 新增 磁盘配额 - 20160915
* 修复put 的时候一定需要3个参数,如果不写第三个参数,就默认加到把文件put到服务器的当前目录
* 修复 put 当没有第三个参数的时候,默认把文件放到当前工作目录
* 新增断电续传

# BUG

* windows系统待验证

# TODU


# 环境要求

* python3

# 作者信息

        yangli
        yangliw3@foxmail.com
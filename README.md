# elog_web

> 💡 每次同步文章都要手动执行同步命令，而且我的elog搭建在公网服务器，因此每次都要先连接到服务器终端，再输入命令，显得有些繁琐。因此我写了一个可以Web页面，让你可以在浏览器中随时随地进行文章的同步。

## 1. 配置

共有三个文件，`app.py`，`config.ini`，`requirements.txt` ，需要在`config.ini` 中配置相关的信息：

    [ssh]
    host = yourip                # 你安装elog的服务器ip
    username = yourname          # 你安装elog的服务器用户名
    password = yourpassword      # 你安装elog的服务器密码
    
    [Paths]                      # elog文件夹目录的绝对路径
    elog_path = /root/Custom_Script/Notion-Halo/elog
    
    [flask]
    host = 0.0.0.0               # 默认0.0.0.0，如果你只想让特定机器或者ip访问，改为自定义ip即可
    port = 5000                  # 服务运行端口


## 2. 部署与运行

> 💡 我的服务器用的是1panel，我以1panel进行演示，其他面板自行类比，或者自己安装python环境手动运行。

1.  **在服务器的可访问位置创建一个文件夹，将三个文件放进去。**
2.  **在1Panel应用商店安装Python运行环境。**

![image.png](https://zb666-1300332882.cos.ap-beijing.myqcloud.com/blog/1186e618149cc06ab12583d2b37f.png)

3. **创建运行脚本**

> 📢 在**网站-运行环境**中，选择**Python**，然后`创建运行环境` ，按照下图所示进行编辑。其中运行目录为`app.py`文件所在的目录，应用端口为`config.ini` 文件中设置的端口，外部映射端口为你在浏览器想访问的端口。

![image.png](https://zb666-1300332882.cos.ap-beijing.myqcloud.com/blog/00fc5dc0175d6b35bd4645b4b129.png)

4. **启动**

![image.png](https://zb666-1300332882.cos.ap-beijing.myqcloud.com/blog/8269de4ccdc6d8ebc94b317808ff.png)

5. **访问Web页面**

> 📢 使用`IP:Port` 访问Web页面，并检查相应的功能是否可用。

![%E5%B1%8F%E5%B9%95%E6%88%AA%E5%9B%BE_2025-05-08_025710.png](https://zb666-1300332882.cos.ap-beijing.myqcloud.com/blog/2b1efc985f62d863dd72c21e0380.png)

![%E5%B1%8F%E5%B9%95%E6%88%AA%E5%9B%BE_2025-05-08_025902.png](https://zb666-1300332882.cos.ap-beijing.myqcloud.com/blog/1121936402827376393d98d9426c.png)

![%E5%B1%8F%E5%B9%95%E6%88%AA%E5%9B%BE_2025-05-08_025726.png](https://zb666-1300332882.cos.ap-beijing.myqcloud.com/blog/756ad1960b6a66c3a2000c8ed255.png)

恭喜你，成功使用Web端完成了文章发布 🥰。
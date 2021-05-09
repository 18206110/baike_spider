
# baike_redis

## 介绍
>基于scrapy框架和redis实现了一个爬取百度百科上相关信息的爬虫
>以[科学百科信息科学分类](https://baike.baidu.com/wikitag/taglist?tagId=76607)网站为入口，以selenium的ChromeDirver驱动动态爬取单位百科上的科学类信息。
### 环境
>python 3.7.3
>redis  3.2.100
>selenium 3.141.0
>scrapy 2.0

### 使用说明
>服务端：
>1、启动数据库，管理员模式运行cmd，切换到redis的根目录，输入redis-server 
>2、操作数据库，打开另一个cmd窗口，输入redis-cli
>客户端：
>1、连接服务器数据库，管理员模式运行cmd，输入redis-cli -h 主机ip地址
>2、启动爬虫：pycharm中命令行输入scrapy crawl baike_spider
>注：需要配置redis的环境变量

>关于代理IP 项目中使用了[快代理](https://www.kuaidaili.com) 请自行购买


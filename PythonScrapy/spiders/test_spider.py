import scrapy
import selenium
from selenium import webdriver
import time


class TestSpiderSpider(scrapy.Spider):
    name = 'test_spider'
    allowed_domains = ['baike.baidu.com']
    start_urls = ['https://baike.baidu.com/wikitag/taglist?tagId=76607']
    # https://baike.baidu.com/wikitag/taglist?tagId=76607

    def parse(self, response):

        browser = selenium.webdriver.Chrome()

        url = 'https://baike.baidu.com/wikitag/taglist?tagId=76607'

        browser.get(url)
        browser.implicitly_wait(5)  # 在等待页面加载规定的时间结束之后允许再等待10s

        # 获取页面初始高度
        js = "return action=document.body.scrollHeight"
        height = browser.execute_script(js)

        # 将滚动条调整至页面底部
        browser.execute_script('window.scrollTo(0, document.body.scrollHeight)')
        time.sleep(5)

        # 定义初始时间戳（秒）
        t1 = int(time.time())

        # 定义循环标识，用于终止while循环
        status = True

        # 重试次数
        num = 0

        while status:
            # 获取当前时间戳（秒）
            t2 = int(time.time())
            # 判断时间初始时间戳和当前时间戳相差是否大于30秒，小于30秒则下拉滚动条
            if t2 - t1 < 30:
                new_height = browser.execute_script(js)
                if new_height > height:
                    time.sleep(1)
                    browser.execute_script('window.scrollTo(0, document.body.scrollHeight)')
                    # 重置初始页面高度
                    height = new_height
                    # 重置初始时间戳，重新计时
                    t1 = int(time.time())
            elif num < 3:  # 当超过30秒页面高度仍然没有更新时，进入重试逻辑，重试3次，每次等待30秒
                time.sleep(3)
                num = num + 1
            else:  # 超时并超过重试次数，程序结束跳出循环，并认为页面已经加载完毕！
                # print("滚动条已经处于页面最下方！")
                status = False
                # 滚动条调整至页面顶部
                browser.execute_script('window.scrollTo(0, 0)')
                break

        # 注意find_elements_by_xpath的使用，框选元素很多时使用elements，单个元素使用element

        info_urls = browser.find_elements_by_xpath("//div[@class='waterFall_item ']/a")
        count = 0
        for info_url in info_urls:
            print(info_url.get_attribute('href'))
            count += 1
        print(count)

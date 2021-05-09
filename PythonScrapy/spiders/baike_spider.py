import scrapy
import re
import selenium
from selenium import webdriver
import time


class BaikeSpiderSpider(scrapy.Spider):
    name = 'baike_spider'
    allowed_domains = ['baike.baidu.com']
    start_urls = ['https://baike.baidu.com/item/%E8%AE%A1%E7%AE%97%E6%9C%BA']

    # https://baike.baidu.com/wikitag/taglist?tagId=76607
    # https://baike.baidu.com/item/%E8%AE%A1%E7%AE%97%E6%9C%BA  计算机
    # https://baike.baidu.com/item/%E8%BD%AF%E4%BB%B6%E5%B7%A5%E7%A8%8B/25279   软件工程

    def parse(self, response):
        browser = selenium.webdriver.Chrome()

        start_url = 'https://baike.baidu.com/wikitag/taglist?tagId=76607'

        browser.get(start_url)
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
        # count = 0
        # 将获取的网址返回给本身spider，继续后续的信息提取
        for info_url in info_urls:
            url = info_url.get_attribute('href')
            yield scrapy.Request(url=url, callback=self.info_process)
            # 给予一定的时间存储数据，防止数据存储出现混乱
            time.sleep(3)
            # count += 1
        # print(count)

    def info_process(self, response):

        item = {}
        # 获取网页中所需内容的整体内容范围
        body = response.xpath("//div[@class='main-content']")

        # 提取标题
        title_first = body.xpath(".//dd[@class='lemmaWgt-lemmaTitle-title']//h1/text()").extract_first()
        title_second = body.xpath(".//dd[@class='lemmaWgt-lemmaTitle-title']//h2/text()").extract_first()
        if title_second is None:
            title = title_first
        else:
            title = title_first + title_second
        item['title'] = title

        # 提取开篇介绍
        induction_list = body.xpath(".//div[@class='lemma-summary']//div")
        induction = ""
        for induce in induction_list:
            induction = induction + induce.xpath("string(.)").extract_first()
        induction = re.sub(r"\s|\t|\n", "", induction)
        item['induction'] = induction

        # 提取目录然后根据目录提取相关内容
        # //div[@class='main-content']//div[@class='lemma-catalog']//ol/li[@class='level1']//span[@class='text']/a
        catalog_list = body.xpath(".//div[@class='lemma-catalog']//ol/li[@class='level1']")
        # 标题序列号
        catalog_serial = 1
        for catalog in catalog_list:
            catalog_info = catalog.xpath(".//span[@class='text']/a/text()").extract_first()
            item['catalog_' + str(catalog_serial)] = catalog_info
            catalog_serial += 1

        # 提取目录标题对应的内容
        '''
            //div[@class='para-title level-2'][1]/following-sibling::node()[position()<
            count(//div[@class='para-title level-2'][1]/following-sibling::node())-
            count(//div[@class='para-title level-2'][2]/following sibling::node())]
        '''

        '''
            //div[@class='para-title level-2'][7]/following-sibling::node()[position()<count(//div[@class='para-title 
            level-2'][7]/following-sibling::node())-count(//div[@class='album-list']/following-sibling::node())]
        '''

        # 提取目录所属所有内容
        count = 1
        while count < catalog_serial - 1:
            address = "//div[@class='para-title level-2'][{}]/following-sibling::node()[position()<count(//div[" \
                      "@class='para-title level-2'][{}]/following-sibling::node())-count(//div[@class='para-title " \
                      "level-2'][{}]/following-sibling::node())]".format(count, count, count + 1)

            # print(address)
            information_list = response.xpath(address)
            information_part = ''
            # 一个标题下的所有内容
            for information in information_list:
                mid_info_part = information.xpath("string(.)").extract_first()
                # print(mid_info_part)
                # 内容细节处理-去掉多于字符
                mid_info_part = re.sub(r"\n", "", str(mid_info_part))
                mid_info_part = mid_info_part.replace('None', '')
                # mid_info_part
                information_part = information_part + str(mid_info_part)

            item["catalog_info_" + str(count)] = information_part
            # print(information_part)
            # print('----------------------' + str(count) + '-------------------')
            count += 1

        # print(count)

        # 去最后一部分内容
        address = "//div[@class='para-title level-2'][{}]/following-sibling::node()[position()<count(//div[" \
                  "@class='para-title level-2'][{}]/following-sibling::node())-count(//div[" \
                  "@class='album-list']/following-sibling::node())]".format(count, count)
        # print(address)
        information_last_part = ''
        information_last = response.xpath(address)
        for info in information_last:
            information_last_part += str(info.xpath("string(.)").extract_first())
            information_last_part = re.sub(r"\n", "", information_last_part)
            information_last_part = information_last_part.replace('None', '')
        item["catalog_info_" + str(count)] = information_last_part

        # print(title)
        # print(induction)
        # print(item)
        yield item

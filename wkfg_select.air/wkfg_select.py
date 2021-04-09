# -*- encoding=utf8 -*-
__author__ = "wwz"

from airtest.core.api import *

# 自动配置运行环境的接口，可以配置当前脚本所在路径、使用的设备、log内容的保存路径、项目根目录和截图压缩精度
# 图中的  auto_setup  接口表示，当前脚本所在路径为变量  __file__  ，
# 并且尝试连接第一台安卓设备。（不填入设备参数的情况下，都是尝试连接第一台安卓设备）。
auto_setup(__file__)

# 初始化poco实例
# 无可奉告论坛是安卓原生App，所以使用AndroidUiautomationPoco方法
from poco.drivers.android.uiautomation import AndroidUiautomationPoco
poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)


def CardView_spider(f):
    '''
    爬取回复楼层信息
    '''

    # 定义1个空list用于存放楼层信息，作为card的唯一标识
    floors = []
    # 定义list目前的长度和最终的长度，用以判断是否爬完
    current_count, last_count = len(floors), len(floors)

    while True:
        last_count = len(floors)

        # 遍历当前屏幕上的所有CardView控件
        for content in poco("org.wkfg.anonymous:id/recycle").child("androidx.cardview.widget.CardView"):
            czxx_list = []   # 此临时队列存放TextView内的信息

            # 爬取每层的层数和身份信息
            if content.offspring('android.widget.TextView').exists():
                
                # 将所有可见的text入队
                # 可能会出现加载不全的情况
                for czxx in content.offspring('android.widget.TextView'):
                    if not czxx.exists():
                        continue
                    floor = czxx.get_text()
                    czxx_list.append(floor)

                # 若加载不全（标志是没有爬到楼层信息），清除当前队列
                if czxx_list[0][0] != '#':
                    czxx_list.clear()
                else:
                    # 点赞信息总是和楼层信息出现在同一行，可以安全地放在else里
                    # 但为了防止意外，还是写了存在性判断
                    if content.offspring('org.wkfg.anonymous:id/like_button').exists():
                        cz_good = content.offspring('org.wkfg.anonymous:id/like_button').get_text()
                        czxx_list.append('\n'+'赞'+cz_good)

            
            # 爬取每层的文本
            c = content.offspring('org.wkfg.anonymous:id/content')
            if not c.exists():
                czxx_list.clear() # 保证了楼层信息的完整性
                continue
            cont = c.get_text()

            # 先判断此文本是否未对应上楼层
            if czxx_list:
                # 若是则将楼层信息（如#1）入floors[]
                if not czxx_list[0] in floors:
                    floors.append(czxx_list[0])  

                    # 写入层内所有信息
                    f.write('-------------------------\n')
                    for cz_xx in czxx_list:
                        f.write(cz_xx + ' ')
                    f.write('\n')
                    f.write(cont+'\n')
                
            # 离开CardView之前，清空czxx_list
            czxx_list.clear()

        # 更新当前楼层    
        current_count = len(floors)

        # 下拉屏幕，持续时间设为2秒防止无法识别
        poco.swipe([0.5,0.7],[0.5,0.1],duration=2)
        sleep(0.8)
        
        # 当俩者数值相等，即current_count不再增加时，表明爬取完毕       
        if current_count == last_count:
            f.write('总共爬了' + str(last_count) + '楼'+'\n')
            f.write('-------------------------\n')
            f.write('-------------------------\n')
            break

    # 离开一个帖子时，清空floors
    floors.clear()



def wkfg_spider(id_list):
    '''
    这个range循环的起始和终止均指帖子的ID
    当然，也可以写一个list，爬取感兴趣的指定帖子
    '''

    f = open('wkfg.txt', 'a', encoding='utf-8') # 使用utf-8编码以打印表情

    for index in id_list:
        dong_id = str(index)

        # 搜索和点进帖子
        
        text("#"+dong_id)
        touch((400,500)) # 绝对坐标，适用于分辨率为1080p(1080×1920)的手机
        sleep(0.5)

        # 打印洞主信息
        f.write('编号：#'+dong_id.zfill(6)+'\n')

        # 判断是否为已封禁帖子
        if not poco("org.wkfg.anonymous:id/title").exists():
            f.write('此帖子已被封禁或屏蔽\n')
            f.write('-------------------------\n')
            f.write('-------------------------\n')
            poco("org.wkfg.anonymous:id/search_close_btn").click()
            sleep(0.3)
            continue


        # 否则开始正常爬取
        # 标题
        title = poco("org.wkfg.anonymous:id/title").get_text()
        f.write("主题："+title+'\n')

        # 洞主的姓名和发帖日期
        dz_name = poco('org.wkfg.anonymous:id/caption').child('org.wkfg.anonymous:id/id').get_text()
        dz_date = poco('org.wkfg.anonymous:id/caption').child('org.wkfg.anonymous:id/update').get_text()
        f.write(dz_name+'·'+dz_date+'\n')

        # 内容和点赞回复浏览信息
        # 因为在第一个CardView里，需要单独处理
        dz_content = poco("androidx.cardview.widget.CardView")[0].offspring('org.wkfg.anonymous:id/content').get_text()
        f.write(dz_content+'\n')

        # 有可能出现第一页看不到点赞的情况
        if not poco("androidx.cardview.widget.CardView")[0].offspring('org.wkfg.anonymous:id/like_button').exists():
            poco.swipe([0.5,0.7],[0.5,0.1],duration=2)
            sleep(0.8)

        dz_good = poco("androidx.cardview.widget.CardView")[0].offspring('org.wkfg.anonymous:id/like_button').get_text()
        dz_reply = poco("androidx.cardview.widget.CardView")[0].offspring('org.wkfg.anonymous:id/reply_button').get_text()
        dz_look = poco("androidx.cardview.widget.CardView")[0].offspring('org.wkfg.anonymous:id/read_button').get_text()                       
        f.write('赞'+dz_good+'  评论'+dz_reply+'  浏览'+dz_look+'\n')
        f.write('-------------------------'+'\n')

        # 核心：爬取回复楼层内信息
        CardView_spider(f)

        # 转移到下一个帖子
        poco("转到上一层级").click()
        sleep(0.5)
        poco("org.wkfg.anonymous:id/search_close_btn").click()
        sleep(0.3)

    # 程序执行完毕，关闭记事本
    f.close()


def main():
    # 启动App
    poco('无可奉告').click()
    sleep(1)

    # 以搜索-进入帖子-读取card的流程爬取信息
    poco('org.wkfg.anonymous:id/app_bar_search').click()

    # 在列表中输入想爬取的帖子的ID
    id_list = [158, 19327]
    wkfg_spider(id_list)


if __name__ == '__main__':
    main()
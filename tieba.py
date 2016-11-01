import re,requests,sys
from bs4 import BeautifulSoup


class Replace:
    def __init__(self):
        self.biaoqing=["微笑","哈哈","吐舌","啊","酷",
                "怒","开心","汗","泪","黑线",
                "鄙视","不高兴","真棒","钱","疑问",
                "阴险","吐","咦","委屈","花心",
                "呼~","笑眼","冷","太开心","滑稽",
                "勉强","狂汗","乖","睡觉","惊哭",
                "生气","惊吓","喷"]
        self.saveEmoji=re.compile(r'<img[^<]+?(/client/image_emoticon|/images/face/i_f)(\d+?)\..*?>')
        self.removeImg=re.compile(r'<img.+?src="(.+?)".*?>')  #保留图片
        # 各种pythonhtml解析器对br标签解释不同，有时会将<br />解析成<br></br> 
        self.removeBr=re.compile(r'<br>|</br>|<br/>')        
        self.removeLink=re.compile(r'<a.+?href="(.+?)".+?>(.+?)</a>') #保留链接
        self.removeTag=re.compile(r'<(/)?.+?>')             #去除杂标签
        self.removeNewline=re.compile(r'\n( *\n)+')          #去除多余的空行
        #处理md格式中有特殊意义的段落开头前四个以上空格
        self.removeHeadBlankSpace=re.compile(r' {4,}')      


        self.chara={"&amp":"&"}
        self.rule=['#','~']     #处理一些在md文件中有着特殊含义的字符
                                     #  #是标题, ~ 是下标, ★ 删除线 


    def replace(self,raw_text,saveImgLink=1,Link=1):
        text=raw_text

        for nu in self.saveEmoji.finditer(text):
            n=int(nu.group(2))
            if(n<=33):
                text=self.saveEmoji.sub("["+eval("self.biaoqing["+str(n-1)+"]")+"]",text,count=1)

        if saveImgLink==1:
            text=self.removeImg.sub(r"\n![](\1)",text)
        else:
            text=self.removeImg.sub("",text)

        text=self.removeBr.sub(r'\n',text)

        if Link==1:
            text=self.removeLink.sub(r'[\2](\2)',text)
        else:
            text=self.removeLink.sub(r'\2',text)
        text=self.removeTag.sub("",text)
        text=self.removeNewline.sub(r'\n',text)
        text=self.removeHeadBlankSpace.sub('',text)
        text=re.sub(r'&amp;','&',text)
        for symbol in self.rule:
            text=re.sub("("+symbol+"+?)",r'\\\1',text)
        return text.strip()


class Color:
    def __init__(self):
        # ansi escape color 31 red, 32 green, 33 yellow, 0 reset/normal 
        self.red=31
        self.green=32
        self.yellow=33
        self.normal=0

    def printcolor(self,text,color=0,endchar="\n"):
        # ansi escape color 31 red, 32 green, 33 yellow, 0 reset/normal
        print("\033["+str(color)+"m"+text+"\033[0m",end=endchar)

class Info:
    def __init__(self):
        self.user_name=self.pid=self.post_nu=self.content=self.islouzhu=""

class TieBa:
    def __init__(self, url_num,see_lz,current_pagenum=1):
        if(see_lz):
            self.see_lz=1
        else:
            self.see_lz=0
        self.base_url="http://tieba.baidu.com/p/"+str(url_num)+"?see_lz="+str(self.see_lz)
        self.dlImg=0            #是否下载图片
        self.saveImgLink=1      #是否保留图片链接
        self.trynum=1
        self.current_pagenum=current_pagenum
        self.pagediscard=0
        self.total_page=0
        self.title="tieba.md"
        self.color=Color()
        self.replace=Replace()
        self.tid=str(url_num)      #每层楼对话内获取容链接的tid参数
        self.curr_page_err=0

    def get_pageinfo(self):
        firstpage=self.get_html(1)
        num=re.search(r'<a href=".+?pn=(\d+?)">尾页</a>',firstpage)
        title=re.search(r'<title>(.+?)</title>',firstpage)
        if(title!=None):
            self.title=title.group(1)
            self.color.printcolor("文件名为"+self.title,self.color.green)
        else:
            self.color.printcolor("获取网页标题失败，将使用默认的tieba.md为文件名",
                    self.color.red)
        if(num!=None):
            self.total_page=int(num.group(1))
            self.color.printcolor("***** 帖子共"+str(self.total_page)+"页 *****",
                    self.color.green)
        else:
            self.color.printcolor("获取帖子页数失败",self.color.red)
            sys.exit()

    def get_postlist(self,html):
        soup=BeautifulSoup(html,"lxml")
        post_list=soup.find_all(class_="l_post")
        return post_list
        

    def get_html(self,pagenum):
        try:
            page_handle=requests.get(self.base_url+"&pn="+str(pagenum),timeout=10)
        except:
            self.retry_gethtml()
        try:
            if(self.pagediscard!=1):
                if(page_handle.status_code==requests.codes.ok):
                    return page_handle.text
                else:
                    self.retry_gethtml()
            else:
                return ""
        #  不知为什么 有时会弹出 page_handle  在赋值前被引用了的错误
        except NameError:
            self.retry_gethtml()

    def retry_gethtml(self):
        self.color.printcolor("第"+str(self.current_pagenum)+"页连接超时第一次",
                self.color.red)
        if(self.trynum<=3):
            self.color.printcolor("正在重新连接第"+str(self.trynum)+"次",self.color.red)
            self.trynum+=1
            self.get_html(self.current_pagenum)
        else:
            choice=input("\033[31m已经尝试连接3次，是否还要尝试连接(Y/N)：\033[0m")
            if(choice in ["Y","y"]):
                self.color.printcolor("正在重新连接",self.color.red)
                self.trynum=1
                self.get_html(self.current_pagenum)
            else:
                self.color.printcolor("已放弃获取第"+str(self.current_pagenum)+"页",
                        self.color.red)
                self.pagediscard=1


    def getComment(self,pid):
        url="http://tieba.baidu.com/p/comment?tid="+self.tid+"&pid="+pid
        html=requests.get(url+"&pn=1").text
        soup=BeautifulSoup(html,"lxml")
        pageInfo=soup.find(class_="lzl_li_pager")['data-field']  
                #data-field值格式为{'total_num':36,'total_page':4}
        start=pageInfo.find("\"total_page\":")+13
        end=pageInfo.find("}")
        total_page=int(pageInfo[start:end])
        comment=""
        page=1
        re_findDate=re.compile(r"\d{4}-\d{1,2}")
        removeOther=re.compile(r"(\d)回复")
        while(page<=total_page):
            html=requests.get(url+"&pn="+str(page)).text
            soup=BeautifulSoup(html,"lxml")
            commentList=soup.find_all("li",class_="lzl_single_post")
            for content in commentList:
                raw_content=self.replace.replace(str(content),0,0)
                date=re_findDate.search(raw_content)
                if not date:
                   self.color.printcolor('''评论中有非法字符如 < >等,\n
                        在html中有特殊含义的字符,会导致html解析出错\n已跳过获取此评论''',self.color.red)
                                                #在html中有特殊含义的字符，会导致html解析出错。
                                                #如  加油。" target="_blank">http://t.cn/zTKa2DH  会在
                                                #贴吧中出现导致解析有问题
                else:
                    start=date.start()   # start()方法返回的是匹配的字符串出现的位置
                    raw_content=removeOther.sub(r'\1',raw_content)
                    pure_content="—"*10+"\n"+raw_content[:start]+"\n"+raw_content[start:] 
                    #添加两个换行是因为md对一个换行忽略 两个换行在md中才显示换行的效果
                    comment=comment+pure_content+"\n"
            page=page+1
        if comment:
            comment=comment+"—"*10+"\n"
        return comment


    #获取楼层主的姓名，pid，第几楼，发帖时间和内容
    #  帖子格式 有两种 一种可直接获得楼层数和发帖时间  另一种是动态加载的 需要在data-field字段中获取
    def getPostInfo(self,post):
        info=Info()
        data=post["data-field"]

        re_nu=re.compile(r'(?<="post_no":)\d+?')
        re_date=re.compile(r'(?<="date":)"(\d| |-|:)+"')

        islouzhu=post.find(class_="louzhubiaoshi_wrap")
        if(islouzhu):
            info.islouzhu=1
        else:
            info.islouzhu=0

        has_info=post.find(class_="post-tail-wrap")
        if(has_info):
            tail_info=has_info.find_all(class_="tail-info")
            # 有可能匹配到 举报  android客户端 之类的字眼 
            # 最后两个才是 楼层数和发帖时间
            length=len(tail_info)
            info.post_nu=tail_info[length-2].get_text()
            info.date=tail_info[length-1].get_text()
        else:
            info.post_nu=re_nu.search(data).group(0)+"楼"
            info.date=re_date.search(data).group(0)[1:-1]

        #将unicode码转换成汉子  如"tink\u6da8" 
        try:
            info.user_name=re.search(r'(?<="user_name":)".+?"',data).group(0)[1:-1].encode("utf-8").decode("unicode_escape")
            info.pid=re.search("(?<=\"post_id\":)\\d+",data).group(0)
            info.content=post.find(class_="d_post_content")
            return info
        except:
            self.curr_page_err=1
            return info

    def GetTiezi(self):
        self.color.printcolor("*****  正在获取"+self.base_url+"  *****",
                self.color.yellow)
        self.get_pageinfo()
        f=open(self.title+".md",mode="w+",encoding="utf-8")
        f.write(self.title+"\n"+self.base_url[:self.base_url.find("?")]+"\n\n")
        f.write("= "*10+"\n\n")
        if(self.total_page!=0):
            while(self.current_pagenum<=self.total_page):
                self.curr_page_err=0  #初始化
                html=self.get_html(self.current_pagenum)
                post_list=self.get_postlist(html)
                ceng=1
                total_ceng=len(post_list)
                page_content=""
                for post in post_list:
                    #user_name,pid,post_nu,date,content
                    info=self.getPostInfo(post)  # 有时会获取user_name 失败 可能值为null
                    if(self.curr_page_err):    #当出错时 就设置curr_page_err 为1 
                        break
                    text=self.replace.replace(str(info.content))
                    comment=self.getComment(info.pid)
                    if(len(comment)==0):
                        nu=0
                    else:
                        nu=4
                    if(info.islouzhu):
                        info.user_name+="(楼主)"
                    page_content=page_content+info.user_name+":\n\n"+text+"\n\n"+"——"+info.post_nu+"  "+info.date+"\n"*nu+comment
                    page_content=page_content+"\n\n"+"= "*10+"\n\n"
                    self.color.printcolor("*****  正在获取第"+str(self.current_pagenum)+
                        "页(共"+str(self.total_page)+"页)已完成%.2f" %(ceng/total_ceng*100)+"%  *****",
                            self.color.yellow,endchar="")
                    ceng+=1
                    self.color.printcolor("\r",endchar="")
                if(self.curr_page_err):
                    self.color.printcolor("***** 获取第"+str(self.current_pagenum)+
                            "页失败  正在重新获取*****",self.color.red)
                else:
                    f.write(page_content)
                    #self.color.printcolor("*****  获取第"+str(self.current_pagenum)+"页成功  *****",
                     #   self.color.green)
                    self.current_pagenum+=1
        f.close()


if(__name__=="__main__"):
    message=Color()
    if(len(sys.argv)!=2):
        message.printcolor("require argument",message.red)
    else:
        tiezi=TieBa(sys.argv[1])
        tiezi.GetTiezi()

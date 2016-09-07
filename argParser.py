# -- coding:utf-8 --
import sys

class Option:
    def __init__(self):
        self.opt_num=0

class Parser:

    def __init__(self):
        self.option=Option()
        self.arglist=[]
        self.info="commandline usage:\n"
    #dest 表示选项的值的存储变量名

    #action值  
    #   store  表示选项必需有参数
    #   store_false store_true  表示dest参数的值设置成flase或true
    #   version 表示print version infomation and exits
    #   help 表示print a complete help message for all options and exits
    #   help 和version 应该默认就加进去的

    #type_ 表示选项值的类型 当action的值为store_false/store_true 时将
    # 忽略type_ 的值
    def add_opt(self,arg,short_arg,long_arg,action="store",arg_type="string",info="",version=""):
        if(type(short_arg)==type(long_arg)==type(arg)==type(info)==type(action)==type("")):
            if(action=="store_true"):
                exec("self.option."+arg+"=True")
            elif(action=="store_false"):
                exec("self.option."+arg+"=False")
            elif(action=="version"):
                exec("self.option."+arg+"="+str(version))
            self.arglist.append({"short":short_arg,"long":long_arg,"arg":arg,"action":action})
            self.info=self.info+"\t"+short_arg+","+long_arg+","+info+"\n"

        
    def parse_arg(self,argc,argv):
        n=0
        for opt in argv:
            hasfind=0
            for raw_opt in self.arglist:
                if(opt==raw_opt["short"] or opt==raw_opt["long"]):
                    if(raw_opt["action"]=="store"):
                        if(n+1==argc or "-" in argv[n+1]):
                            print("invalid argument,%s requires a argument" % opt)
                            sys.exit()
                        else:
                           exec("self.option."+raw_opt["arg"]+"="+str(argv[n+1]))
                           hasfind=1
                           break
                    elif(raw_opt["action"]=="help"):
                        print(self.info)
                        sys.exit()
                    elif(raw_opt["action"]=="version"):
                        exec("print(self.option."+raw_opt["arg"]+")")
                        sys.exit()
                    elif(raw_opt["action"]=="store_true"):
                       exec("self.option."+raw_opt["arg"]+"=False")
                       hasfind=1
                       break
                    elif(raw_opt["action"]=="store_false"):
                       exec("self.option."+raw_opt["arg"]+"=True")
                       hasfind=1
                       break
                        
            if(hasfind==0 and "-" in argv[n]):
                print("invalid  option: %s " % opt)
                sys.exit()

            n=n+1

        return self.option



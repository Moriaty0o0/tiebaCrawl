import argParser
import tieba
import sys

parser=argParser.Parser()

parser.add_opt("help","-h","--help",action="help",
        info="get usage of this programe")
parser.add_opt("version","-v","--version",action="version",
        info="print the version of the software",version="3.0")
parser.add_opt("post_nu","-p","--post-number",info="tieba post number")
parser.add_opt("see_lz","-L","--see-lz",action="store_false",
        info="only get lz's infomation")
parser.add_opt("filename","-o","--output",info="rename the file's name")
parser.add_opt("list_info","-l","--list-info",action="store_false",
        info="get the infomation of the tieba,for example,the total pages of tieba")
parser.add_opt("cur_page","-s","--start-page",
        info="get content from this to end")

options=parser.parse_arg(len(sys.argv)-1,sys.argv[1:])
if(hasattr(options,"cur_page")):
    tiezi=tieba.tieba(options.post_nu,options.see_lz,
            current_pagenum=options.cur_page)
else:
    tiezi=tieba.tieba(options.post_nu,options.see_lz)
if(options.list_info):
    tiezi.get_pageinfo()
else:
    tiezi.start()

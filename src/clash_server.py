import http.server
import socketserver
import requests
import yaml
import sys
import urllib.parse
import collections
from os.path import expanduser

URL=""
PORT = 9093

## 写下改写代码
def transform(y):
    y.pop("cfw-bypass", None)
    y.pop("cfw-latency-timeout" , None)

    groups = y["Proxy Group"]
    for proxy in groups:
        ## 过滤掉 glaobal 中的 pro 
        if proxy["name"] == "GlobalMedia" :
            proxy["proxies"] = [ x for x in proxy["proxies"] if not "Pro" in x ]

    # sort key
    return dict(collections.OrderedDict(sorted(y.items(), reverse=True)))

def transformClashYaml(url):
    req = requests.get(url)

    if req.status_code == 200:
        return transform(yaml.safe_load(req.text))
    else:
        return None

class Handler(http.server.BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def do_GET(self):
        params = urllib.parse.parse_qs(self.path[2:])


        if "url" in params:
            req = transformClashYaml(params["url"][0])
        else: 
            req = None

        if req is not None:
            self.send_response(200)
            self.send_header("Content-type", "text/yaml")
            self.end_headers()
            yaml.safe_dump(req, encoding="utf-8", stream=self.wfile, default_flow_style=False, sort_keys=False)
            return

        self.send_response(500)
        self.end_headers()


def Cmd():
    with open(expanduser("~/.openclashconfig"), 'r') as file:
        content = file.read()
        config = yaml.safe_load(content)
        url = config["clash_config_url"]
        req = transformClashYaml(url)
        yaml.safe_dump(req, encoding="utf-8", stream=sys.stdout, sort_keys=False)


def Serv(server="", port=9091):


    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("serving at port", PORT)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            httpd.server_close()
            pass

    httpd.server_close()

if __name__ == "__main__":
    if "run" not in sys.argv :
        Serv()
    else:
        Cmd()
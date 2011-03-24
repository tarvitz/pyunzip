# coding: utf-8
import subprocess
def get_self_ip_address():
    try:
        out = subprocess.Popen(['noip2','-S'],stderr=subprocess.PIPE).stderr.read()
        import re
        r = re.compile(r'Last IP Address set (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',re.U)
        ip = r.findall(out)
        if ip:
            return ip[0]
        else:
            return None
    except:
        return None
if __name__ in '__main__':
    ip = get_self_ip_address()
    print ip

import os
import json
import random
import datetime
import pyscreenshot as ImageGrab
from launchFirefox import FirefoxLauncher
from mozregression.log import init_logger

logger = init_logger()
env = os.environ.copy()
app_launch_path = env.get("MOZREGRESSION_BINARY")
build_date = env.get("MOZREGRESSION_BUILD_DATE")
result_fn = "result.json"

if os.path.exists(result_fn):
    try:
        with open(result_fn) as read_fh:
            output_result = json.load(result_fn)
    except:
        output_result = {}
else:
    output_result = {}

url_list = {"https://www.amazon.com/": {"label": "amazon"},
            "https://www.amazon.com/gp/goldbox/ref=nav_cs_gb": {"label": "amazon"},
            "https://www.amazon.com/stream/ref=nav_upnav_LargeImage_C_Gateway?pf_rd_m=ATVPDKIKX0DER&pf_rd_s=nav-upnav-msg1&pf_rd_r%5B%5D=56D4NFKYN5BTC49NEZAP&pf_rd_r%5B%5D=56D4NFKYN5BTC49NEZAP&pf_rd_t=4201&pf_rd_p%5B%5D=6071acbf-fe43-448d-8f47-33114e3f82d5&pf_rd_p%5B%5D=6071acbf-fe43-448d-8f47-33114e3f82d5&pf_rd_i=navbar-4201&asCursor=WyIxLjgiLCJ0czEiLCIxNTE1NjQ1NjAwMDAwIiwiIiwiUzAwMDQ6MDpudWxsIiwiUzAwMDQ6MjoxIiwiUzAwMDQ6MDotMSIsIiIsIiIsIjAiLCJzdWIyIiwiMTUxNTY0OTY2Mzg0MSIsImhmMS1zYXZlcyIsIjE1MTU2NDQxMDAwMDAiLCJ2MSIsIjE1MTU2NDk0MjIzMDkiLCJ2MSIsIjE1MDEwMTYzNDk2NTgiLCJ2MSIsIjE1MTU2NDYwMjA5ODIiXQ%3D%3D&asCacheIndex=0&asYOffset=-432": {
                "label": "amazon"},
            "https://us.yahoo.com/?p=us": {"label": "yahoo"},
            "https://www.yahoo.com/news/": {"label": "yahoo"},
            "https://www.yahoo.com/news/us/": {"label": "yahoo"},
            "https://tw.yahoo.com/?p=us": {"label": "yahoo"},
            "https://www.youtube.com/": {"label": "youtube"},
            "https://www.youtube.com/feed/trending": {"label": "youtube"},
            "https://www.youtube.com/feed/history": {"label": "youtube"}}


for _ in range(1):
    url_addr = url_list.keys()[int(random.random()*100 % 10)]
    cmd_args = [url_addr]

    firefox_launcher = FirefoxLauncher(app_launch_path)
    firefox_launcher.start(cmdargs=cmd_args)
    firefox_launcher.is_browser_window_show_up()

    # create image name and take snapshot
    current_ts = int((datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1, 0, 0, 0, 0)).total_seconds())
    image_name = "%s_%s.png" % (build_date, current_ts)
    if os.path.exists(image_name):
        os.remove(image_name)
    ImageGrab.grab((0, 0, 1024, 768)).save(image_name, "png")

    if os.path.exists(image_name):
        output_result[image_name] = {"build_date": build_date, "url": cmd_args[0], "label": url_list[url_addr]["label"]}

    with open(result_fn, "w") as write_fh:
        json.dump(output_result, write_fh)

    import time
    time.sleep(100)

    firefox_launcher.stop()

exit(0)

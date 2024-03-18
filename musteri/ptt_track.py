import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def ptt_track(ptt_code):
    url = "https://gonderitakip.ptt.gov.tr/Track/summaryResult"

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://gonderitakip.ptt.gov.tr",
        "Cookie": "PTT_=AAI7geJ-ZDuQDGQEAAAAADusx-Nlhq_drPQVOwgPDKxZ-wvAiGWsfsLDqsK2EziPOw==ceZ-ZA==3uxh-1-6xXhb5uB1RBI2ma6RppQ=",
        "Accept-Language": "tr-TR,tr;q=0.9",
        "Host": "gonderitakip.ptt.gov.tr",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15",
        "Referer": "https://gonderitakip.ptt.gov.tr/Track/Index",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    data = {
        "q": ptt_code,
        "as_sfid": "AAAAAAXuQ9h3EO7BKvu_ASH5GF9VLh8yApa2But2CNQspZYQMeco2ZDJ-EKIjfg5QAMyW1nTEFgN1tRQVl4tckLY8Vw3IA3jw7pz7BM79Ai9R4P5a1tvpSGvq497Z2VIoJeJ2e1OxnUAK3U7HuB0aAH00VBMxWICKxmpPEYqEsvfzmAP7w==",
        "as_fid": "2bb17013dca56c5e12971d9ac029dbfe14fcff49",
    }

    response = requests.post(url, headers=headers, data=data, verify=False)

    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table")  # ilk bulunan tabloyu alır
    rows = table.find_all("tr")  # tablodaki tüm satırları alır

    data = []
    for row in rows:
        cols = row.find_all("td")
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele])  # boş verileri almadan değerleri alır

    hareket = ""
    # son 5 sonucu (veya mevcut olan kadarını) alır ve yazdırır
    for row in data[-5:]:
        hareket += " ".join(row) + "\n"

    return hareket


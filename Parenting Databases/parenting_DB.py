from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
import socket
socket.getaddrinfo('localhost', 8080)

baseurl = "https://www.solusibuku.com/"
headers = {
    "user agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
}

productlinks = []

for i in range(1,4):
    r = requests.get(f"https://www.solusibuku.com/parenting?page={i}",timeout=20)
    soup = BeautifulSoup(r.content, "html.parser")
    lists = soup.find_all('div', class_= "col-xl-4 col-lg-4 col-md-6 col-sm-6 col-12")
    for item in lists:
        for link in item.find_all("a", class_ = "ps-product__title", href=True):
            productlinks.append(link["href"])
            
    print(f"product links : {len(productlinks)}")
    print(f"Page {i} done")

product = []

for i in productlinks:
    r = requests.get(i,timeout=20)
    soup = BeautifulSoup(r.content, "html.parser")

    try:
        nama = soup.find('div', class_="ps-product__info").h1.text
        nama = re.sub(r'[-()\"#/@;:<>{}`+=~|*.!?,]','', nama)
    except:
        nama="no name"
    
    sourceimg = []
    for img in soup.find_all("img"):
        if img.has_attr('src'):
            sourceimg.append(img['src'])
            
    res = requests.get(sourceimg[1], stream = True)
    open(f"{nama}.jpg", 'wb').write(res.content)
    try:
        harga = str(soup.find("h4", class_= "ps-product__price").text)
        harga = harga[:10]
    except:
        harga = ""
    try:   
        deskripsi = soup.find("div", class_="ps-document").text
    except:
        deskripsi = ""


    detail =  []
    try:
        table = soup.find("table", { "class" : "table table-bordered ps-table ps-table--specification" })
        trs = table.find_all("tr")
        for tr in trs:
            tds = tr.find_all('td')
            for td in tds:
                detail.append(td.text)       
        key = []
        key_new = []       
        key_old = detail[::2]
        for x in key_old:
            key_new.append(x.replace(":",""))
        for x in key_new:
            key.append(x.strip())
        value = detail[1::2]
        detail = dict(zip(key, value))
    except:
        detail = {}

    data = {
        "nama" : nama,
        "harga" : harga,
        "deskripsi" : deskripsi,
        "detail" : detail,
        "link gambar" : sourceimg[1],
        "link" : i
    }
    
    product.append(data)
    print(f"progress : {len(product)}")
    
df = pd.DataFrame(product)
df.to_csv("parenting_DB.csv")
import requests
from requests_html import HTMLSession
from models import POI, db
from bs4 import BeautifulSoup
import xlwt
import xlrd
import time
import datetime
from math import radians, cos, sin, asin, sqrt

# -*- coding:UTF8MB4 -*-


class RecCoordinate:
    def __init__(self, longitude0, latitude0, longitude1, latitude1):
        self.longitude0 = longitude0
        self.latitude0 = latitude0
        self.longitude1 = longitude1
        self.latitude1 = latitude1

    def tostring(self):
        return str(self.longitude0) + "," + str(self.latitude0) + "|" + str(self.longitude1) + "," + str(self.latitude1)

    def get_lon_average(self):
        return (self.longitude0 + self.longitude1) / 2

    def get_lat_average(self):
        return (self.latitude0 + self.latitude1) / 2

    def get_lon0(self):
        return self.longitude0

    def get_lon1(self):
        return self.longitude1

    def get_lat0(self):
        return self.latitude0

    def get_lat1(self):
        return self.latitude1


def get_result(rec_area, page):
    poi_type = "010000|010100|010101|010102|010103|010104|010105|010107|010108|010109|010110|010111|010112|010200|" \
               "010300|010400|010401|010500|010600|010700|010800|010900|010901|011000|011100|020000|020100|020101|" \
               "020102|020103|020104|020105|020106|020200|020201|020202|020203|020300|020301|020400|020401|020402|" \
               "020403|020404|020405|020406|020407|020408|020600|020601|020602|020700|020701|020702|020703|020800|" \
               "020900|020904|020905|021000|021001|021002|021003|021004|021100|021200|021201|021202|021203|021300|" \
               "021301|021400|021401|021500|021501|021600|021601|021602|021700|021701|021702|021800|021802|021803|" \
               "021804|021900|022000|022100|022200|022300|022301|022400|022500|022501|022502|022600|022700|022800|" \
               "022900|023000|023100|023200|023300|023301|023400|023500|025000|025100|025200|025300|025400|025500|" \
               "025600|025700|025800|025900|026000|026100|026200|026300|029900|030000|030100|030200|030201|030202|" \
               "030203|030204|030205|030206|030300|030301|030302|030303|030400|030401|030500|030501|030502|030503|" \
               "030504|030505|030506|030507|030508|030700|030701|030702|030800|030801|030802|030803|030900|031000|" \
               "031004|031005|031100|031101|031102|031103|031104|031200|031300|031301|031302|031303|031400|031401|" \
               "031500|031501|031600|031601|031700|031701|031702|031800|031801|031802|031900|031902|031903|031904|" \
               "032000|032100|032200|032300|032400|032401|032500|032600|032601|032602|032700|032800|032900|033000|" \
               "033100|033200|033300|033400|033401|033500|033600|035000|035100|035200|035300|035400|035500|035600|" \
               "035700|035800|035900|036000|036100|036200|036300|039900|040000|040100|040101|040200|040201|050000|" \
               "050100|050101|050102|050103|050104|050105|050106|050107|050108|050109|050110|050111|050112|050113|" \
               "050114|050115|050116|050117|050118|050119|050120|050121|050122|050123|050200|050201|050202|050203|" \
               "050204|050205|050206|050207|050208|050209|050210|050211|050212|050213|050214|050215|050216|050217|" \
               "050300|050301|050302|050303|050304|050305|050306|050307|050308|050309|050310|050311|050400|050500|" \
               "050501|050502|050503|050504|050600|050700|050800|050900|060000|060100|060101|060102|060103|060200|" \
               "060201|060202|060300|060301|060302|060303|060304|060305|060306|060307|060308|060400|060401|060402|" \
               "060403|060404|060405|060406|060407|060408|060409|060411|060413|060414|060415|060500|060501|060502|" \
               "060600|060601|060602|060603|060604|060605|060606|060700|060701|060702|060703|060704|060705|060706|" \
               "060800|060900|060901|060902|060903|060904|060905|060906|060907|061000|061001|061100|061101|061102|" \
               "061103|061104|061200|061201|061202|061203|061204|061205|061206|061207|061208|061209|061210|061211|" \
               "061212|061213|061214|061300|061301|061302|061400|061401|070000|070100|070200|070201|070202|070203|" \
               "070300|070301|070302|070303|070304|070305|070306|070400|070401|070500|070501|070600|070601|070603|" \
               "070604|070605|070606|070607|070608|070609|070610|070700|070701|070702|070703|070704|070705|070706|" \
               "070800|070900|071000|071100|071200|071300|071400|071500|071600|071700|071800|071801|071900|071901|" \
               "071902|071903|072000|072001|080000|080100|080101|080102|080103|080104|080105|080106|080107|080108|" \
               "080109|080110|080111|080112|080113|080114|080115|080116|080117|080118|080119|080200|080201|080202|" \
               "080300|080301|080302|080303|080304|080305|080306|080307|080308|080400|080401|080402|080500|080501|" \
               "080502|080503|080504|080505|080600|080601|080602|080603|090000|090100|090101|090102|090200|090201|" \
               "090202|090203|090204|090205|090206|090207|090208|090209|090210|090211|090300|090400|090500|090600|" \
               "090601|090602|090700|090701|090702|100000|100100|100101|100102|100103|100104|100105|100200|100201|" \
               "110000|110100|110101|110102|110103|110104|110105|110106|110200|110201|110202|110203|110204|110205|" \
               "110206|110207|110208|110209|120000|120100|120200|120201|120202|120203|120300|120301|120302|120303|" \
               "120304|130000|130100|130101|130102|130103|130104|130105|130106|130107|130200|130201|130202|130300|" \
               "130400|130401|130402|130403|130404|130405|130406|130407|130408|130409|130500|130501|130502|130503|" \
               "130504|130505|130506|130600|130601|130602|130603|130604|130605|130606|130700|130701|130702|130703|" \
               "140000|140100|140101|140102|140200|140201|140300|140400|140500|140600|140700|140800|140900|141000|" \
               "141100|141101|141102|141103|141104|141105|141200|141201|141202|141203|141204|141205|141206|141207|" \
               "141300|141400|141500|150000|150100|150101|150102|150104|150105|150106|150107|150200|150201|150202|" \
               "150203|150204|150205|150206|150207|150208|150209|150210|150300|150301|150302|150303|150304|150400|" \
               "150500|150501|150600|150700|150701|150702|150703|150800|150900|150903|150904|150905|150906|150907|" \
               "150908|150909|151000|151100|151200|151300|160000|160100|160101|160102|160103|160104|160105|160106|" \
               "160107|160108|160109|160110|160111|160112|160113|160114|160115|160117|160118|160119|160120|160121|" \
               "160122|160123|160124|160125|160126|160127|160128|160129|160130|160131|160132|160133|160134|160135|" \
               "160136|160137|160138|160139|160140|160141|160142|160143|160144|160145|160146|160147|160148|160149|" \
               "160150|160151|160152|160200|160300|160301|160302|160303|160304|160305|160306|160307|160308|160309|" \
               "160310|160311|160312|160314|160315|160316|160317|160318|160319|160320|160321|160322|160323|160324|" \
               "160325|160326|160327|160328|160329|160330|160331|160332|160333|160334|160335|160336|160337|160338|" \
               "160339|160340|160341|160342|160343|160344|160345|160346|160347|160348|160349|160400|160401|160402|" \
               "160403|160404|160405|160406|160407|160408|160500|160501|160600|170000|170100|170200|170201|170202|" \
               "170203|170204|170205|170206|170207|170208|170209|170300|170400|170401|170402|170403|170404|170405|" \
               "170406|170407|170408|180000|180100|180101|180102|180103|180104|180200|180201|180202|180203|180300|" \
               "180301|180302|180400|180500|190000|190100|190101|190102|190103|190104|190105|190106|190107|190108|" \
               "190109|190200|190201|190202|190203|190204|190205|190300|190301|190302|190303|190304|190305|190306|" \
               "190307|190308|190309|190310|190311|190400|190401|190402|190403|190500|190600|190700|200000|200100|" \
               "200200|200300|200301|200302|200303|200304|200400|220000|220100|220101|220102|220103|220104|220105|" \
               "220106|220107|220200|220201|220202|220203|220204|220205|970000|990000|991000|991001|991400|991401|" \
               "991500"
    data = {
        'polygon': rec_area.tostring(),
        'types': poi_type,
        'offset': '20',
        'page': page,
        'extensions': 'all',
        'language': 'en',
        'key': '7af3615b66b96d1e0cd54b010b9ed5e8'
    }
    url = "https://restapi.amap.com/v3/place/polygon"
    # try to parse POI information from json in target URL
    try:
        r = requests.get(url, params=data)
        s = requests.session()
        s.keep_alive = False
        result = r.json()
        return result
    except requests.exceptions.ConnectionError as e:
        r.status_code = "Connection refused"
        print('except:', e)


# when the POI number in one area is greater than 1000, this area need to be splited
def get_splitrec(rec_area):
    rec_1 = RecCoordinate(rec_area.get_lon0(), rec_area.get_lat0(),
                          rec_area.get_lon_average(), rec_area.get_lat_average())
    rec_2 = RecCoordinate(rec_area.get_lon_average(), rec_area.get_lat0(),
                          rec_area.get_lon1(), rec_area.get_lat_average())
    rec_3 = RecCoordinate(rec_area.get_lon0(), rec_area.get_lat_average(),
                          rec_area.get_lon_average(), rec_area.get_lat1())
    rec_4 = RecCoordinate(rec_area.get_lon_average(), rec_area.get_lat_average(),
                          rec_area.get_lon1(), rec_area.get_lat1())
    rec_list = [rec_1, rec_2, rec_3, rec_4]
    return rec_list


final_result = []


# recursive judge whether the POI in the area is meeting the requirements
def judge_result(rec_area):
    result = get_result(rec_area, 1)
    if 'count' in result.keys():
        count = result['count']
        if int(count) >= 1000:
            split_list = get_splitrec(rec_area)
            for rec in split_list:
                judge_result(rec)
        else:
            final_result.append(rec_area)
    return final_result


# save POI information into database
def save_result(result):
    for i in range(len(result)):
        if "'" in result[i]['name']:
            name = result[i]['name'].replace("'", "\'")
        else:
            name = result[i]['name']
        typecode = result[i]['typecode']
        if "'" in result[i]['address']:
            address = result[i]['address'].replace("'", "\'")
        elif str(result[i]['address']) == '[]':
            address = '[]'
        else:
            address = result[i]['address']
        location = result[i]['location']
        longitude = location.split(",")[0]
        latitude = location.split(",")[1]
        try:
            poi = POI()
            poi.name = name
            poi.typecode = typecode
            poi.address = address
            poi.longitude = longitude
            poi.latitude = latitude
            db.session.add(poi)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e


# read POI infor in json form pages by pages
def analyze_result(rec_area):
    page = 1
    is_last_page = False
    p_result = {}
    poi_result = []
    while is_last_page is False:
        try:
            p_result = get_result(rec_area, page)
            if 'pois' in p_result.keys():
                poi_result = p_result['pois']
        except Exception as e:
            print('except:', e)

        if str(poi_result) != '[]' and len(poi_result) < 20:
            is_last_page = True

        if str(poi_result) == '[]':
            is_last_page = True

        save_result(poi_result)
        page += 1


def get_poi_service():
    rec_area = RecCoordinate(103.8, 30.74, 104.02, 30.55)
    area = judge_result(rec_area)
    for rec in area:
        print(rec.tostring())
        analyze_result(rec)


# crawl the no.92 fuel price
def get_fuel():
    session = HTMLSession()
    url = 'http://youjia.chemcp.com/sichuan/'
    r = session.get(url)
    e = r.html.xpath("//div[@class='content']/font/text()")
    return e[1]


def geo_map(start_name, des_name):
    if "[" in start_name:
        s_name = start_name.split("[")[0]
        s_address = start_name.split("[")[1].split("]")[0]
        start_poi = db.session.query(POI).filter(POI.name == s_name, POI.address == s_address).first()
    else:
        start_poi = db.session.query(POI).filter(POI.name == start_name).first()

    if "[" in des_name:
        d_name = des_name.split("[")[0]
        d_address = des_name.split("[")[1].split("]")[0]
        des_poi = db.session.query(POI).filter(POI.name == d_name, POI.address == d_address).first()
    else:
        des_poi = db.session.query(POI).filter(POI.name == des_name).first()

    poi_list = [start_poi.longitude, start_poi.latitude, des_poi.longitude, des_poi.latitude, start_name, des_name]
    return poi_list


# get HTML for target URL
def get_page_info(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 3578.98 Safari/537.36'}
        html = requests.get(url, headers=headers)
        html.raise_for_status()
        soup = BeautifulSoup(html.content.decode('utf-8', 'ignore'), 'lxml')
        return soup
    except Exception as e:
        print(e)


# parse hotel information in Chengdu
def get_hotel_info(url):
    hotel_info = {}
    hotel_id = ['Rate', 'Name', 'Coordinate', 'Price']
    col_num = 1
    page_num = 1

    workbook = xlwt.Workbook(encoding='utf-8', style_compression=0)
    sheet = workbook.add_sheet('hotel_info', cell_overwrite_ok=True)
    # write first row，which is the name of each column
    for i in range(len(hotel_id)):
        sheet.write(0, i, hotel_id[i])

    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    new_url = url + ";checkin_year_month_monthday=" + str(today) + \
              ";checkout_year_month_monthday=" + str(tomorrow) + ";lang=en-us"

    while page_num < 17:
        soup = get_page_info(new_url)
        hotels = soup.find_all('div', class_=["sr_item", "sr_item_new", "sr_item_default", "sr_property_block",
                                              "sr_flex_layout", "sr_item_no_dates"])

        for hotel in hotels:
            if hotel.find('div', class_='bui-review-score__badge'):
                hotel_info['star'] = hotel.find('div', class_='bui-review-score__badge').get_text()
                hotel_info['name'] = hotel.find('a', class_=["hotel_name_link", "url"]).find('span').get_text()
                hotel_info['coord'] = hotel.find('a', class_="bui-link")['data-coords']
                hotel_info['price'] = hotel.find_all('div', class_=["bui-price-display__value",
                                                                "prco-inline-block-maker-helper"])[1].get_text()
                print(hotel_info['name'] + hotel_info['coord'] + hotel_info['star']
                  + hotel_info['price'])

                # write into the row of excel
                for i in range(len(hotel_info.values())):
                    sheet.write(col_num, i, list(hotel_info.values())[i])
                col_num += 1

        # By clicking the next page button, the system would continue to read next page
        if soup.find('div', class_=["bui-pagination", "results-paging"]).find('nav').find('ul').find_all('li')[-1].find('a'):
            new_url = "https://www.booking.com" + str(soup.find('div', class_=["bui-pagination", "results-paging"])
                                                      .find('nav').find('ul').find_all('li')[-1].find('a')['href'])
        time.sleep(1)
        page_num += 1

    workbook.save('hotel_info_chengdu.xls')


# function to calculate distance between two point
def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # the average radio of earth is 6371km
    dis = c * r * 1000  # transfer from km to m
    return dis


def readxlsx_int():
    poi_table = xlrd.open_workbook("poicode.xlsx")
    poi_sheet = poi_table.sheet_by_index(0)
    poi_dict = {}
    for row in poi_sheet.get_rows():
        type_row = row[1]
        poi_type = type_row.value
        category_row = row[7]
        poi_category = category_row.value
        if str(poi_category) != "Sub Category":
            poi_dict[int(poi_type)] = str(poi_category)
    return poi_dict


def readxlsx_str():
    poi_table = xlrd.open_workbook("poicode.xlsx")
    poi_sheet = poi_table.sheet_by_index(0)
    poi_dict = {}
    for row in poi_sheet.get_rows():
        type_row = row[1]
        poi_type = type_row.value
        category_row = row[7]
        poi_category = category_row.value
        if str(poi_category) != "Sub Category":
            if "." in str(poi_type):
                poi_dict[str(poi_category)] = str(poi_type).split(".")[0]
            else:
                poi_dict[str(poi_category)] = str(poi_type)

    return poi_dict


# get all sort of POI
def get_sort_list():
    poi_type = db.session.query(POI.typecode).all()
    new_poi = []
    for poi in poi_type:
        if poi not in new_poi:
            new_poi.append(poi)

    poi_dict = readxlsx_int()
    p_list = [(1, "---- Choose the type ----")]
    # p_list.append((1, "---- Choose the type ----"))
    i = 2
    for poi in new_poi:
        poi = str(poi)
        index = poi.split("'", 2)[1]

        if index == "072101":
            break
        elif index == "991601":
            break
        else:
            if '|' in poi:
                new_index = index.split("|")
                p_list.append((i, poi_dict[int(new_index[0])] + "|" + poi_dict[int(new_index[1])]))
                # p_list.append((i, poi_dict[int(new_index[0])] + "|" + poi_dict[int(new_index[1])]))
                i += 1
            else:
                p_list.append((i, poi_dict[int(index)]))
                # p_list.append((i, poi_dict[int(index)]))
                i += 1
    return p_list

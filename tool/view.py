from flask import Flask, render_template, redirect, request, url_for, jsonify
import form
from models import db, app, POI
from extensions import geo_map, get_poi_service, get_fuel, get_hotel_info, haversine, readxlsx_str
import requests
import xlrd

# -*- coding: utf-8 -*-


@app.route('/')
def hello_world():
    return redirect('/geo_map')


@app.route('/choose_name', methods=['POST'])
def choose_name():
    if request.method == "POST":
        data = request.get_json()
        typename = data["typename"]
        typelist = readxlsx_str()
        typename = str(typename)
        if '|' in typename:
            new_typename = typename.split("|")
            typecode1 = typelist.get(new_typename[0])
            typecode2 = typelist.get(new_typename[1])
            code = str(typecode1) + "|" + str(typecode2)
        else:
            code = typelist.get(typename)
        pois = POI.query.filter_by(typecode=code).all()
        namelist = [(poi.id, poi.name, poi.address) for poi in pois]
        return jsonify(namelist)


@app.route('/geo_map', methods=['GET', 'POST'])
def geo():
    # get_poi_service()
    sort_form = form.PoiSort()
    if request.method == "GET":
        return render_template('choose-sort.html', sort_form=sort_form)
    if request.method == "POST":
        data = request.get_json()
        start_name = data["start_name"]
        des_name = data["des_name"]
        poi_list = geo_map(start_name, des_name)
        return jsonify(poi_list)


@app.route('/bus_path', methods=['POST'])
def bus_path():
    if request.method == "POST":
        data = request.get_json()
        start_poi_lon = data["start_poi_lon"]
        start_poi_lat = data["start_poi_lat"]
        des_poi_lon = data["des_poi_lon"]
        des_poi_lat = data["des_poi_lat"]

        strategy = [1, 2, 4]
        b_list = []
        for s in strategy:
            data = {
                'origin': str(start_poi_lat) + "," + str(start_poi_lon),
                'destination': str(des_poi_lat) + "," + str(des_poi_lon),
                'tactics_incity': s,
                'ak': 'YBZZIRimrGrpgbnRlQABvqvC1Vw8o7WD'
            }
            url = "http://api.map.baidu.com/direction/v2/transit"
            r = requests.get(url, params=data)
            result = r.json()
            if result['result']['routes']:
                routes = result['result']['routes'][0]

                b_dict = {
                    'b_distance': routes['distance'],
                    'b_time': routes['duration'],
                    'b_cost': routes['price'],
                    'subway_cost': routes['price_detail'][0]['ticket_price'],
                    'bus_cost': routes['price_detail'][1]['ticket_price']
                }
                b_list.append(b_dict)
            else:
                b_list = []

        return jsonify(b_list)


@app.route('/drive_path', methods=['POST'])
def drive_path():
    if request.method == "POST":
        data = request.get_json()
        start_poi_lon = data["start_poi_lon"]
        start_poi_lat = data["start_poi_lat"]
        des_poi_lon = data["des_poi_lon"]
        des_poi_lat = data["des_poi_lat"]

        strategy = [2, 4, 6]
        fuel_price = get_fuel()

        d_list = []
        for s in strategy:
            data = {
                'origin': str(start_poi_lat) + "," + str(start_poi_lon),
                'destination': str(des_poi_lat) + "," + str(des_poi_lon),
                'tactics': s,
                'ak': 'YBZZIRimrGrpgbnRlQABvqvC1Vw8o7WD'
            }
            url = "http://api.map.baidu.com/direction/v2/driving"
            r = requests.get(url, params=data)
            result = r.json()
            if result['result']['routes']:
                routes = result['result']['routes'][0]
                # we assume the car consume 10 L petrol per 100 km
                cost = round(float(fuel_price) * 10 * int(routes['distance']) / 100000, 2)
                d_dict = {
                    'd_distance': routes['distance'],
                    'd_time': routes['duration'],
                    'd_cost': float(routes['toll']) + cost,
                    'd_fuel_cost': cost
                }
                d_list.append(d_dict)
            else:
                d_list = []
        return jsonify(d_list)


@app.route('/ride_path', methods=['POST'])
def ride_path():
    if request.method == "POST":
        data = request.get_json()
        start_poi_lon = data["start_poi_lon"]
        start_poi_lat = data["start_poi_lat"]
        des_poi_lon = data["des_poi_lon"]
        des_poi_lat = data["des_poi_lat"]

        r_list = []
        data = {
            'origin': str(start_poi_lat) + "," + str(start_poi_lon),
            'destination': str(des_poi_lat) + "," + str(des_poi_lon),
            'ak': 'YBZZIRimrGrpgbnRlQABvqvC1Vw8o7WD'
        }
        url = "http://api.map.baidu.com/direction/v2/riding"
        r = requests.get(url, params=data)
        r_result = r.json()
        if 'result' in r_result.keys():
            routes = r_result['result']['routes'][0]
            r_dict = {
                'r_distance': routes['distance'],
                'r_time': routes['duration'],
            }
            r_list.append(r_dict)
        else:
            r_list = []

        bus_strategy = [1, 2, 4]
        bus_sum_dis = 0
        bus_sum_time = 0
        bus_sum_cost = 0
        b_sign = 0
        for s in bus_strategy:
            data = {
                'origin': str(start_poi_lat) + "," + str(start_poi_lon),
                'destination': str(des_poi_lat) + "," + str(des_poi_lon),
                'tactics_incity': s,
                'ak': 'YBZZIRimrGrpgbnRlQABvqvC1Vw8o7WD'
            }
            url = "http://api.map.baidu.com/direction/v2/transit"
            r = requests.get(url, params=data)
            result = r.json()
            if result['result']['routes']:
                routes = result['result']['routes'][0]

                bus_sum_dis += routes['distance']
                bus_sum_time += routes['duration']
                bus_sum_cost += routes['price']
            else:
                r_list = []
                b_sign = 1
                break

        if b_sign is 0:
            bus_av_dis = round(bus_sum_dis / 3, 1)
            bus_av_time = round(bus_sum_time / 3, 1)
            bus_av_cost = round(bus_sum_cost / 3, 3)
            r_list.append(bus_av_dis)
            r_list.append(bus_av_time)
            r_list.append(bus_av_cost)

        drive_strategy = [2, 4, 6]
        drive_sum_dis = 0
        drive_sum_time = 0
        drive_sum_cost = 0
        d_sign = 0
        fuel_price = get_fuel()

        for s in drive_strategy:
            data = {
                'origin': str(start_poi_lat) + "," + str(start_poi_lon),
                'destination': str(des_poi_lat) + "," + str(des_poi_lon),
                'tactics': s,
                'ak': 'YBZZIRimrGrpgbnRlQABvqvC1Vw8o7WD'
            }
            url = "http://api.map.baidu.com/direction/v2/driving"
            r = requests.get(url, params=data)
            result = r.json()
            routes = result['result']['routes'][0]
            if routes['distance'] is 1:
                r_list = []
                d_sign = 1
                break
            else:
                # we assume the car consume 10 L petrol per 100 km
                cost = round(float(fuel_price) * 10 * int(routes['distance']) / 100000, 2)
                drive_sum_dis += routes['distance']
                drive_sum_time += routes['duration']
                drive_sum_cost += (float(routes['toll']) + cost)

        if d_sign is 0:
            drive_av_dis = round(drive_sum_dis / 3, 1)
            drive_av_time = round(drive_sum_time / 3, 1)
            drive_av_cost = round(drive_sum_cost / 3, 3)
            r_list.append(drive_av_dis)
            r_list.append(drive_av_time)
            r_list.append(drive_av_cost)

        return jsonify(r_list)


@app.route('/get_h_info', methods=['POST'])
def get_info():
    if request.method == "POST":
        data = request.get_json()
        url = data["url"]
        get_hotel_info(url)
        return '0'


@app.route('/get_hotel', methods=['POST'])
def get_hotel():
    if request.method == "POST":
        data = request.get_json()
        start_poi_lon = float(data["start_poi_lon"])
        start_poi_lat = float(data["start_poi_lat"])
        des_poi_lon = float(data["des_poi_lon"])
        des_poi_lat = float(data["des_poi_lat"])

        start_min = float("inf")
        des_min = float("inf")
        # start_dis_id = 0
        # des_dis_id = 0
        hotel_data = xlrd.open_workbook('hotel_info_chengdu.xls')
        sheet = hotel_data.sheet_by_index(0)
        nrows = sheet.nrows  # the number of rows
        for i in range(1, nrows):
            location = str(sheet.row_values(i, 2))
            lon = float(location.split(",")[0].split("'")[1])
            lat = float(location.split(",")[1].split("'")[0])
            start_dis = haversine(start_poi_lon, start_poi_lat, lon, lat)
            if start_dis < start_min:
                start_min = start_dis
                # start_dis_id = i
            des_dis = haversine(des_poi_lon, des_poi_lat, lon, lat)
            if des_dis < des_min:
                des_min = des_dis
                # des_dis_id = i

        start_rate = float("-inf")
        des_rate = float("-inf")
        start_rate_id = 0
        des_rate_id = 0
        for j in range(1, nrows):
            rate = float(str(sheet.cell(j, 0)).split("'")[1].split("'")[0])
            coor = str(sheet.row_values(j, 2))
            lon = float(coor.split(",")[0].split("'")[1])
            lat = float(coor.split(",")[1].split("'")[0])
            start_dis = haversine(start_poi_lon, start_poi_lat, lon, lat)
            if start_dis <= 1.2 * start_min:
                if rate > start_rate:
                    start_rate = rate
                    start_rate_id = j
            des_dis = haversine(des_poi_lon, des_poi_lat, lon, lat)
            if des_dis <= 1.2 * des_min:
                if rate > des_rate:
                    des_rate = rate
                    des_rate_id = j

        start_hotel_info = sheet.row_values(start_rate_id)
        start_hotel_info[1] = start_hotel_info[1].replace('\n', '')
        start_hotel_info[3] = start_hotel_info[3].replace('\n', '')
        start_hotel_info[3] = start_hotel_info[3].replace('\xa0', ' ')
        des_hotel_info = sheet.row_values(des_rate_id)
        des_hotel_info[1] = des_hotel_info[1].replace('\n', '')
        des_hotel_info[3] = des_hotel_info[3].replace('\n', '')
        des_hotel_info[3] = des_hotel_info[3].replace('\xa0', ' ')

        result = {'start_hotel_info': start_hotel_info, 'des_hotel_info': des_hotel_info}
        return result


if __name__ == '__main__':
    app.run(debug=True)



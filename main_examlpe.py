# -*- coding: utf-8 -*-
import os
import sys
import telnetlib
import subprocess
reload(sys)
sys.setdefaultencoding('utf8')
from flask import Flask, request, jsonify,render_template,redirect, flash
#from flask import send_file, send_from_directory, safe_join, abort, jsonify
import pymysql.cursors
import pymysql
from flask_sqlalchemy import SQLAlchemy
from config import Configuration
app = Flask(__name__)
app.config.from_object(Configuration)
app.secret_key = '12345'



@app.route('/')
def resume():

    return render_template('index.html', title='Resume')

@app.route('/generator')
def config():
    
    return render_template('config.html', title='Generator')


@app.route('/flash')
def flash():
    flash('You were successfully logged in')
    return render_template('flash.html')



@app.route('/get-config', methods = ['POST'])
def getconfig():
    vlanext = request.form.get('vlanext')
    vlanextid = request.form.get('vlanextid')
    vlannat = request.form.get('vlannat')
    vlannatid = request.form.get('vlannatid')
    vlanfake = request.form.get('vlanfake')
    vlanfakeid = request.form.get('vlanfakeid')
    vlansw = request.form.get('vlansw')
    vlanswid = request.form.get('vlanswid')
    ip = request.form.get('ip')
    gateway = ip[:6]+'.1'
    return render_template('get-config.html',vlanext=vlanext, vlanextid=vlanextid, 
                          vlannat=vlannat, vlannatid=vlannatid, vlanfake=vlanfake ,
                          vlanfakeid=vlanfakeid, vlansw=vlansw, vlanswid=vlanswid, ip=ip, gateway=gateway)
    print(dump())



@app.route('/vlan-list')
def vlanlist():
    conn = ( pymysql.connect(host = '185.190.150.7',
                             user = 'script',
                             password = 'golden1306!',
                             database = 'service',
                             charset='utf8' ) )

    cursor = conn.cursor()
    mySql_select_Query = '''SELECT h.id
                             , k.name type
                             , h.name
                             , h.startIp
                             , h.stopIp
                             , h.gateway
                             , h.mask
                             , vl.vlan vlans
                             ,(SELECT count(*) FROM eq_bindings WHERE INET_ATON(ip) BETWEEN INET_ATON(startIp) and INET_ATON(stopIp)) bindings
                             FROM `eq_neth` h
                             JOIN eq_kinds k on k.id = h.type
                             LEFT JOIN (SELECT GROUP_CONCAT(vl.vlan) vlan, neth FROM eq_vlan_neth n JOIN eq_vlans vl on vl.id = n.vlan GROUP BY neth) vl on vl.neth = h.id
                             ORDER  by 2,4'''
    cursor.execute(mySql_select_Query)
    return render_template('vlan-list.html', cursor=cursor)


@app.route("/get-image/<image_name>")
def get_image(image_name):

    try:
        return send_from_directory(app.config["FILE_STORAGE"], filename=image_name, as_attachment=True)
    except FileNotFoundError:
        abort(404)




@app.route("/switch-info")
def swinfo():
    conn = ( pymysql.connect(host = 'localhost',
                             user = 'grin',
                             password = 'golden1306!',
                             database = 'switch-info',
                             charset='utf8' ) )

    cursor = conn.cursor()
    mySql_select_Query = 'SELECT * FROM `sw-info`'

    cursor.execute(mySql_select_Query)
    return render_template('switch-info.html',cursor=cursor)




@app.route("/switch-add",methods = ['POST', 'GET'])
def swadd():
    sw = request.form.get('sw')
    ip = request.form.get('ip')
    location = request.form.get('location')
    presence = request.form.get('presence')
    fvlan = request.form.get('fvlan')
    model = request.form.get('model')
    conn = ( pymysql.connect(host = 'localhost',
                             user = 'grin',
                             password = 'golden1306!',
                             database = 'switch-info',
                             charset='utf8' ) )

    cursor = conn.cursor()
    sql = '''INSERT INTO `switch-info`.`sw-info`(`sw`, `ip`, `location`, `presence`, `fixed-vlan`, `model`)
             VALUES (%s, %s, %s, %s, %s, %s)'''
    cursor.execute(sql, [sw, ip, location, presence, fvlan, model])
    conn.commit()
    return redirect("https://grin.golden.net.ua/switch-info")


@app.route("/switch-edit=<int:id>")
def swedit(id):
    conn = ( pymysql.connect(host = 'localhost',
                             user = 'grin',
                             password = 'golden1306!',
                             database = 'switch-info',
                             charset='utf8' ) )

    cursor = conn.cursor()
    cursor.execute('SELECT * FROM `sw-info` WHERE id= %s;',(id))
    return render_template('switch-edit.html',cursor=cursor)


@app.route("/switch-update",methods = ['POST', 'GET'])
def swupdate():
    sw = request.form.get('sw')
    ip = request.form.get('ip')
    location = request.form.get('location')
    presence = request.form.get('presence')
    fvlan = request.form.get('fvlan')
    model = request.form.get('model')
    id = request.form.get('id')
    conn = ( pymysql.connect(host = 'localhost',
                             user = 'grin',
                             password = 'golden1306!',
                             database = 'switch-info',
                             charset='utf8' ) )

    cursor = conn.cursor()
    sql = '''UPDATE `switch-info`.`sw-info` SET `sw`= %s, `ip`= %s, `location`= %s, `presence`= %s, `fixed-vlan`= %s, `model`= %s  WHERE `id` = %s'''
    cursor.execute(sql, [sw, ip, location, presence, fvlan, model, id])
    conn.commit()
    return redirect("https://grin.golden.net.ua/switch-info")





if __name__=='__main__':
    app.run(port=8000)



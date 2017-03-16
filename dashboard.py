#! /usr/bin/env python2

import boto.ec2
import boto.exception
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

# default configuration
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'
DEFAULT_REGION = 'us-east-1'
REGIONS = ['us-east-1', 'us-west-2', 'us-west-1', 'us-east-2']

# create app
app = Flask(__name__)
app.config.from_envvar('DASHAPP_SETTINGS', silent=False)
app.secret_key = app.config['SECRET_KEY']

def _instance_list(conn, filterset):
    return conn.get_only_instances(filters=filterset)

def _parse_hibernation(valueString):
    VALID_DAYS = set(str(x) for x in range(0, 7))
    VALID_HOURS = set(str(x) for x in range(0, 24))
    parsed = {'days': '', 'hours': ''}
    if valueString.count("|"):
        hours, days = (x.strip() for x in valueString.split("|"))
    else:
        return parsed
    if days:
        days = days.split(",")
        days = [int(x) for x in days if x in VALID_DAYS]
        parsed['days'] = days
    if hours:
        if hours.count(",") == 1:
            start, stop = hours.split(",")
            if start in VALID_HOURS and start != stop and stop in VALID_HOURS:
                parsed['start'] = start
                parsed['stop'] = stop
    return parsed

@app.before_request
def before_request():
    if not session.get('region'):
        session['region'] = app.config['DEFAULT_REGION']
    region = request.args.get('region', None)
    if region and region in REGIONS:
        session['region'] = region

@app.route('/', methods=['GET'])
@app.route('/ServiceOwner/<ownerfilter>', methods=['GET'])
def display_list(ownerfilter=None):
    ec2 = boto.ec2.connect_to_region(session['region'])
    filters = {"tag:InstanceHibernate":"*"}
    if ownerfilter:
        filters["tag:ServiceOwner"] = ownerfilter
    instances = _instance_list(ec2, filters)
    return render_template('list_instances.html', instances=instances)

@app.route('/instance/<instanceid>')
def display_instance(instanceid):
    ec2 = boto.ec2.connect_to_region(session['region'])
    if instanceid:
        try:
            i = ec2.get_only_instances([instanceid])[0]
            htag = i.tags.get('InstanceHibernate', '')
            hibernation = _parse_hibernation(htag)
            instance = {"obj": i, "hibernation": hibernation}
            return render_template('instance_view.html', inst=instance)
        except boto.exception.EC2ResponseError, e:
            return render_template('oops.html', error={'message': e})
    else:
        return render_template('oops.html',
            error={'message': 'No Instance Id'})

if __name__ == '__main__':
    app.run(host='0.0.0.0')

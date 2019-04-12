# -*- coding: utf-8 -*-
import datetime
import json

from blueking.component.shortcuts import get_client_by_request
from common.mymako import render_mako_context, render_json
from home_application.biz_utils import get_app_by_user
from common.log import logger
from home_application import celery_tasks
from home_application.models import OptLog

def home(request):
    """
    首页
    """
    """根据用户权限获取业务列表"""
    client = get_client_by_request(request)
    client.set_bk_api_ver('v2')
    # 根据权限查询业务列表
    bk_biz_list = get_app_by_user(request.COOKIES['bk_token'])
    for x in bk_biz_list:
        if x.get("app_name") == u'\u8d44\u6e90\u6c60' or x.get("app_name") == 'Resource pool':
            bk_biz_list.remove(x)
            break

    return render_mako_context(request, '/home_application/home.html' , {
        'bk_biz_list': bk_biz_list })


def test(request):
    """
    测试接口
    :param request:
    :return:
    """
    username = request.user.username
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result = {
        "result": True,
        "message": "success",
        "data": {
            'user': username,
            'time': str(now_time)
        }
    }
    return render_json(result)


def dev_guide(request):
    """
    开发指引
    """
    return render_mako_context(request, '/home_application/dev_guide.html')


def contactus(request):
    """
    联系我们
    """
    return render_mako_context(request, '/home_application/contact.html')


def get_set_list(request):
    """
    根据业务id获取集群列表
    :param request:
    :return:
    """
    """获取集群列表"""
    client = get_client_by_request(request)
    client.set_bk_api_ver('v2')
    biz_id = request.GET['bizID']
    if not biz_id:
        return render_json(
            {
                "result": False,
                "message": u"没有选择业务",
            })

    param = {
        "bk_biz_id": biz_id,
        "fields": [
            "bk_set_id",
            "bk_set_name"
        ]
    }
    res = client.cc.search_set(param)
    return render_mako_context(request, '/home_application/set_option.html',
                               {'set_list': res.get('data').get('info')})


def get_host_list(request):
    """
    根据业务id，集群id，获取主机列表
    :param request:
    :return:
    """
    client = get_client_by_request(request)
    client.set_bk_api_ver('v2')
    biz_id = request.GET['bizID']
    set_id = request.GET['setID']
    res = client.cc.search_host({
        "bk_biz_id": biz_id,
        "condition": [
            {
                "bk_obj_id": "set",
                "fields": [],
                "condition": [
                    {
                        "field": "bk_set_id",
                        "operator": "$eq",
                        "value": int(set_id)
                    }
                ]
            }
        ]
    })
    if res.get('result', False):
        bk_host_list = res.get('data').get('info')
    else:
        bk_host_list = []
        logger.error(u"请求主机列表失败：%s" % res.get('message'))

    bk_host_list = [
        {
            'bk_host_name': host['host']['bk_host_name'],
            'bk_host_innerip': host['host']['bk_host_innerip'],
            'bk_cloud_id': host['host']['bk_cloud_id'][0]['bk_inst_id'],
            'bk_cloud_name': host['host']['bk_cloud_id'][0]['bk_inst_name'],
            'bk_os_name': host['host']['bk_os_name']
        }
        for host in bk_host_list
    ]
    return render_mako_context(request, '/home_application/ip_table.html',
                               {'bk_host_list': bk_host_list})





def history(request):
    """
    执行历史界面
    """
    """根据用户权限获取业务列表"""
    client = get_client_by_request(request)
    client.set_bk_api_ver('v2')
    # 根据权限查询业务列表
    bk_biz_list = get_app_by_user(request.COOKIES['bk_token'])
    for x in bk_biz_list:
        if x.get("app_name") == u'\u8d44\u6e90\u6c60' or x.get("app_name") == 'Resource pool':
            bk_biz_list.remove(x)
            break
    return render_mako_context(request, '/home_application/history.html', {
        'bk_biz_list': bk_biz_list })


def fast_execute_script(request):
    """快速执行脚本"""
    req = json.loads(request.body)
    client = get_client_by_request(request)
    host_list = req.get('hosts')
    biz_id = req.get('bizID')
    user_name = request.user
    celery_tasks.execute_task(biz_id, user_name, host_list)
    return render_json({
        'result': True,
        'data': '提交成功' })


def get_history_log(request):
    """
    查询执行日志
    :param request:
    :return:
    """
    biz_id = request.GET['bizID']
    if biz_id == 'all':
        history_result = OptLog.objects.all()
    else:
        history_result = OptLog.objects.filter(bizID=biz_id)
    log_list = []
    for history in history_result:
        temp = {
            "createUser": history.createUser,
            "log": history.log,
            "bizName": history.bizName,
            "ipList": history.ipList,
            "actionTime": str(history.actionTime),
            "jobID": history.jobID
        }
        if history.jobStatus == 3:
            temp["jobStatus"] = 'success'
        else:
            temp["jobStatus"] = 'failed'
        log_list.append(temp)
    return render_mako_context(request, '/home_application/historyTable.html',
                               {'historyList': log_list})
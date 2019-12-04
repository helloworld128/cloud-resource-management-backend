from flask import request
from flask_restplus import Resource, Namespace

from app.main.util.decorator import token_required, admin_token_required
from ..service.judge_service import judgeFunc, get_status
from app.main.service.auth_helper import Auth


api = Namespace('judge', description='judging operations')


@api.route('/submit/<id>')
class Judge(Resource):
    @api.param('Authorization', 'authorization token', 'header')
    @api.doc('submit current problem', params={'id':'task id'})
    def get(self, id):
        """submit current problem"""
        userid = Auth.get_logged_in_user_id(request)
        return judgeFunc(id, userid)


@api.route('/result/<id>')
class Result(Resource):
    @api.param('Authorization', 'authorization token', 'header')
    @api.doc('get result of submission', params={'id':'task id'})
    def get(self, id):
        userid = Auth.get_logged_in_user_id(request)
        return get_status(id, userid)


from flask import request
from flask_restplus import Resource, Namespace

from app.main.util.decorator import token_required, admin_token_required
from ..service.editor_service import read_file, save_file, get_file_tree, create_file, delete_file
from app.main.service.auth_helper import Auth


api = Namespace('editor', description='web editor related operations')


@api.route('/file')
class File(Resource):
    @token_required
    @api.param('Authorization', 'authorization token', 'header')
    @api.param('id', 'task id', 'header')
    @api.param('name', 'file name', 'header')
    @api.doc('get a file')
    def get(self):
        """get a file"""
        userid = Auth.get_logged_in_user_id(request)
        taskid = request.headers.get('id')
        name = request.headers.get('name')
        return read_file(taskid, userid, name)

    @api.response(201, 'File successfully created.')
    @token_required
    @api.param('Authorization', 'authorization token', 'header')
    @api.param('id', 'task id', 'body')
    @api.param('name', 'file name', 'body')
    @api.doc('create a new file')
    def post(self):
        """create a new file"""
        userid = Auth.get_logged_in_user_id(request)
        taskid = request.json.get('id')
        name = request.json.get('name')
        return create_file(taskid, userid, name)

    @token_required
    @api.param('Authorization', 'authorization token', 'header')
    @api.param('content', 'file content', 'body')
    @api.param('id', 'task id', 'body')
    @api.param('name', 'file name', 'body')
    @api.doc('save a file')
    def put(self):
        """save a file"""
        userid = Auth.get_logged_in_user_id(request)
        data = request.json
        return save_file(userid, data)

    @token_required
    @api.param('Authorization', 'authorization token', 'header')
    @api.doc('delete a file')
    @api.param('id', 'task id', 'body')
    @api.param('name', 'file name', 'body')
    def delete(self):
        """delete a file"""
        userid = Auth.get_logged_in_user_id(request)
        taskid = request.json.get('id')
        name = request.json.get('name')
        return delete_file(taskid, userid, name)


@api.route('/filetree')
class FileTree(Resource):
    @token_required
    @api.param('Authorization', 'authorization token', 'header')
    @api.param('id', 'task id', 'header')
    @api.doc('get whole file tree of current user')
    def get(self):
        userid = Auth.get_logged_in_user_id(request)
        taskid = request.headers.get('id')
        return get_file_tree(taskid, userid)



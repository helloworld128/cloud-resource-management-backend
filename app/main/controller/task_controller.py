from flask import request
from flask_restplus import Resource

from app.main.util.decorator import token_required, admin_token_required
from app.main.service.auth_helper import Auth
from ..util.dto import TaskDto
from ..service.task_service import (get_all_tasks, get_a_task, save_new_task, 
                                    save_uploaded_files, modify_a_task, get_a_task_admin)
import sys

api = TaskDto.api


@api.route('/')
class TaskList(Resource):
    @api.doc('list_of_tasks')
    @api.marshal_list_with(TaskDto.task)
    def get(self):
        """List all tasks"""
        return get_all_tasks()

    # @admin_token_required
    # @api.param('Authorization', 'authorization token', 'header')
    @api.expect(TaskDto.taskAdmin, validate=True)
    @api.response(201, 'Task successfully created.')
    @api.doc('create a new task')
    def post(self):
        """Creates a new task """
        data = request.json
        return save_new_task(data=data)


@api.route('/<id>')
class Task(Resource):
    @token_required
    @api.doc('get a task', params={'id':'task id'})
    @api.marshal_with(TaskDto.taskUser)
    @api.param('Authorization', 'authorization token', 'header')
    @api.response(404, 'Task not found.')
    @api.response(503, 'Cannot get websocket url')
    def get(self, id):
        """get a task given its identifier"""
        userid = Auth.get_logged_in_user_id(request)
        return get_a_task(userid, id)

    # @admin_token_required
    # @api.param('Authorization', 'authorization token', 'header')
    @api.doc('modify a task', params={'id':'task id'})
    @api.expect(TaskDto.taskAdmin, validate=True)
    def put(self, id):
        """modify a task given its identifier"""
        data = request.json
        return modify_a_task(id, data)


@api.route('/admin/<id>')
class AdminTask(Resource):
    # @admin_token_required
    # @api.param('Authorization', 'authorization token', 'header')
    @api.doc('get a task (only for administrator)', params={'id':'task id'})
    @api.marshal_with(TaskDto.taskAdmin)
    @api.response(404, 'Task not found.')
    def get(self, id):
        """get a task given its identifier"""
        return get_a_task_admin(id)


@api.route('/upload/<id>')
class Upload(Resource):
    # @admin_token_required
    # @api.param('Authorization', 'authorization token', 'header')
    @api.doc('upload Dockerfile, initial files and judge script. \
    Note the request should use "multipart/form-data" for file uploading.', params={'id':'task id'})
    def post(self, id):
        """upload Dockerfile, initial files and judge script"""
        files = request.files.getlist("fileUpload")
        return save_uploaded_files(files, id)


@api.route('/images')
class Image(Resource):
    @api.doc('get available images')
    def get(self):
        """get available images"""
        return ['mysshd', 'mypython3', 'mycpp'], 200
        
        


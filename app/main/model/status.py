from .. import db
import datetime


class Status(db.Model):
    """ 
    Status Model for storing info related to every (user, task) pair, 
    including socketid for the pair, username and password.
    """
    __tablename__ = "status"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid = db.Column(db.Integer, db.ForeignKey('users.id'))
    taskid = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    status = db.Column(db.String(64))
    socketid = db.Column(db.String(64))
    username = db.Column(db.String(64))
    password = db.Column(db.String(64))
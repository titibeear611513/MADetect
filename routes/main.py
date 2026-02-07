"""
主頁路由
"""
from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def homepage():
    """首頁"""
    return render_template('homepage.html')

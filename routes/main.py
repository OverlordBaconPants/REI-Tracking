from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
import logging
import requests

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/main')
@login_required
def main():
    return render_template('main/main.html', name=current_user.name)

@main_bp.route('/properties')
@login_required
def properties():
    return render_template('main/properties.html')

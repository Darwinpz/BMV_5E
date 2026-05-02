from flask import Blueprint, redirect, url_for

index_bp = Blueprint("index", __name__, url_prefix='/')

@index_bp.route('/', methods=['GET'])
def indexRoute():
    return redirect(url_for('vocacional.index'))

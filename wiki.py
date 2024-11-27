from flask import Flask, render_template, abort, send_from_directory, url_for, jsonify
import os
from socket import gaierror

sesid = None
app = Flask(__name__)

wiki_folder = './wiki_files'
resources = './templates'
staticf = './static'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'txt', 'html'}

def is_allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/wiki/<path:filename>/')
def serve_file(filename):
    if not is_allowed_file(filename):
        return abort(404, description="File type not allowed")
    
    try:
        return send_from_directory(wiki_folder, filename)
    except FileNotFoundError:
        return abort(404, description="File not found")

@app.route('/wiki/')
def list_files():
    try:
        files = [f for f in os.listdir(cdn_folder) if is_allowed_file(f)]
    except FileNotFoundError:
        return abort(404, description="Directory not found")
    
    return render_template('wiki_list.html', files=files)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    if not os.path.exists(wiki_folder):
        os.makedirs(wiki_folder)
    app.run(debug=False, host='0.0.0.0', port=5000)

from flask import Flask, render_template, send_from_directory, request
from predict import predict_bp

app = Flask(__name__, static_folder='static')

# 注册 predict
app.register_blueprint(predict_bp)

# 路由到首页，并渲染 index.html
@app.route('/')
def index():
    return render_template('index.html')

# 路由到静态文件
@app.route('/static/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

# 路由到查询请求处理
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form['query']
        # 这里可以添加查询逻辑，例如数据库查询等
        # 现在只是简单地返回查询的值
        return f'You searched for: {query}'
    return render_template('search.html')

if __name__ == '__main__':
    app.run(debug=True)
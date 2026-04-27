from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import config

db = SQLAlchemy()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    CORS(app)
    db.init_app(app)
    
    # 注册蓝图
    from routes.api import api_bp
    from routes.process_mining import mining_bp
    from routes.simulation import simulation_bp
    
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(mining_bp, url_prefix='/api/mining')
    app.register_blueprint(simulation_bp, url_prefix='/api/simulation')
    
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app('development')
    app.run(debug=True, port=5000)

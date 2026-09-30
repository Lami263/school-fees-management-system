from flask import Flask
from app.config import Config
from app.extensions import db, jwt, cors


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    from app.routes.auth import auth_bp
    from app.routes.students import students_bp
    from app.routes.classes_terms import classes_terms_bp
    from app.routes.fees import fees_bp
    from app.routes.discounts import discounts_bp
    from app.routes.payments import payments_bp
    from app.routes.receipts import receipts_bp
    from app.routes.reports import reports_bp
    from app.routes.search import search_bp
    from app.routes.audit import audit_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(students_bp, url_prefix="/api/students")
    app.register_blueprint(classes_terms_bp, url_prefix="/api")
    app.register_blueprint(fees_bp, url_prefix="/api/fee-structures")
    app.register_blueprint(discounts_bp, url_prefix="/api/discounts")
    app.register_blueprint(payments_bp, url_prefix="/api/payments")
    app.register_blueprint(receipts_bp, url_prefix="/api/receipts")
    app.register_blueprint(reports_bp, url_prefix="/api/reports")
    app.register_blueprint(search_bp, url_prefix="/api/search")
    app.register_blueprint(audit_bp, url_prefix="/api/audit")

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    with app.app_context():
        db.create_all()

    return app

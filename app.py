from flask import Flask


from database import create_recruita_core_tables
from routes.admin_routes import register_admin_routes
from routes.auth_routes import register_auth_routes
from routes.company_routes import register_company_routes
from routes.student_routes import register_student_routes



app = Flask(__name__)
app.config["SECRET_KEY"] = "recruita-secret-key"


create_recruita_core_tables()


register_auth_routes(app)
register_admin_routes(app)
register_company_routes(app)
register_student_routes(app)



if __name__ == "__main__":
      app.run(debug=True)

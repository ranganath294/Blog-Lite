from blog import create_app
from flask_restful import Resource, Api

if __name__ == "__main__":
    app, api = create_app()
    
    from blog.api import UserAPI, BlogAPI
    api.add_resource(UserAPI, "/api/<string:username>")
    api.add_resource(BlogAPI, "/api/<int:id>")

    app.run(debug=True)
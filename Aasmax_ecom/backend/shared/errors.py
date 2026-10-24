from flask import jsonify

def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(err):
        return jsonify({"success": False, "message": "Bad request"}), 400

    @app.errorhandler(401)
    def unauthorized(err):
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    @app.errorhandler(403)
    def forbidden(err):
        return jsonify({"success": False, "message": "Forbidden"}), 403

    @app.errorhandler(404)
    def not_found(err):
        return jsonify({"success": False, "message": "Not found"}), 404

    @app.errorhandler(500)
    def server_error(err):
        app.logger.exception("Unhandled error")
        return jsonify({"success": False, "message": "Internal server error"}), 500

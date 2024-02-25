from flask import jsonify

class result:
    @staticmethod
    def OK(message, status, data):
        return jsonify({
            "message": message,
            "status": status,
            "data": data
        }),200
        
    @staticmethod
    def error(message, status, data):
        return jsonify({
            "message": message,
            "status": status,
            "data": data
        }),500
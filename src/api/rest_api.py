from flask import Flask, request, jsonify
from core.firewall import DatabaseFirewall

app = Flask(__name__)
firewall = DatabaseFirewall()


@app.route('/api/query', methods=['POST'])
def execute_query():
    data = request.json
    is_auth, results, reason = firewall.execute_query(
        data['app_id'],
        request.remote_addr,
        data['operation'],
        data['query']
    )

    return jsonify({
        'authorized': is_auth,
        'results': results,
        'reason': reason
    })


@app.route('/api/logs', methods=['GET'])
def get_logs():
    return jsonify(firewall.get_logs())
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "ok",
        "message": "LLM_PEXPERIMENT MVP is LIVE!",
        "service": "Government Consulting LLM Automation",
        "version": "1.0.0"
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    app.run()

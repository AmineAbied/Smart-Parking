from flask import Flask

app = Flask(__name__)

free_slot = "a1"

@app.route("/parking", methods=["GET"])
def parking():

    return free_slot

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

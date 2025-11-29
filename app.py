from flask import Flask, render_template

app = Flask(__name__)

# Ajusta esta URL si cambias el endpoint del stream en Render
STREAM_URL = "https://vision-ia-server.onrender.com/stream"

@app.route("/")
def panel():
    # Enviamos la URL del stream a la plantilla por si quieres cambiarla dinámicamente
    return render_template("panel.html", stream_url=STREAM_URL)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

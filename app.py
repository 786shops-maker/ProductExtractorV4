"""
app.py
Flask web application for Product Extractor V3.
"""
import os
import threading
from flask import Flask, render_template, request, jsonify, send_from_directory
from extractor.parser import Parser
from extractor.exceptions import ProductExtractorError

app = Flask(__name__)
parser = Parser(output_dir="downloads")

# Global progress tracker
progress_state = {
    "percent": 0,
    "message": "Idle",
    "running": False,
    "result": None,
    "error": None
}

def update_progress(percent, message):
    progress_state["percent"] = percent
    progress_state["message"] = message

# Route to serve downloaded images so they show up on the web page
@app.route('/downloads/<path:filename>')
def serve_download(filename):
    return send_from_directory('downloads', filename)

@app.get("/")
def welcome():
    return render_template("welcome.html")

@app.get("/extract")
def extract_page():
    return render_template("index.html")

@app.post("/run-extract")
def run_extract():
    url = request.form.get("url", "").strip()
    if not url:
        return jsonify({"success": False, "error": "URL is required"})
    
    if progress_state["running"]:
        return jsonify({"success": False, "error": "Another extraction is already running"})
    
    progress_state["running"] = True
    progress_state["percent"] = 0
    progress_state["message"] = "Starting..."
    progress_state["result"] = None
    progress_state["error"] = None
    
    def run_extraction():
        try:
            result = parser.parse(url, progress_callback=update_progress)
            
            # --- Calculate correct price and format images for web ---
            price_info = result.get("price_info", {})
            price = str(price_info.get("price", "")).replace(",", "")
            sale_price = str(price_info.get("sale_price", "")).replace(",", "")
            
            # If there is a sale price and it's different, use it as the final price
            final_price = sale_price if (sale_price and sale_price != price) else price
            on_sale = bool(sale_price and sale_price != price)
            
            # Convert local image paths to web URLs
            web_images = []
            for img_path in result.get("images", []):
                try:
                    relative_path = os.path.relpath(img_path, 'downloads')
                    web_images.append(f"/downloads/{relative_path.replace(os.sep, '/')}")
                except:
                    pass

            progress_state["result"] = {
                "title": result.get("display_title", ""),
                "brand": result.get("brand", ""),
                "product_id": result.get("product_id", ""),
                "color": result.get("dress_color", ""),
                "description": result.get("description", ""),
                "price": final_price,
                "original_price": price if on_sale else "",
                "on_sale": on_sale,
                "url": url,
                "images": web_images
            }
        except Exception as e:
            progress_state["error"] = str(e)
        finally:
            progress_state["running"] = False
            progress_state["percent"] = 100
            progress_state["message"] = "Done!"
    
    thread = threading.Thread(target=run_extraction)
    thread.start()
    
    return jsonify({"success": True, "message": "Extraction started"})

@app.get("/progress")
def get_progress():
    return jsonify(progress_state)

@app.get("/result")
def result_page():
    if progress_state["error"]:
        return render_template("result.html", success=False, error=progress_state["error"])
    if progress_state["result"]:
        return render_template("result.html", success=True, product=progress_state["result"])
    return render_template("result.html", success=False, error="No result available")

if __name__ == "__main__":
    app.run(debug=True, port=5000, threaded=True)
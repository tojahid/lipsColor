# importing modules 
from flask import Flask, render_template, Response, request
from camera import VideoCamera
  
# declaring app name 
app = Flask(__name__) 

color_HexCode = "d2e603"
# defining home page 
@app.route('/', methods = ['POST', 'GET']) 
def homepage():
    global color_HexCode
    if request.method == 'POST':
        color_text = request.form['color_input']
        print(color_text)
        color_HexCode = color_text
        camera = VideoCamera(color_HexCode)
    return render_template("index00.html") 


def gen(camera):
    while True:
        #get camera frame
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        
@app.route('/video_feed')
def video_feed():
    global color_HexCode
    return Response(gen(VideoCamera(hexCode=color_HexCode)), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__': 
    app.run( host='127.0.0.1', port=5000 ,debug=False, threaded=False)

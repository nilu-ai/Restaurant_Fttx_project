from flask import Flask, request, jsonify
import cv2
import numpy as np
import base64
from deepface import DeepFace
import os
import sqlite3

app = Flask(__name__)

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    photo BLOB,
                    order_count INTEGER DEFAULT 0,
                    fav_dish TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    order_details TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(id))''')
    conn.commit()
    conn.close()
init_db()

@app.route('/', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        data = request.json
        img_data = data['image'].split(',')[1]
        nparr = np.frombuffer(base64.b64decode(img_data), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        try:
            predictions = DeepFace.find(img_path=img, db_path="trainss", model_name="Facenet512")
            face = DeepFace.analyze(img, ['emotion'])

            if not predictions[0].empty and predictions[0].distance[0] < 0.3:
                identity = predictions[0].identity[0].split("/")[3]

                conn = sqlite3.connect('users.db')
                c = conn.cursor()
                c.execute("SELECT id, username FROM users WHERE username = ?", (identity,))
                user = c.fetchone()
                conn.close()

                response = {
                    'id': user[0],
                    'username': user[1],
                    'emotion': face[0]["dominant_emotion"]
                }
            else:
                response = {'prediction': 'unknown User'}
        except Exception as e:
            response = {'status': 'error', 'message': str(e)}

        return jsonify(response)

    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body>
        <video id="video" width="640" height="480" autoplay></video>
        <canvas id="canvas" width="640" height="480" style="display:none;"></canvas>
        <div id="prediction"></div>
        <script>
            const video = document.getElementById('video');
            const canvas = document.getElementById('canvas');
            const predictionDiv = document.getElementById('prediction');

            async function initCamera() {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                    video.srcObject = stream;
                } catch (err) {
                    console.error('Error accessing camera:', err);
                }
            }

            async function captureAndPredict() {
                const context = canvas.getContext('2d');
                context.drawImage(video, 0, 0, canvas.width, canvas.height);
                const imageData = canvas.toDataURL('image/jpeg');
                const response = await fetch('/', {
                    method: 'POST',
                    body: JSON.stringify({ image: imageData }),
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                const result = await response.json();
                predictionDiv.innerHTML = JSON.stringify(result, null, 2);
            }

            setInterval(captureAndPredict, 1000);

            initCamera();
        </script>
    </body>
    </html>
    """

@app.route('/new_user', methods=['GET', 'POST'])
def newuser():
    if request.method == 'POST':
        print("image storing started")
        data = request.get_json()
        username = data['username']
        photos = data['photos']

        # Create directory for the new user
        user_dir = os.path.join('trainss', username)
        os.makedirs(user_dir, exist_ok=True)

        # Save photos and store the first one in the database

        for i, photo in enumerate(photos):
            photo_data = base64.b64decode(photo.split(',')[1])
            print(i)
            with open(os.path.join(user_dir, f'photo_{i+1}.jpg'), 'wb') as f:
                f.write(photo_data)
        photo_datas = base64.b64decode(photos[0].split(',')[1])
        with open(os.path.join(user_dir, 'photo_10.jpg'), 'wb') as f:
            f.write(photo_datas)
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, photo) VALUES (?, ?)", (username, photo_datas))
        conn.commit()
        conn.close()

        return jsonify({'status': 'success', 'message': 'User data saved.'})

    else:
        return '''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
            </head>
            <body>
                <video id="video" width="640" height="480" autoplay></video>
                <canvas id="canvas" width="640" height="480" style="display:none;"></canvas>
                <label>Name: <input id="username" type="text"/></label>
                <button id="submitimage">Submit New Data</button>
                <script>
                    const video = document.getElementById('video');
                    const canvas = document.getElementById('canvas');
                    const submit = document.getElementById('submitimage');
                    const usernameInput = document.getElementById('username');
                    let photos = [];
                    let photoCount = 0;

                    async function initCamera() {
                        try {
                            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                            video.srcObject = stream;
                        } catch (err) {
                            console.error('Error accessing camera:', err);
                        }
                    }

                    function capturePhoto() {
                        const context = canvas.getContext('2d');
                        context.drawImage(video, 0, 0, canvas.width, canvas.height);
                        const imageData = canvas.toDataURL('image/jpeg');
                        photos.push(imageData);
                    }

                    async function submitData() {
                        if (photoCount < 5) {
                            capturePhoto();
                            photoCount++;
                            setTimeout(submitData, 500); // Capture a photo every second
                        } else {
                            const username = usernameInput.value;
                            const response = await fetch('/new_user', {
                                method: 'POST',
                                body: JSON.stringify({ username, photos }),
                                headers: {
                                    'Content-Type': 'application/json'
                                }
                            });
                            const result = await response.json();
                            console.log(result);
                        }
                    }

                    submit.addEventListener('click', () => {
                        photoCount = 0;
                        photos = [];
                        submitData();
                    });

                    initCamera();
                </script>
            </body>
            </html>
        '''

@app.route('/update_user', methods=['GET','POST'])
def update_user():
  if request.method == 'POST':
      data = request.get_json()
      user_id = data['id']
      order_details = data.get('order')
      fav_dish = data.get('fav_dish')

      conn = sqlite3.connect('users.db')
      c = conn.cursor()

      if order_details:
          c.execute("INSERT INTO orders (user_id, order_details) VALUES (?, ?)", (user_id, order_details))
          c.execute("UPDATE users SET order_count = order_count + 1 WHERE id = ?", (user_id,))

      if fav_dish:
          c.execute("UPDATE users SET fav_dish = ? WHERE id = ?", (fav_dish, user_id))

      conn.commit()
      conn.close()

      return jsonify({'status': 'success', 'message': 'User data updated.'})
  else:
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>

        </style>
    </head>
    <body>

        <label>Name: <input id="id" type="text"/></label>
        <label>Order: <input id="order" type="text"/></label>
        <label>Favorite Dish: <input id="fav_dish" type="text"/></label>
        <button id="updatedata">Submit New Data</button>
        <script>




        </script>
    </body>
    </html>
    """



@app.route('/user/<int:user_id>', methods=['GET','POST'])
def get_user(user_id):
  if request.method == 'POST':
      conn = sqlite3.connect('users.db')
      c = conn.cursor()
      c.execute("SELECT username, order_count, fav_dish ,photo FROM users WHERE id = ?", (user_id,))
      user = c.fetchone()

      if user==None:
          return jsonify({'status': 'error', 'message': 'User not found'})

      c.execute("SELECT order_details FROM orders WHERE user_id = ? ORDER BY id DESC LIMIT 10", (user_id,))
      orders = [order[0] for order in c.fetchall()]

      conn.close()
      img_base64 = base64.b64encode(user[3]).decode('utf-8')

      return jsonify({
          'username': user[0],
          'order_count': user[1],
          'fav_dish': user[2],
          'last_10_orders': orders,
          'userphoto':img_base64
      })

  else:
      return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>

        </style>
    </head>
    <body>

            <div id="user-info">
             <img id="user-image" width="200" height="200" src="" alt="User Image">
        <p id="username"></p>
        <p id="order-count"></p>
        <p id="fav-dish"></p>
        <p id="last-orders"></p>

    </div>
        <script>

            const predictionDiv = document.getElementById('prediction');
            var id = window.location.href.split("/").pop().split("?")[0];


            async function captureAndPredict() {


                console.log(id)
                const response = await fetch(`/user/${id}`, {
                    method: 'POST',

                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                const result = await response.json();
                 console.log(result)
                const userData=result
                      document.getElementById("username").textContent = "Customer Name: " + userData.username;
        document.getElementById("order-count").textContent = "Order Count: " + userData.order_count;
        document.getElementById("fav-dish").textContent = "Favorite Dish: " + userData.fav_dish;
        document.getElementById("last-orders").textContent = "Last 10 Orders: " + userData.last_10_orders.join(", ");

        // Set user image
        const imgElem = document.getElementById("user-image");
        imgElem.src = "data:image/jpeg;base64," + userData.userphoto;

            }

            captureAndPredict()


        </script>
    </body>
    </html>
    """
@app.route('/add_order', methods=['GET', 'POST'])
def add_order():
    if request.method == 'POST':
        data = request.get_json()
        user_id = data['id']
        order_details = data['order']

        conn = sqlite3.connect('users.db')
        c = conn.cursor()

        c.execute("INSERT INTO orders (user_id, order_details) VALUES (?, ?)", (user_id, order_details))
        c.execute("UPDATE users SET order_count = order_count + 1 WHERE id = ?", (user_id,))

        conn.commit()
        conn.close()

        return jsonify({'status': 'success', 'message': 'Order added successfully.'})
    else:
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body>
            <label>User ID: <input id="id" type="text"/></label>
            <label>Order: <input id="order" type="text"/></label>
            <button id="addorder">Add Order</button>
            <script>
                document.getElementById('addorder').onclick = function() {
                    var id = document.getElementById('id').value;
                    var order = document.getElementById('order').value;

                    fetch('/add_order', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({id: id, order: order})
                    }).then(response => response.json())
                      .then(data => alert(data.message));
                };
            </script>
        </body>
        </html>
        """

if __name__ == '__main__':
    app.run()


# # Importing flask module in the project is mandatory
# # An object of Flask class is our WSGI application.
# from flask import Flask

# # Flask constructor takes the name of 
# # current module (__name__) as argument.
# app = Flask(__name__)

# # The route() function of the Flask class is a decorator, 
# # which tells the application which URL should call 
# # the associated function.
# @app.route('/')
# # ‘/’ URL is bound with hello_world() function.
# def hello_world():
#     return 'Hello World'

# # main driver function
# if __name__ == '__main__':

#     # run() method of Flask class runs the application 
#     # on the local development server.
#     app.run()

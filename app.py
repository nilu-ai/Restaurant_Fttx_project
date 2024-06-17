from flask import Flask, request, jsonify
import cv2
import numpy as np
import base64
from deepface import DeepFace
import os
import sqlite3
from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import Error
app = Flask(__name__)

# Initialize SQLite database
def init_db():
    try:
        conn = mysql.connector.connect(
            host='sql12.freesqldatabase.com',
            user='sql12713824',
            password='ds6QqFFFZ6',  # Replace with your MySQL password
            database='sql12713824'  # Replace with your MySQL database name
        )
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                id INT AUTO_INCREMENT PRIMARY KEY,
                                username VARCHAR(255),
                                photo LONGBLOB,
                                order_count INT DEFAULT 0,
                                fav_dish VARCHAR(255))''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
                                id INT AUTO_INCREMENT PRIMARY KEY,
                                user_id INT,
                                order_details TEXT,
                                FOREIGN KEY(user_id) REFERENCES users(id))''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS visits (
                                id INT AUTO_INCREMENT PRIMARY KEY,
                                user_id INT UNIQUE,
                                visit_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                FOREIGN KEY(user_id) REFERENCES users(id)
                            )''')
            conn.commit()
        conn.close()
    except Error as e:
        print(f"Error: {e}")

init_db()
@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="dark:bg-gray-900">
    
  

<nav class="bg-white border-gray-200 dark:bg-gray-900">
  <div class="max-w-screen-xl flex flex-wrap items-center justify-between mx-auto p-4">
    <a href="https://flowbite.com/" class="flex items-center space-x-3 rtl:space-x-reverse">
      
        <span class="self-center text-2xl font-semibold whitespace-nowrap dark:text-white">Restra Predict</span>
    </a>
    <button data-collapse-toggle="navbar-default" type="button" class="inline-flex items-center p-2 w-10 h-10 justify-center text-sm text-gray-500 rounded-lg md:hidden hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-200 dark:text-gray-400 dark:hover:bg-gray-700 dark:focus:ring-gray-600" aria-controls="navbar-default" aria-expanded="false">
        <span class="sr-only">Open main menu</span>
        <svg class="w-5 h-5" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 17 14">
            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M1 1h15M1 7h15M1 13h15"/>
        </svg>
    </button>
    <div class="hidden w-full md:block md:w-auto" id="navbar-default">
      <ul class="font-medium flex flex-col p-4 md:p-0 mt-4 border border-gray-100 rounded-lg bg-gray-50 md:flex-row md:space-x-8 rtl:space-x-reverse md:mt-0 md:border-0 md:bg-white dark:bg-gray-800 md:dark:bg-gray-900 dark:border-gray-700">
        <li>
          <a href="/" class="block py-2 px-3 text-white bg-blue-700 rounded md:bg-transparent md:text-blue-700 md:p-0 dark:text-white md:dark:text-blue-500" aria-current="page">Home</a>
        </li>
        <li>
          <a href="/predict" class="block py-2 px-3 text-gray-900 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 md:p-0 dark:text-white md:dark:hover:text-blue-500 dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent">Predict</a>
        </li>
        <li>
          <a href="/new_user" class="block py-2 px-3 text-gray-900 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 md:p-0 dark:text-white md:dark:hover:text-blue-500 dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent">Add New User</a>
        </li>
         <li>
          <a href="/update_user" class="block py-2 px-3 text-gray-900 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 md:p-0 dark:text-white md:dark:hover:text-blue-500 dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent" aria-current="page">Update User</a>
        </li>
        <li>
        <li>
          <a href="/user" class="block py-2 px-3 text-gray-900 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 md:p-0 dark:text-white md:dark:hover:text-blue-500 dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent">View User</a>
        </li>
        <li>
          <a href="/add_order" class="block py-2 px-3 text-gray-900 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 md:p-0 dark:text-white md:dark:hover:text-blue-500 dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent">Add Order</a>
        </li>
      </ul>
    </div>
  </div>
</nav>



</body>
</html>
'''
@app.route('/predict', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        data = request.json
        img_data = data['image'].split(',')[1]
        nparr = np.frombuffer(base64.b64decode(img_data), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        # user_dir = os.path.join('temp')
        # os.makedirs(user_dir, exist_ok=True)

        # Save photos and store the first one in the database

        
        # photo_data = base64.b64decode(img_data)
           
        # with open(os.path.join(user_dir, f'photo_.jpg'), 'wb') as f:
        #         f.write(photo_data)
        try:

            predictions = DeepFace.find(img_path=img, db_path="trainss", model_name="Facenet512")
            face = DeepFace.analyze(img, ['emotion'])

            if not predictions[0].empty and predictions[0].distance[0] < 0.3:
                identity = predictions[0].identity[0].split("/")[1]
                conn = mysql.connector.connect(
                    host='sql12.freesqldatabase.com',
                    user='sql12713824',
                    password='ds6QqFFFZ6',
                    database='sql12713824'
                )
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM users WHERE username = %s", (identity,))
                userids = cursor.fetchone()
                if userids:
                    user_id=userids[0]
                    cursor.execute("""
                            INSERT INTO visits (user_id, visit_timestamp)
                              VALUES (%s, NOW())
                               ON DUPLICATE KEY UPDATE visit_timestamp = NOW()
                              """, (user_id,))

                    conn.commit()

                




                # conn = sqlite3.connect('users.db')
                # c = conn.cursor()
                # c.execute("SELECT id, username FROM users WHERE username = ?", (identity,))
                # user = c.fetchone()
                # conn.close()

                # response = {
                #     'id': user[0],
                #     'username': user[1],
                #     'emotion': face[0]["dominant_emotion"]
                # }


                response={"Name":identity, 'emotion': face[0]["dominant_emotion"]}
            else:
                response = {'prediction': 'unknown User'}
            cursor.close()
            conn.close()
        except Exception as e:
            response = {'status': 'error', 'message': str(e)}
        print(response)
        
        return jsonify(response)

    return """
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    
    <div class="grid sm:grid-cols-12 place-items-stretch gap-1 ">
        <div class="col-span-8">
          <video id="video" width="100%" autoplay></video>
          <canvas id="canvas" width="640" height="480" style="display:none;"></canvas>
        </div>
        <div class="col-span-4">

            <div class="flex h-screen">
                <div  class="m-auto">
                    <h1>prediction: </h1>
                    <h1>Name :<span id="Name"> </span></h1>
                    <h1>Emotion : <span id="Emotion" ></span></h1>
                    <h1>Error : <span id="err"></span></h1>
                </div>
              </div>
          
        </div>
        <p id="prediction"></p>
</div>
    <script>
        const video = document.getElementById('video');
        const canvas = document.getElementById('canvas');
        const predictionDiv = document.getElementById('prediction');
        const pname=document.getElementById('Name')
        const pemotion=document.getElementById('Emotion')
        const errors=document.getElementById('err');
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
            const response = await fetch('https://crispy-carnival-w456g5q7pq5fv9g4-5000.app.github.dev/predict', {
                method: 'POST',
                body: JSON.stringify({ image: imageData }),
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            const result = await response.json();
 
            predictionDiv.innerHTML = JSON.stringify(result);
            
            if(result.prediction){
                console.log(result.status);
                pname.innerText = ""
                pemotion.innerText = ""
                errors.innerText = result.prediction
            }
            else if(result.status=="error"){
                
                pname.innerText = ""
                pemotion.innerText = ""
                errors.innerText = result.message
            }
            else{
                pname.innerText = result.Name
                pemotion.innerText = result.emotion
                errors.innerText = ""
            }
            

        }

        setInterval(captureAndPredict, 2000);

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
        # photo_datas = base64.b64decode(photos[0].split(',')[1])
        # with open(os.path.join(user_dir, 'photo_10.jpg'), 'wb') as f:
        #     f.write(photo_datas)
        # conn = sqlite3.connect('users.db')
        # c = conn.cursor()
        # print(photo_datas)
        # c.execute("INSERT INTO users (username) VALUES (?)", (username,))
        # conn.commit()
        # conn.close()
        try:
            photo_datas = base64.b64decode(photos[0].split(',')[1])
            with open(os.path.join(user_dir, 'photo_10.jpg'), 'wb') as f:
                f.write(photo_datas)
            conn = mysql.connector.connect(
                host='sql12.freesqldatabase.com',            user='sql12713824',
            password='ds6QqFFFZ6',   
            database='sql12713824'              )
            if conn.is_connected():
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (username,photo) VALUES (%s,%s)", (username,photo_datas))
                conn.commit()
            conn.close()
        except Error as e:
            return jsonify({'status': 'error', 'message': str(e)})
        return jsonify({'status': 'success', 'message': 'User data saved.'})

    else:
        return '''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <script src="https://cdn.tailwindcss.com"></script>
            </head>
            <body>
            <nav class="bg-white border-gray-200 dark:bg-gray-900">
  <div class="max-w-screen-xl flex flex-wrap items-center justify-between mx-auto p-4">
    <a href="https://flowbite.com/" class="flex items-center space-x-3 rtl:space-x-reverse">
      
        <span class="self-center text-2xl font-semibold whitespace-nowrap dark:text-white">Restra Predict</span>
    </a>
    <button data-collapse-toggle="navbar-default" type="button" class="inline-flex items-center p-2 w-10 h-10 justify-center text-sm text-gray-500 rounded-lg md:hidden hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-200 dark:text-gray-400 dark:hover:bg-gray-700 dark:focus:ring-gray-600" aria-controls="navbar-default" aria-expanded="false">
        <span class="sr-only">Open main menu</span>
        <svg class="w-5 h-5" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 17 14">
            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M1 1h15M1 7h15M1 13h15"/>
        </svg>
    </button>
    <div class="hidden w-full md:block md:w-auto" id="navbar-default">
      <ul class="font-medium flex flex-col p-4 md:p-0 mt-4 border border-gray-100 rounded-lg bg-gray-50 md:flex-row md:space-x-8 rtl:space-x-reverse md:mt-0 md:border-0 md:bg-white dark:bg-gray-800 md:dark:bg-gray-900 dark:border-gray-700">
        <li>
          <a href="/" class="block py-2 px-3 text-white bg-blue-700 rounded md:bg-transparent md:text-blue-700 md:p-0 dark:text-white md:dark:text-blue-500" aria-current="page">Home</a>
        </li>
        <li>
          <a href="/predict" class="block py-2 px-3 text-gray-900 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 md:p-0 dark:text-white md:dark:hover:text-blue-500 dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent">Predict</a>
        </li>
        <li>
          <a href="/new_user" class="block py-2 px-3 text-gray-900 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 md:p-0 dark:text-white md:dark:hover:text-blue-500 dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent">Add New User</a>
        </li>
        <li>
          <a href="/user" class="block py-2 px-3 text-gray-900 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 md:p-0 dark:text-white md:dark:hover:text-blue-500 dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent">View User</a>
        </li>
        <li>
          <a href="/add_order" class="block py-2 px-3 text-gray-900 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 md:p-0 dark:text-white md:dark:hover:text-blue-500 dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent">Add Order</a>
        </li>
      </ul>
    </div>
  </div>
</nav>
                <div class="dark:bg-gray-900 h-screen">

 <video class="bg-black items-center flex mx-auto "  id="video" width="640" height="480" autoplay></video>
               <div class="flex flex-col">
 <canvas id="canvas" width="640" height="480" style="display:none;"></canvas>
                <label class="items-center flex mx-auto my-2 text-gray-200">Name: <input  class="mx-2 p-1 border bg-slate-400 text-white" id="username" type="text"/></label>
                <button class="bg-blue-300 w-fit items-center flex mx-auto rounded-xl p-2" id="submitimage">Submit New Data</button>
               </div>

            <div class="items-center flex mx-auto w-fit p-4 m-4 text-sm text-red-800 rounded-lg bg-red-50 dark:bg-gray-800 dark:text-red-400" role="alert">
  <span id="res" class="font-medium"></span> 

               
</div>
                <script>
                    const video = document.getElementById('video');
                    const canvas = document.getElementById('canvas');
                    const submit = document.getElementById('submitimage');
                    const usernameInput = document.getElementById('username');
                    const ress=document.getElementById('res');
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
                            
                            ress.innerHTML = JSON.stringify(result.message, null, 2);
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
        print(fav_dish)
        try:
            conn = mysql.connector.connect(
                host='sql12.freesqldatabase.com',
            user='sql12713824',
            password='ds6QqFFFZ6',   
            database='sql12713824' 
            )
            if conn.is_connected():
                cursor = conn.cursor()

                if order_details:
                    cursor.execute("INSERT INTO orders (user_id, order_details, fav_dish) VALUES (%s, %s)", (user_id, order_details, fav_dish))
                    cursor.execute("UPDATE users SET order_count = order_count + 1 WHERE id = %s", (user_id,))

                if fav_dish:
                    cursor.execute("UPDATE users SET fav_dish = %s WHERE id = %s", (fav_dish, user_id))

                conn.commit()
            conn.close()
        except Error as e:
            return jsonify({'status': 'error', 'message': str(e)})

        return jsonify({'status': 'success', 'message': 'User data updated.'})
    else:
        return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body>
<nav class="bg-white border-gray-200 dark:bg-gray-900">
  <div class="max-w-screen-xl flex flex-wrap items-center justify-between mx-auto p-4">
    <a href="https://flowbite.com/" class="flex items-center space-x-3 rtl:space-x-reverse">
      
        <span class="self-center text-2xl font-semibold whitespace-nowrap dark:text-white">Restra Predict</span>
    </a>
    <button data-collapse-toggle="navbar-default" type="button" class="inline-flex items-center p-2 w-10 h-10 justify-center text-sm text-gray-500 rounded-lg md:hidden hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-200 dark:text-gray-400 dark:hover:bg-gray-700 dark:focus:ring-gray-600" aria-controls="navbar-default" aria-expanded="false">
        <span class="sr-only">Open main menu</span>
        <svg class="w-5 h-5" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 17 14">
            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M1 1h15M1 7h15M1 13h15"/>
        </svg>
    </button>
    <div class="hidden w-full md:block md:w-auto" id="navbar-default">
      <ul class="font-medium flex flex-col p-4 md:p-0 mt-4 border border-gray-100 rounded-lg bg-gray-50 md:flex-row md:space-x-8 rtl:space-x-reverse md:mt-0 md:border-0 md:bg-white dark:bg-gray-800 md:dark:bg-gray-900 dark:border-gray-700">
        <li>
          <a href="/" class="block py-2 px-3 text-white bg-blue-700 rounded md:bg-transparent md:text-blue-700 md:p-0 dark:text-white md:dark:text-blue-500" aria-current="page">Home</a>
        </li>
        <li>
          <a href="/predict" class="block py-2 px-3 text-gray-900 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 md:p-0 dark:text-white md:dark:hover:text-blue-500 dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent">Predict</a>
        </li>
        <li>
          <a href="/new_user" class="block py-2 px-3 text-gray-900 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 md:p-0 dark:text-white md:dark:hover:text-blue-500 dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent">Add New User</a>
        </li>
        <li>
          <a href="/user" class="block py-2 px-3 text-gray-900 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 md:p-0 dark:text-white md:dark:hover:text-blue-500 dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent">View User</a>
        </li>
        <li>
          <a href="/add_order" class="block py-2 px-3 text-gray-900 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 md:p-0 dark:text-white md:dark:hover:text-blue-500 dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent">Add Order</a>
        </li>
      </ul>
    </div>
  </div>
</nav>
  <div class="dark:bg-gray-900 h-screen justify-center items-center flex flex-col my-auto  ">

      <div class="flex flex-col mx-auto  gap-3"> 
           <label class="text-gray-300">ID :<input class="mx-2 ml-10 p-1 border bg-slate-400 text-white" id="id" type="text"/></label>
        <label class="text-gray-300">Order  :<input class="mx-2 ml-4 p-1 border bg-slate-400 text-white" id="order" type="text"/></label>
        <label class="text-gray-300">FavDish:<input class="mx-2 p-1 border bg-slate-400 text-white" id="fav_dish" type="text"/></label>
        <button  class="bg-blue-300 w-fit items-center flex mx-auto rounded-xl p-2" onclick="addorder()">Submit New Data</button>

      </div>
</div>
     

 <script>
                function addorder() {
                console.log("calledmethod")
                    var id = document.getElementById('id').value;
                    var order = document.getElementById('order').value;
                    var fav_dish = document.getElementById('fav_dish').value;

                    fetch('/update_user', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({id: id, order: order, fav_dish:fav_dish})
                    }).then(response => response.json())
                      .then(data => alert(data.message));
                };
            </script>


        
    </body>
    </html>
    """



@app.route('/user/<int:user_id>', methods=['GET','POST'])
def get_user(user_id):
    if request.method == 'POST':
        try:
            conn = mysql.connector.connect(
                host='sql12.freesqldatabase.com',            user='sql12713824',
            password='ds6QqFFFZ6',   
            database='sql12713824'             )
            if conn.is_connected():
                cursor = conn.cursor()
                cursor.execute("SELECT username, order_count, fav_dish, photo FROM users WHERE id = %s", (user_id,))
                user = cursor.fetchone()

                if user is None:
                    return jsonify({'status': 'error', 'message': 'User not found'})

                cursor.execute("SELECT order_details FROM orders WHERE user_id = %s ORDER BY id DESC LIMIT 10", (user_id,))
                orders = [order[0] for order in cursor.fetchall()]

                conn.close()
                img_base64 = base64.b64encode(user[3]).decode('utf-8')

                return jsonify({
                    'username': user[0],
                    'order_count': user[1],
                    'fav_dish': user[2],
                    'last_10_orders': orders,
                    'userphoto': img_base64
                })
        except Error as e:
            return jsonify({'status': 'error', 'message': str(e)})

    else:
       return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body>
    <nav class="bg-white border-gray-200 dark:bg-gray-900">
  <div class="max-w-screen-xl flex flex-wrap items-center justify-between mx-auto p-4">
    <a href="https://flowbite.com/" class="flex items-center space-x-3 rtl:space-x-reverse">
      
        <span class="self-center text-2xl font-semibold whitespace-nowrap dark:text-white">Restra Predict</span>
    </a>
    <button data-collapse-toggle="navbar-default" type="button" class="inline-flex items-center p-2 w-10 h-10 justify-center text-sm text-gray-500 rounded-lg md:hidden hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-200 dark:text-gray-400 dark:hover:bg-gray-700 dark:focus:ring-gray-600" aria-controls="navbar-default" aria-expanded="false">
        <span class="sr-only">Open main menu</span>
        <svg class="w-5 h-5" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 17 14">
            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M1 1h15M1 7h15M1 13h15"/>
        </svg>
    </button>
    <div class="hidden w-full md:block md:w-auto" id="navbar-default">
      <ul class="font-medium flex flex-col p-4 md:p-0 mt-4 border border-gray-100 rounded-lg bg-gray-50 md:flex-row md:space-x-8 rtl:space-x-reverse md:mt-0 md:border-0 md:bg-white dark:bg-gray-800 md:dark:bg-gray-900 dark:border-gray-700">
        <li>
          <a href="/" class="block py-2 px-3 text-white bg-blue-700 rounded md:bg-transparent md:text-blue-700 md:p-0 dark:text-white md:dark:text-blue-500" aria-current="page">Home</a>
        </li>
        <li>
          <a href="/predict" class="block py-2 px-3 text-gray-900 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 md:p-0 dark:text-white md:dark:hover:text-blue-500 dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent">Predict</a>
        </li>
        <li>
          <a href="/new_user" class="block py-2 px-3 text-gray-900 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 md:p-0 dark:text-white md:dark:hover:text-blue-500 dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent">Add New User</a>
        </li>
        <li>
          <a href="/user" class="block py-2 px-3 text-gray-900 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 md:p-0 dark:text-white md:dark:hover:text-blue-500 dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent">View User</a>
        </li>
        <li>
          <a href="/add_order" class="block py-2 px-3 text-gray-900 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 md:p-0 dark:text-white md:dark:hover:text-blue-500 dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent">Add Order</a>
        </li>
      </ul>
    </div>
  </div>
</nav>

        <div class="dark:bg-gray-900 h-screen justify-center items-center flex flex-col my-auto  ">

      <div class="flex flex-col mx-auto  gap-3"> 
        

    <div id="user-info" class="text-gray-200" >
             <img  id="user-image" width="200" height="200"  >
        <p  id="username"></p>
        <p id="order-count"></p>
        <p id="fav-dish"></p>
        <p id="last-orders"></p>
         <p id="error"></p>

    </div>

      </div>
</div>
        <script>
            
            const predictionDiv = document.getElementById('prediction');
            var id = window.location.href.split("/").pop().split("?")[0];
            const errors = document.getElementById('error');

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
                 if(result.status!='error'){
                const userData=result
                      document.getElementById("username").textContent = "Customer Name: " + userData.username;
        document.getElementById("order-count").textContent = "Order Count: " + userData.order_count;
        document.getElementById("fav-dish").textContent = "Favorite Dish: " + userData.fav_dish;
        document.getElementById("last-orders").textContent = "Last 10 Orders: " + userData.last_10_orders.join(", ");

        // Set user image
        const imgElem = document.getElementById("user-image");
        imgElem.src = "data:image/jpeg;base64," + userData.userphoto;
}
else{
 errors.textContent = "No User Found"
 var img = document.getElementById('user-image');
    img.style.visibility = 'hidden';
}
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

        try:
            conn = mysql.connector.connect(
                host='sql12.freesqldatabase.com',            user='sql12713824',
            password='ds6QqFFFZ6',   
            database='sql12713824'             )
            if conn.is_connected():
                cursor = conn.cursor()
                cursor.execute("INSERT INTO orders (user_id, order_details) VALUES (%s, %s)", (user_id, order_details))
                cursor.execute("UPDATE users SET order_count = order_count + 1 WHERE id = %s", (user_id,))
                conn.commit()
            conn.close()
        except Error as e:
            return jsonify({'status': 'error', 'message': str(e)})

        return jsonify({'status': 'success', 'message': 'Order added successfully.'})
    else:
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body>
        <nav class="bg-white border-gray-200 dark:bg-gray-900">
  <div class="max-w-screen-xl flex flex-wrap items-center justify-between mx-auto p-4">
    <a href="https://flowbite.com/" class="flex items-center space-x-3 rtl:space-x-reverse">
      
        <span class="self-center text-2xl font-semibold whitespace-nowrap dark:text-white">Restra Predict</span>
    </a>
    <button data-collapse-toggle="navbar-default" type="button" class="inline-flex items-center p-2 w-10 h-10 justify-center text-sm text-gray-500 rounded-lg md:hidden hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-200 dark:text-gray-400 dark:hover:bg-gray-700 dark:focus:ring-gray-600" aria-controls="navbar-default" aria-expanded="false">
        <span class="sr-only">Open main menu</span>
        <svg class="w-5 h-5" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 17 14">
            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M1 1h15M1 7h15M1 13h15"/>
        </svg>
    </button>
    <div class="hidden w-full md:block md:w-auto" id="navbar-default">
      <ul class="font-medium flex flex-col p-4 md:p-0 mt-4 border border-gray-100 rounded-lg bg-gray-50 md:flex-row md:space-x-8 rtl:space-x-reverse md:mt-0 md:border-0 md:bg-white dark:bg-gray-800 md:dark:bg-gray-900 dark:border-gray-700">
        <li>
          <a href="/" class="block py-2 px-3 text-white bg-blue-700 rounded md:bg-transparent md:text-blue-700 md:p-0 dark:text-white md:dark:text-blue-500" aria-current="page">Home</a>
        </li>
        <li>
          <a href="/predict" class="block py-2 px-3 text-gray-900 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 md:p-0 dark:text-white md:dark:hover:text-blue-500 dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent">Predict</a>
        </li>
        <li>
          <a href="/new_user" class="block py-2 px-3 text-gray-900 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 md:p-0 dark:text-white md:dark:hover:text-blue-500 dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent">Add New User</a>
        </li>
        <li>
          <a href="/user" class="block py-2 px-3 text-gray-900 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 md:p-0 dark:text-white md:dark:hover:text-blue-500 dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent">View User</a>
        </li>
        <li>
          <a href="/add_order" class="block py-2 px-3 text-gray-900 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 md:p-0 dark:text-white md:dark:hover:text-blue-500 dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent">Add Order</a>
        </li>
      </ul>
    </div>
  </div>
</nav>
          <div class="dark:bg-gray-900 h-screen justify-center items-center flex flex-col my-auto  ">

      <div class="flex flex-col mx-auto  gap-3"> 
         


  <label class="text-gray-300">UserID: <input id="id" class="mx-2 p-1 border bg-slate-400 text-white" type="text"/></label>
            <label class="text-gray-300">Order : <input id="order" class="mx-2 p-1 border bg-slate-400 text-white" type="text"/></label>
            <button id="addorder"  class="bg-blue-300 w-fit items-center flex mx-auto rounded-xl p-2" >Add Order</button>
      </div>
</div>
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
@app.route('/clear_db', methods=['GET'])
def clear_db():
    try:
        conn = mysql.connector.connect(
host='sql12.freesqldatabase.com',            user='sql12713824',
            password='ds6QqFFFZ6',   
            database='sql12713824' 
 # Replace with your MySQL database name
        )
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS orders")
            cursor.execute("DROP TABLE IF EXISTS users")
            conn.commit()
            conn.close()
            return jsonify({'status': 'success', 'message': 'Database cleared successfully.'})
    except Error as e:
        return jsonify({'status': 'error', 'message': str(e)})
    

@app.route('/user')
def homes():
    return '''
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="dark:bg-gray-900">
    
  

<nav class="bg-white border-gray-200 dark:bg-gray-900">
  <div class="max-w-screen-xl flex flex-wrap items-center justify-between mx-auto p-4">
    <a href="https://flowbite.com/" class="flex items-center space-x-3 rtl:space-x-reverse">
      
        <span class="self-center text-2xl font-semibold whitespace-nowrap dark:text-white">Restra Predict</span>
    </a>
    <button data-collapse-toggle="navbar-default" type="button" class="inline-flex items-center p-2 w-10 h-10 justify-center text-sm text-gray-500 rounded-lg md:hidden hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-200 dark:text-gray-400 dark:hover:bg-gray-700 dark:focus:ring-gray-600" aria-controls="navbar-default" aria-expanded="false">
        <span class="sr-only">Open main menu</span>
        <svg class="w-5 h-5" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 17 14">
            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M1 1h15M1 7h15M1 13h15"/>
        </svg>
    </button>
    <div class="hidden w-full md:block md:w-auto" id="navbar-default">
      <ul class="font-medium flex flex-col p-4 md:p-0 mt-4 border border-gray-100 rounded-lg bg-gray-50 md:flex-row md:space-x-8 rtl:space-x-reverse md:mt-0 md:border-0 md:bg-white dark:bg-gray-800 md:dark:bg-gray-900 dark:border-gray-700">
        <li>
          <a href="/" class="block py-2 px-3 text-white bg-blue-700 rounded md:bg-transparent md:text-blue-700 md:p-0 dark:text-white md:dark:text-blue-500" aria-current="page">Home</a>
        </li>
        <li>
          <a href="/predict" class="block py-2 px-3 text-gray-900 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 md:p-0 dark:text-white md:dark:hover:text-blue-500 dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent">Predict</a>
        </li>
        <li>
          <a href="/new_user" class="block py-2 px-3 text-gray-900 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 md:p-0 dark:text-white md:dark:hover:text-blue-500 dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent">Add New User</a>
        </li>
        <li>
          <a href="/user" class="block py-2 px-3 text-gray-900 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 md:p-0 dark:text-white md:dark:hover:text-blue-500 dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent">View User</a>
        </li>
        <li>
          <a href="/add_order" class="block py-2 px-3 text-gray-900 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 md:p-0 dark:text-white md:dark:hover:text-blue-500 dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent">Add Order</a>
        </li>
      </ul>
    </div>
  </div>
</nav>

 <div class="dark:bg-gray-900 h-screen justify-center items-center flex flex-col my-auto  ">

      <div class="flex flex-col mx-auto  gap-3"> 
           <label class="text-gray-300">ID :<input class="mx-2 ml-10 p-1 border bg-slate-400 text-white" id="id" type="text"/></label>
      
        <button onclick="send()"  class="bg-blue-300 w-fit items-center flex mx-auto rounded-xl p-2" id="updatedata">View User Data</button>
    <script>
function send(){
   var id = document.getElementById('id').value;
  
    window.location.href =  
                `https://crispy-carnival-w456g5q7pq5fv9g4-5000.app.github.dev/user/${id}`; 
}
      </script>
      </div>

</div>

</body>
</html>
'''

@app.route('/today_user',methods=['GET', 'POST'])
def get_today_users():
    if request.method == 'POST':

      try:
          # Connect to MySQL database
          conn = mysql.connector.connect(
              host='sql12.freesqldatabase.com',
              user='sql12713824',
              password='ds6QqFFFZ6',
              database='sql12713824'
          )
          cursor = conn.cursor()

          # Calculate timestamp 3 hours ago
          three_hours_ago = datetime.now() - timedelta(hours=3)
          # cursor.execute("TRUNCATE TABLE visits;")
          # cursor.execute("DROP TABLE IF EXISTS visits")
          # # Commit the transaction
          # conn.commit()


          # SQL query to get users who visited in the last 3 hours
          query = """
          select * from visits
          """
          cursor.execute(query)
          
          users = cursor.fetchall()
          

          # Fetch all results
          
          print(users)
          # Close connection
          conn.close()

          
          # response = []
          # for user in users:
          #     user_data = {
          #         'username': user[0],
          #         'visit_timestamp': user[1].strftime('%Y-%m-%d %H:%M:%S')
          #     }
          #     response.append(response)

          return jsonify(users)

      except Error as e:
          return jsonify({'error': str(e)})

      return jsonify([])  # Return empty list if no users found
    else:
        return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body>
    <nav class="bg-white border-gray-200 dark:bg-gray-900">
  <div class="max-w-screen-xl flex flex-wrap items-center justify-between mx-auto p-4">
    <a href="https://flowbite.com/" class="flex items-center space-x-3 rtl:space-x-reverse">
      
        <span class="self-center text-2xl font-semibold whitespace-nowrap dark:text-white">Restra Predict</span>
    </a>
    <button data-collapse-toggle="navbar-default" type="button" class="inline-flex items-center p-2 w-10 h-10 justify-center text-sm text-gray-500 rounded-lg md:hidden hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-200 dark:text-gray-400 dark:hover:bg-gray-700 dark:focus:ring-gray-600" aria-controls="navbar-default" aria-expanded="false">
        <span class="sr-only">Open main menu</span>
        <svg class="w-5 h-5" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 17 14">
            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M1 1h15M1 7h15M1 13h15"/>
        </svg>
    </button>
    <div class="hidden w-full md:block md:w-auto" id="navbar-default">
      <ul class="font-medium flex flex-col p-4 md:p-0 mt-4 border border-gray-100 rounded-lg bg-gray-50 md:flex-row md:space-x-8 rtl:space-x-reverse md:mt-0 md:border-0 md:bg-white dark:bg-gray-800 md:dark:bg-gray-900 dark:border-gray-700">
        <li>
          <a href="/" class="block py-2 px-3 text-white bg-blue-700 rounded md:bg-transparent md:text-blue-700 md:p-0 dark:text-white md:dark:text-blue-500" aria-current="page">Home</a>
        </li>
        <li>
          <a href="/predict" class="block py-2 px-3 text-gray-900 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 md:p-0 dark:text-white md:dark:hover:text-blue-500 dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent">Predict</a>
        </li>
        <li>
          <a href="/new_user" class="block py-2 px-3 text-gray-900 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 md:p-0 dark:text-white md:dark:hover:text-blue-500 dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent">Add New User</a>
        </li>
        <li>
          <a href="/user" class="block py-2 px-3 text-gray-900 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 md:p-0 dark:text-white md:dark:hover:text-blue-500 dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent">View User</a>
        </li>
        <li>
          <a href="/add_order" class="block py-2 px-3 text-gray-900 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 md:p-0 dark:text-white md:dark:hover:text-blue-500 dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent">Add Order</a>
        </li>
      </ul>
    </div>
  </div>
</nav>

        <div class="dark:bg-gray-900 h-screen justify-center items-center flex flex-col my-auto  ">

      <div class="flex flex-col mx-auto  gap-3"> 
        

    <div id="user-info" class="text-gray-200" >
          <div id="users-list">
            <!-- Users data will be rendered here -->
        </div>

    </div>

      </div>
</div>
        <script>
            
            const predictionDiv = document.getElementById('prediction');
            var id = window.location.href.split("/").pop().split("?")[0];
            const errors = document.getElementById('error');

            async function captureAndPredict() {


                console.log(id)
                const response = await fetch(`/today_user`, {
                    method: 'POST',

                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                const data = await response.json();
                 console.log(data)
                             const usersList = document.getElementById('users-list');
            usersList.innerHTML = ''; // Clear previous content

            data.forEach(user => {
                const userElement = document.createElement('div');
                userElement.classList.add('user');
                const sr = user[0];
                const userId = user[1];
                const date = user[2];
                const link = `/user/${userId}`;

                userElement.innerHTML = `
                    <strong>SR:</strong> ${sr}, 
                    <strong>User ID:</strong> ${userId}, 
                    <strong>Date:</strong> ${date}, 
                    <a href="${link}">View Details</a>
                `;

                usersList.appendChild(userElement);
            });

            }

            captureAndPredict()


        </script>
    </body>
    </html>
'''



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

from flask import Flask, request, render_template, jsonify
import requests
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Bitrix24 Configuration
BASE_URL = "https://agrovisiongroup.bitrix24.in/rest/"
USER_ID = "1853"
AUTH_TOKEN = "gyfdo6xxmnphedml"

# BASE_URL = "https://agrovisiongroup.bitrix24.in/rest"
# USER_ID = "1853"
# AUTH_TOKEN = "jgyfdo6xxmnphedml"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/button1')
def button1():
    return render_template('button1.html')

@app.route('/create-task', methods=['POST'])
def create_task():
    title = request.form['title']
    description = request.form['description']
    responsible_id = request.form['responsible_id']

    if not title or not responsible_id:
        return jsonify({"success": False, "error": "Title and Responsible ID are required"}), 400

    url = f"{BASE_URL}/{USER_ID}/{AUTH_TOKEN}/tasks.task.add.json"
    payload = {
        "fields": {
            "TITLE": title,
            "DESCRIPTION": description,
            "RESPONSIBLE_ID": responsible_id
        }
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return jsonify({"success": True, "data": response.json()})
    else:
        return jsonify({"success": False, "error": response.text}), response.status_code

@app.route('/button2')
def button2():
    return render_template('button2.html')

@app.route('/update-task', methods=['POST'])
def update_task():
    task_id = request.form.get('task_id')
    title = request.form.get('title')
    description = request.form.get('description', '')

    if not task_id or not title:
        return jsonify({"success": False, "error": "Task ID and Title are required"}), 400

    url = f"{BASE_URL}/{USER_ID}/{AUTH_TOKEN}/tasks.task.update.json"
    payload = {
        "taskId": task_id,
        "fields": {
            "TITLE": title,
            "DESCRIPTION": description
        }
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return jsonify({"success": True, "data": response.json()})
    else:
        return jsonify({"success": False, "error": response.text}), response.status_code


@app.route('/button3', methods=['GET', 'POST'])
def button3():
    if request.method == 'POST':
        task_id = request.form['task_id']
        url = f"{BASE_URL}/{USER_ID}/{AUTH_TOKEN}/tasks.task.get.json"
        params = {'taskId': task_id}
        response = requests.get(url, params=params)
        if response.status_code == 200:
            task_data = response.json().get('result', {}).get('task', {})
            return render_template('button3.html', task=task_data, error=None)
        else:
            error_message = "Failed to retrieve task data. " + response.json().get('error_description', 'No additional error info provided.')
            return render_template('button3.html', task=None, error=error_message)
    return render_template('button3.html', task=None, error=None)


@app.route('/button4')
def button4():
    url = f"{BASE_URL}/{USER_ID}/{AUTH_TOKEN}/tasks.task.list.json"
    response = requests.get(url)
    if response.status_code == 200:
        tasks_data = response.json().get('result', {}).get('tasks', [])
        tasks = []
        for task in tasks_data:
            status = task.get('status')
            if isinstance(status, dict):
                status_name = status.get('name', 'N/A')
            else:
                status_name = status or 'N/A'  # Default to 'N/A' if status is None or not provided
            formatted_task = {
                'ID': task.get('id'),
                'TITLE': task.get('title'),
                'STATUS': status_name
            }
            tasks.append(formatted_task)
        return render_template('button4.html', tasks=tasks)
    else:
        error_message = "Failed to retrieve tasks. Error: " + str(response.status_code)
        return render_template('button4.html', tasks=None, error=error_message)

@app.route('/button5', methods=['GET', 'POST'])
def complete_task():
    if request.method == 'POST':
        task_id = request.json.get('task_id')
        if task_id:
            # API URL to mark the task as completed
            url = f"{BASE_URL}/{USER_ID}/{AUTH_TOKEN}/task.item.complete"
            
            # Data to send to the API
            data = {
                'TASKID': task_id
            }

            try:
                # Send a POST request to Bitrix24 API to mark the task as completed
                response = requests.post(url, json=data)
                
                # Log the response status code and body for debugging
                print("Response Status Code:", response.status_code)
                print("Response Text:", response.text)
                
                # If status code is 200, parse the JSON response
                if response.status_code == 200:
                    result = response.json()
                    print("API Response JSON:", result)  # Log the JSON response
                    if result.get('result'):
                        return jsonify({'success': True, 'message': f'Task {task_id} marked as completed successfully'})
                    else:
                        # Log and return more detailed error information from the API
                        error_details = result.get('error', 'Proceed')
                        return jsonify({'success': False, 'error': 'Task Completed Sucessfully', 'details': error_details})
                else:
                    # Log and return the response details when status is not 200
                    return jsonify({'success': False, 'error': 'Task Completed Sucessfully', 'details': response.text})

            except Exception as e:
                # Log the exception in case of failure
                print("Error:", str(e))
                return jsonify({'success': False, 'error': 'An error occurred while processing your request'})

        else:
            return jsonify({'success': False, 'error': 'Missing task ID'})

    # Render the button5.html page for GET requests
    return render_template('button5.html')

@app.route('/button6', methods=['GET', 'POST'])
def add_comment():
    if request.method == 'POST':
        task_id = request.form.get('task_id')
        comment_text = request.form.get('comment')
        if task_id and comment_text:
            url = f"{BASE_URL}/{USER_ID}/{AUTH_TOKEN}/task.commentitem.add"  # Adjust the API endpoint if necessary
            data = {
                'TASKID': task_id,
                'FIELDS': {
                    'POST_MESSAGE': comment_text
                }
            }
            response = requests.post(url, json=data)
            if response.status_code == 200:
                return jsonify({'success': True, 'message': 'Comment added successfully'})
            else:
                return jsonify({'success': False, 'error': 'Failed to add comment', 'details': response.text})
        else:
            return jsonify({'success': False, 'error': 'Missing task ID or comment'})

    return render_template('button6.html') 

@app.route('/button7', methods=['GET', 'POST'])
def create_contact():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')

        if first_name and last_name and email and phone:
            url = f"{BASE_URL}/{USER_ID}/{AUTH_TOKEN}/crm.contact.add"
            data = {
                'fields': {
                    'NAME': first_name,
                    'LAST_NAME': last_name,
                    'EMAIL': [{'VALUE': email, 'VALUE_TYPE': 'WORK'}],
                    'PHONE': [{'VALUE': phone, 'VALUE_TYPE': 'WORK'}]
                }
            }
            response = requests.post(url, json=data)
            if response.status_code == 200 and 'result' in response.json():
                return jsonify({'success': True, 'message': 'Contact created successfully', 'contact_id': response.json()['result']})
            else:
                return jsonify({'success': False, 'error': 'Failed to create contact', 'details': response.text})
        else:
            return jsonify({'success': False, 'error': 'Missing required contact details'})
            
    return render_template('button7.html')

@app.route('/button8', methods=['GET', 'POST'])
def add_checklist_item():
    if request.method == 'POST':
        task_id = request.form.get('task_id')
        checklist_title = request.form.get('checklist_title')
        if task_id and checklist_title:
            url = f"{BASE_URL}/{USER_ID}/{AUTH_TOKEN}/task.checklistitem.add"
            data = {
                'TASKID': task_id,
                'FIELDS': {
                    
                    'TITLE': checklist_title                    
                }
            }
            response = requests.post(url, json=data)
            if response.status_code == 200 and response.json().get('result'):
                return jsonify({'success': True, 'message': 'Checklist item added successfully', 'item_id': response.json()['result']})
            else:
                return jsonify({'success': False, 'error': 'Failed to add checklist item', 'details': response.text})
        else:
            return jsonify({'success': False, 'error': 'Missing task ID or checklist title'})

    # If it's a GET request or if there's any other issue, display the form.
    return render_template('button8.html')

@app.route('/button9', methods=['GET', 'POST'])
def delegate_task():
    if request.method == 'POST':
        task_id = request.json.get('task_id')
        user_id = request.json.get('user_id')

        # Ensure both task_id and user_id are provided
        if task_id and user_id:
            # API URL to delegate the task
            url = f"{BASE_URL}/{USER_ID}/{AUTH_TOKEN}/task.item.delegate"
            
            # Data to send to the API
            data = {
                'TASKID': task_id,
                'USERID': user_id
            }

            try:
                # Send a POST request to Bitrix24 API to delegate the task
                response = requests.post(url, json=data)
                
                # Log the response status code and body for debugging
                print("Response Status Code:", response.status_code)
                print("Response Text:", response.text)

                # If status cod is 200, then parse the JSON Response
                if response.status_code == 200:
                    result = response.json()
                    print("API Response JSON:", result)  # Log the JSON response
                    if result.get('result'):
                        return jsonify({'success': True, 'message': f'Task {task_id} delegated successfully to User {user_id}'})
                    else:
                        # Capture any additional error message from Bitrix24 response
                        error_message = result.get('error', 'Proceed')
                        return jsonify({'success': False, 'error': 'Task Delegated:Sucess', 'details': error_message})
                else:
                    #If Status code is 200, capture the detailed response
                    return jsonify({'success': False, 'error': 'Task Delegated:Sucess', 'details': response.text})

            except requests.exceptions.RequestException as e:
                # catch any request errors and log details
                print("Request Exception:", str(e))
                return jsonify({'success': False, 'error': 'Task Delegated:Sucess', 'details': str(e)})

        else:
            return jsonify({'success': False, 'error': 'Missing task ID or user ID'})

    # Render the button9.html page for GET requests
    return render_template('button9.html')

@app.route('/button10', methods=['GET', 'POST'])
def attach_file_to_task():
    if request.method == 'POST':
        task_id = request.form.get('task_id')
        file_id = request.form.get('file_id')

        if task_id and file_id:
            # Prepare the URL to call the tasks.task.files.attach API
            url = f"{BASE_URL}/{USER_ID}/{AUTH_TOKEN}/tasks.task.files.attach"
            data = {
                'taskId': task_id,
                'fileId': file_id,
                'params': []  # Pass an empty array for params as per the API requirement
            }

            #call api to attach file
            response = requests.post(url, json=data)

            if response.status_code == 200:
                # Parse the response and return a success message
                result = response.json()
                return jsonify({'success': True, 'message': 'File attached successfully', 'result': result})
            else:
                #Handel faliure from bitrix24 api
                return jsonify({'success': False, 'error': 'Failed to attach file', 'details': response.text})
        else:
            return jsonify({'success': False, 'error': 'Missing task ID or file ID'})

    return render_template('button10.html')

@app.route('/button11', methods=['GET', 'POST'])
def get_storages():
    if request.method == 'POST':
        # Prepare the URL to call the disk.storage.getlist API
        url = f"{BASE_URL}/{USER_ID}/{AUTH_TOKEN}/disk.storage.getlist"
        
        # Call the API (We are passing an empty dictionary for 'filter' as no filters are required)
        response = requests.post(url, json={'filter': {}})
        
        if response.status_code == 200:
            # Print the raw response content to the terminal
            print("Raw response from Bitrix24 API:")
            print(response.text)  # This will print the raw response as a string

            # Parse the response (optional, if you still need to return data to the frontend)
            storages = response.json()

            return jsonify({'success': True, 'storages': storages})
        else:
            # Handle failure response from Bitrix24 API
            print(f"Failed to fetch storages. Error: {response.status_code}")
            return jsonify({'success': False, 'error': 'Failed to fetch storages', 'details': response.text})

    return render_template('button11.html')

@app.route('/button12', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        task_id = request.form.get('task_id')
        folder_id = request.form.get('folder_id')
        file = request.files.get('file')

        if task_id and folder_id and file:
            # Step 1: Call the disk.folder.uploadfile method to get the upload URL
            url = f"{BASE_URL}/{USER_ID}/{AUTH_TOKEN}/disk.folder.uploadfile"
            data = {
                'id': folder_id,
            }

            response = requests.post(url, data=data)
            if response.status_code == 200:
                upload_url = response.json().get('result', {}).get('uploadUrl')
                field = response.json().get('result', {}).get('field')

                if upload_url and field:
                    # Step 2: Upload the file to the obtained uploadUrl
                    files = {
                        field: (file.filename, file.stream, file.content_type)
                    }

                    upload_response = requests.post(upload_url, files=files)
                    if upload_response.status_code == 200:
                        upload_result = upload_response.json()
                        file_id = upload_result.get('result', {}).get('ID')
                        download_url = upload_result.get('result', {}).get('DOWNLOAD_URL')

                        return jsonify({
                            'success': True,
                            'message': 'File uploaded successfully.',
                            'file_id': file_id,
                            'download_url': download_url
                        })
                    else:
                        return jsonify({'success': False, 'error': 'Failed to upload file to the folder', 'details': upload_response.text})
                else:
                    return jsonify({'success': False, 'error': 'Failed to get upload URL', 'details': response.text})
            else:
                return jsonify({'success': False, 'error': 'Failed to get upload URL', 'details': response.text})
        else:
            return jsonify({'success': False, 'error': 'Missing required fields (task_id, folder_id, file)'})

    return render_template('button12.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Placeholder logic for authentication
        if username == 'admin' and password == 'password':  # Replace with your authentication logic
            return render_template('welcome.html', username=username, show_popup=True)
        else:
            return render_template('login.html', error="Invalid username or password.")
        
    return render_template('login.html')

task_data_store = []

# Webhook Route
@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    global task_data_store

    if request.method == 'POST':
        try:
            # Parse incoming Bitrix webhook payload
            data = request.json
            if not data:
                logging.error("No data received in POST request.")
                return jsonify({"message": "Invalid payload: No data received"}), 400

            # Extract task ID from the payload
            event_name = data.get('event', 'No Event Name Provided')
            fields_after = data.get('data', {}).get('FIELDS_AFTER', {})
            task_id = fields_after.get('ID')

            if not task_id:
                logging.error("No Task ID found in payload.")
                return jsonify({"message": "Task ID not found in payload"}), 400

            logging.info(f"Received Event: {event_name}, Task ID: {task_id}")

            # Fetch task details using inbound webhook
            inbound_webhook_url = f"https://b24-77nw8f.bitrix24.in/rest/1/gmfydo0ziujqry9f/task.item.getdata?taskId={task_id}"
            
            response = requests.get(inbound_webhook_url)

            if response.status_code == 200:
                task_details = response.json().get('result', {})
                logging.info(f"Task Details Retrieved: {task_details}")

                # Store task details for displaying on the web page
                task_data_store.append(task_details)
                return jsonify({"message": "Task details fetched successfully"}), 200
            else:
                logging.error(f"Failed to fetch task details: {response.text}")
                return jsonify({"message": "Failed to fetch task details"}), response.status_code

        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            return jsonify({"message": "Internal server error"}), 500

    # Render the task details on the web page
    return render_template('tasks.html', tasks=task_data_store)


if __name__ == '__main__':
    app.run(debug=True)

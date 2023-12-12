import requests
from flask import Flask, request, jsonify,render_template
import traceback
import json
from flask_cors import CORS
from urllib.parse import urlencode
import base64
app = Flask(__name__)
CORS(app)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/make_request', methods=['POST'])
def make_request():
    try:
        if 'multipart/form-data'in request.headers.get('Content-Type'):
            url = request.form.get('url')
            method = request.form.get('method', 'GET')
            headers = json.loads(request.form.get('headers', '{}'))
            params = json.loads(request.form.get('params', '{}'))
            data_body = json.loads(request.form.get('data', '{}'))
            authentication = json.loads(request.form.get('auth', '{}'))
            print(authentication)
            # auth = request.authorization
            if "Bearer Token" in authentication:
                headers['Authorization'] = f"Bearer {authentication['Bearer Token']}"
            elif "Basic Auth" in authentication:
                auth_data = json.loads(authentication['Basic Auth'])
                username = auth_data['Username']
                password = auth_data['Password']
                credentials = f"{username}:{password}"
                encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

                headers['Authorization'] = f"Basic {encoded_credentials}"

            # Use request.files to get the file
            if 'Content-Type' in headers:
                if headers['Content-Type']=='application/x-www-form-urlencoded':
                    data_body = urlencode(data_body)

            if request.files.get('file') is not None:
                file = request.files['file']
                files = {'file': (file.filename, file.stream, file.content_type)}
            else:
                files = None
            
            # Use the requests library to send a multipart/form-data request
            if method == 'POST':
                headers['X-Forwarded-For'] = '8.213.34.174'         
                response = requests.post(url,data=data_body, params=params, files=files)
                client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
                # print(response.text)
                print(client_ip)
            elif method == 'GET':
                headers['X-Forwarded-For'] = '8.213.34.174'         
                response = requests.get(url,data=data_body, params=params, files=files)
                client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
                print(client_ip)
                # print(response.text)

        else:
            # For raw json type
            data = request.get_json(force=True)  # Ensure content type is treated as JSON
            url = data.get('url')
            method = data.get('method', 'GET')
            headers = data.get('headers', {})
            params = data.get('params', {})
            data_body = data.get('data', None)
            auth = data.get('auth', None)

            if auth and 'Authorization' in auth:
                auth = json.loads(auth)
                headers['Authorization'] = f"Bearer {auth['Authorization'][7:]}"
                auth = ("Bearer", auth['Authorization'][7:])
                # print(auth)
            elif auth and 'username'  in auth:
                auth = auth=(auth['username'], auth['password'])
            if data_body:
                data_body = json.loads(data_body)
            else:
                # print('scenario 2')
                data_body = {}

            
            # If 'file' is present in data_body, construct the files parameter
            files = None
            if headers:
                if headers['Content-Type']=='application/x-www-form-urlencoded':
                    data_body = urlencode(data_body)
            else:
                if data_body and 'file' in data_body:
                    # data_body = json.loads(data_body)

                    # files = [
                    #     ('file',(data_body['file'] open(data_body['file'], 'rb'),'image/jpeg'))
                    # ]
                    files=[('file',(data_body['file'],open(data_body['file'],'rb'),'image/jpeg'))]
                    del data_body['file']  # Remove 'file' from data_body since it's now handled by 'files'
            # Use the requests library to send a multipart/form-data request
            if method == 'POST':
                # print(data_body) 
                headers['X-Forwarded-For'] = '8.213.34.174'         
                response = requests.post(url, headers=headers, params=params, data=data_body, files=files, auth=auth)
            elif method == 'GET':
                headers['X-Forwarded-For'] = '8.213.34.174'         
                # print(headers)
                response = requests.get(url, headers=headers, params=params,data=data_body, files=files, auth=auth)

        
        # Return response details as JSON
        print("request_url", response.request.url)
        print("request_method",response.request.method)
        print("request_headers", dict(response.request.headers))
        print("request_body", response.request.body)
        print("response_status_code", response.status_code)
        print("response_headers", dict(response.headers))
        print("response_content", response.content)
        print("response_content", 'success')
        # print("response_content", response.json())

        if 'Content-Type' in dict(response.headers):
            if "application/json" in dict(response.headers)['Content-Type']:
                response_content = response.json()
            elif "text/html; charset=utf-8" in dict(response.headers)['Content-Type']:
                response_content = response.text
            else:
                response_content = response.content
                try:
                    # Attempt to decode as JSON
                    json_content = json.loads(response_content)
                    print("JSON Content:")
                    print(json_content)
                except json.JSONDecodeError:
                    # If decoding as JSON fails, treat it as plain text
                    text_content = response_content.decode('utf-8')
                    print("Text Content:")
                    print(text_content)

            

        return {
            # "request_url": response.request.url,
            # "request_method": response.request.method,
            # "request_headers": dict(response.request.headers),
            # "request_body": response.request.body,
            # "response_status_code": response.status_code,
            "response_headers": dict(response.headers),
            "response_content": response_content,
            "server_url":client_ip
            # "response_content": response.content()
            # "response_content": 'success'
        }

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=80)

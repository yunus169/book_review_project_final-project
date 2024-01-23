from flask import Flask, jsonify, request
import json

app = Flask(__name__)

def read_tasks():
    with open('tasks.json', 'r') as file:
        return json.load(file)

def write_tasks(tasks):
    with open('tasks.json', 'w') as file:
        json.dump(tasks, file, indent=4)

@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = read_tasks()
    completed = request.args.get('completed')
    if completed:
        completed = completed.lower() == 'true'
        tasks = [task for task in tasks if task['completed'] == completed]
    return jsonify(tasks)

@app.route('/tasks', methods=['POST'])
def add_task():
    tasks = read_tasks()
    new_task = request.json
    new_task['id'] = max(task['id'] for task in tasks) + 1
    new_task['completed'] = False
    tasks.append(new_task)
    write_tasks(tasks)
    return jsonify(new_task), 201

@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    tasks = read_tasks()
    task = next((task for task in tasks if task['id'] == task_id), None)
    return jsonify(task) if task else ('', 404)

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    tasks = read_tasks()
    tasks = [task for task in tasks if task['id'] != task_id]
    write_tasks(tasks)
    return '', 204

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    tasks = read_tasks()
    task = next((task for task in tasks if task['id'] == task_id), None)
    if not task:
        return '', 404
    update_data = request.json
    task.update(update_data)
    write_tasks(tasks)
    return jsonify(task)

@app.route('/tasks/<int:task_id>/complete', methods=['PUT'])
def complete_task(task_id):
    tasks = read_tasks()
    task = next((task for task in tasks if task['id'] == task_id), None)
    if not task:
        return '', 404
    task['completed'] = True
    write_tasks(tasks)
    return jsonify(task)

@app.route('/tasks/categories/', methods=['GET'])
def get_categories():
    tasks = read_tasks()
    categories = set(task['category'] for task in tasks)
    return jsonify(list(categories))

@app.route('/tasks/categories/<category_name>', methods=['GET'])
def get_tasks_by_category(category_name):
    tasks = read_tasks()
    category_tasks = [task for task in tasks if task['category'] == category_name]
    return jsonify(category_tasks)

if __name__ == '__main__':
    app.run(debug=True)

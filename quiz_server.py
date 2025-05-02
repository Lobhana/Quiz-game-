import json
import os
import http.server
import socketserver
import webbrowser
from jinja2 import Template

# Ensure the script serves files from the correct directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Check if questions.json exists and is valid
questions_file = "questions.json"
if not os.path.exists(questions_file):
    print("Error: 'questions.json' file not found!")
    exit(1)

try:
    with open(questions_file, "r") as file:
        questions = json.load(file)
        if not questions:  # Check if the JSON is empty
            raise ValueError("Error: 'questions.json' is empty!")
except json.JSONDecodeError:
    print("Error: 'questions.json' is not a valid JSON file!")
    exit(1)
except ValueError as e:
    print(e)
    exit(1)

# Create an HTML template
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Quiz</title>
    <link rel="stylesheet" type="text/css" href="quiz_style.css">
    <script>
        function validateAnswers() {
            var form = document.forms[0];
            var questions = {{ questions|tojson|safe }};
            var score = 0;

            for (var i = 0; i < questions.length; i++)  {
                var questionNumber = i + 1;
                var selectedOption = form["q" + questionNumber + "_answer"];

                var isOptionSelected = false;
                for (var j = 0; j < selectedOption.length; j++) {
                    if (selectedOption[j].checked) {
                        isOptionSelected = true;
                        if (selectedOption[j].value == questions[i].answer) {
                            score++;
                        }
                        break;
                    }
                }

                if (!isOptionSelected) {
                    alert("Please select an option for question " + questionNumber);
                    return;
                }
            }

            alert("You scored " + score + " out of " + questions.length);
        }
    </script>
</head>
<body>
    <div class="quiz-container">
        <h1>Quiz</h1>
        <form>
        {% for question in questions %}
            <p>{{ question.question }}</p>
            {% set counter = loop.index %}
            {% for option in question.options %}
            <label>
                <input type="radio" name="q{{ counter }}_answer" value="{{ option }}">{{ option }}
            </label>
            {% endfor %}
        {% endfor %}
        </form>
        <button type="button" onclick="validateAnswers()">Submit</button>
    </div>
</body>
</html>
"""

# Render the template
template = Template(html_template)
rendered_html = template.render(questions=questions)

# Save the rendered HTML to file
with open("quiz.html", "w") as output_file:
    output_file.write(rendered_html)

# Start the HTTP server
port = 8000
Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", port), Handler) as httpd:
    print(f"Serving on port {port}")

    # Open the quiz in a web browser
    webbrowser.open(f"http://localhost:{port}/quiz.html")

    httpd.serve_forever()

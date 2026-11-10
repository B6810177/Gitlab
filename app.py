from flask import Flask, render_template, request

from bjt_bias import validate, bias

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    errors = []
    values = {}
    if request.method == 'POST':
        form = request.form
        values = {k: form.get(k, '') for k in ['VCC', 'R1', 'R2', 'RC', 'RE', 'beta', 'VBE']}
        try:
            v = validate.validate_inputs(
                values['VCC'], values['R1'], values['R2'],
                values['RC'], values['RE'], values['beta'], values['VBE']
            )
            result = bias.calculate_bias(**v)
        except Exception as e:
            errors.append(str(e))
    return render_template('index.html', result=result, errors=errors, values=values)


if __name__ == '__main__':
    app.run(debug=True)

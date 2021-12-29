from flask import Flask, render_template, redirect, url_for
from trading_simulator import PARAMS, run
from forms import ParamsForm


app = Flask(__name__)
app.config['SECRET_KEY'] = '3a368f9c1dce6b6ab1523772'


@app.route("/")
def home_page():
    return render_template('home.html')


@app.route("/model", methods=['GET', 'POST'])
def modeling_page():
    form = ParamsForm()
    if form.validate_on_submit():
        PARAMS['lifetime_period'] = form.lifetime_period.data
        PARAMS['platform_interest'] = form.platform_interest.data
        PARAMS['invest'] = form.invest.data
        PARAMS['segmentation'] = form.segmentation.data
        PARAMS['lifetime_accuracy'] = form.lifetime_acc.data
        PARAMS['demand_rmse_to_avg'] = form.demand_acc.data
        PARAMS['num_epochs'] = form.epochs.data
        return redirect(url_for("modeling_results_page"))
    return render_template('model.html', form=form, params=PARAMS)


@app.route ("/model/results")
def modeling_results_page(model_params=PARAMS):
    df = run(model_params)
    return render_template('market_results.html', df=df)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000", debug=True)

import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

import os
from io import BytesIO
import math
import random
import timeit

from helpers import helper
from algorithms.tsp.aco_tsp_solve import ACO_TSP_SOLVE
from algorithms.tsp.ga_tsp_solve import GA_TSP_SOLVE

from flask import Flask, render_template, request, make_response, redirect, abort, flash, url_for, jsonify
from werkzeug.utils import secure_filename

# import warnings
# warnings.filterwarnings("ignore")

YUKLEME_KLASORU = 'static/dataUpload'
# Test amaçlı duruyorlar, son hali => .csv ve .txt olcak
UZANTILAR = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv'])

app = Flask(__name__)

app.config['SECRET_KEY'] = '^%huYtFd90;90jjj'
app.config['UPLOADED_DATAS'] = 'uploads'

app.config['UPLOAD_FOLDER'] = YUKLEME_KLASORU
app.secret_key = "denemeKey"


def uzanti_kontrol(dosyaadi):
    return '.' in dosyaadi and \
        dosyaadi.rsplit('.', 1)[1].lower() in UZANTILAR


helper.run_schedule()


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/optimization')
def optimization():
    return render_template("optimization.html")


@app.route('/machine_learning')
def machine_learning():
    return render_template("machine-learning.html")


@app.route('/travellingsalesmanproblem')
def tsp():
    return render_template("tsp.html")


@app.route('/process2', methods=['POST'])
def process():

    email = request.form['email']
    name = request.form['name']
    print(name + " " + email)
    if name and email:
        datas = email + name
        time.sleep(5)
        return jsonify({'name': datas})

    return jsonify({'error': 'Missing data!'})


@app.route('/tsptest', methods=['POST'])
def tsptest():
    file_type = "csv"
    if file_type == "text":
        df = pd.read_text("../input/marmara_mesafe/{}".format("mesafeler.txt"))
    if file_type == "csv":
        df = pd.read_csv("data/marmara_mesafeler.csv")

    cities = df.loc[:, 'city'].values

    cities_x_axis = df.loc[:, 'longitude'].values  # longitude is x axis

    cities_y_axis = df.loc[:, 'latitude'].values  # latitude is y axis

    antsize = request.form['antsize']
    print(antsize)
    pheromonerho = request.form['pheromonerho']
    print("rho", pheromonerho)
    alpha = request.form['alfa']
    print("alfa", alpha)
    beta = request.form['beta']
    iteration = request.form['iteration']

    print(alpha + " " + beta)

    if antsize and pheromonerho and alpha and beta:
        start = timeit.default_timer()

        cities_xy = helper.format_for_genetic(cities_x_axis, cities_y_axis)

        aco_tsp = ACO_TSP_SOLVE(_x_axis=cities_x_axis,
                                _y_axis=cities_y_axis,
                                _iteration=int(iteration),
                                _ant_size=int(antsize),
                                _rho=float(pheromonerho),
                                _alpha=float(alpha),
                                _beta=float(beta),
                                _cities=cities)

        aco_best_route, aco_cost_values, aco_best_cost = aco_tsp.run_optimize()

        ga_tsp = GA_TSP_SOLVE(_cities_xy=cities_xy,
                              _cities=cities,
                              _life_count=100,
                              _cross_rate=0.4,
                              _mutation_rate=0.2)

        ga_best_route, ga_cost_values, ga_best_cost = ga_tsp.run(
            int(iteration))

        # bitti
        stop = timeit.default_timer()

        show_label = True

        # save routes figure
        plt_compare_routes_fig = helper.compare_route_graphic(
            cities_x_axis, cities_y_axis, cities, aco_best_route, ga_best_route)
        compare_route_fig_path = helper.save_figures_to_upload(
            plot_fig=plt_compare_routes_fig, img_name="plt_compare_routes.png")

        # save cost figure
        plt_compare_costs_fig = helper.compare_cost_values(
            aco_cost_values, ga_cost_values)
        compare_cost_fig_path = helper.save_figures_to_upload(
            plot_fig=plt_compare_costs_fig, img_name="plt_compare_costs.png")

        # compare_route_fig_path = "static/uploads/karınca.png"
        print("onay {} resim yolu : {}".format(
            show_label, compare_route_fig_path))

        time.sleep(5)

        return jsonify({'img1': compare_route_fig_path, 'img2': compare_cost_fig_path})

    return jsonify({'error': 'Missing data!'})

@app.route('/optimization')
def optimization():
    return render_template("optimization.html")

@app.route('/optimize', methods=['POST'])
def optimize():
    pass



@app.route('/salih')
def salih():
    return render_template("salih.html")

@app.route('/berkayTest')
def berkay_test():
    return render_template("berkaytest.html")

@app.route('/berkay')
def berkay():
    return render_template("berkay.html")
# Formdan gelen resmi kullanıcıya geri göster. Veya belgesyi

@app.route('/berkay/<string:dosya>')
def dosyayuklemesonuc(dosya):
    return render_template("berkay.html", dosya=dosya)
# Form ile dosya yüklemek

@app.route('/dataUpload', methods=['POST'])
def dosyayukle():
    if request.method == 'POST':
        # Formdan bize bir dosya geldi mi ?
        if 'dosya' not in request.files:
            flash('Dosya seçilmedi')
            return redirect('berkay')

            # Kullanıcı dosya seçmemiş olabilir veya tarayıcı boş göndermiş mi kontrol et.
        dosya = request.files['dosya']
        if dosya.filename == '':
            flash('Dosya seçilmedi')
            return redirect('berkay')

            # Gelen dosya tipi bizim istediğim tipte bir dosya mı ?
        # secure_filename => adı "../../../../home/images/logo.png" ise "home_images_logo.png" şeklinde çevirir.
        if dosya and uzanti_kontrol(dosya.filename):
            dosyaadi = secure_filename(dosya.filename)
            dosya.save(os.path.join(app.config['UPLOAD_FOLDER'], dosyaadi))
            # return redirect(url_for('berkay',dosya=dosyaadi))
            return redirect('berkay/' + dosyaadi)
        else:
            flash(
                'İzin verilmeyen dosya uzantısı. Lütfen .txt veya .csv uzantılı bir dosya yükleyiniz !')
            return redirect('berkay')
    else:
        abort(401)

# Cache Blocker


@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


@app.route('/tsptest2', methods=['POST'])
def tsptest2():
    """
    file operation done
    """
    """
    file = request.files['cityfile']
    filename = helper.combine_names()
    filename += secure_filename(file.filename)

    file.save(os.path.join(app.config['UPLOADED_DATAS'], filename))

    # file name
    print(file.filename, type(file), file.filename.split('.')[0])

    # file extension -1 yapıyor
    print(file.filename, type(file), file.filename.split('.')[-1])

    file_extension = str(file.filename.split('.')[-1])

    if file_extension == "txt":
        df = pd.read_text("uploads/{}".format(filename))
    if file_extension == "csv":
        df = pd.read_csv("uploads/{}".format(filename))

    """

    """
    end file operation
    """

    df = pd.read_csv("data/marmara_mesafeler.csv")

    cities = df.loc[:, 'city'].values

    cities_x_axis = df.loc[:, 'longitude'].values  # longitude is x axis

    cities_y_axis = df.loc[:, 'latitude'].values  # latitude is y axis

    show_label = False

    start = timeit.default_timer()

    ant_size = request.form.get('ant_size', False)

    pheromone_rho = request.form.get('pheromone_rho', False)

    alpha = request.form.get('alpha', False)

    beta = request.form.get('beta', False)

    # genetik parametreleri
    life_count = request.form.get('life_count', False)
    mutation_rate = request.form.get('mutation_rate', False)
    cross_rate = request.form.get('cross_rate', False)

    # iterasyon
    iteration = request.form.get('iteration', False)

    # file da eklenecek
    if ant_size and iteration and pheromone_rho and alpha and beta and life_count and mutation_rate and cross_rate and iteration:

        cities_xy = helper.format_for_genetic(cities_x_axis, cities_y_axis)

        aco_tsp = ACO_TSP_SOLVE(_x_axis=cities_x_axis,
                                _y_axis=cities_y_axis,
                                _iteration=int(iteration),
                                _ant_size=int(ant_size),
                                _rho=float(pheromone_rho),
                                _alpha=float(alpha),
                                _beta=float(beta),
                                _cities=cities)

        aco_best_route, aco_cost_values, aco_best_cost = aco_tsp.run_optimize()

        ga_tsp = GA_TSP_SOLVE(_cities_xy=cities_xy,
                              _cities=cities,
                              _life_count=int(life_count),
                              _cross_rate=float(cross_rate),
                              _mutation_rate=float(mutation_rate))

        ga_best_route, ga_cost_values, ga_best_cost = ga_tsp.run(
            int(iteration))

        # bitti
        stop = timeit.default_timer()
        print(start, "", stop, "", ga_best_cost, " ", aco_best_cost)

        show_label = True

        # save compare routes figure
        plt_compare_routes_fig = helper.compare_route_graphic(
            cities_x_axis, cities_y_axis, cities, aco_best_route, ga_best_route)
        compare_route_fig_path = helper.save_figures_to_upload(
            plot_fig=plt_compare_routes_fig, img_name="plt_compare_routes.png")

        # save compare cost figure
        plt_compare_costs_fig = helper.compare_cost_values(
            aco_cost_values, ga_cost_values)
        compare_cost_fig_path = helper.save_figures_to_upload(
            plot_fig=plt_compare_costs_fig, img_name="plt_compare_costs.png")

        # save ant colony route figure
        plt_antcolony_route_fig = aco_tsp.plot_cities(
            aco_best_route, aco_cost_values)

        antcolony_route_fig_path = helper.save_figures_to_upload(
            plot_fig=plt_antcolony_route_fig, img_name="plt_antcolony_route.png")

        # save ant colony cost figure
        plt_antcolony_costs_fig = aco_tsp.plot_cost_iteration(aco_cost_values)

        antcolony_cost_fig_path = helper.save_figures_to_upload(
            plot_fig=plt_antcolony_costs_fig, img_name="plt_antcolony_costs.png")

        # save genetic algorithm route figure
        plt_ga_route_fig = ga_tsp.plot_cities(
            cities_x_axis, cities_y_axis, ga_best_route, ga_cost_values)

        ga_route_fig_path = helper.save_figures_to_upload(
            plot_fig=plt_ga_route_fig, img_name="plt_ga_route.png")

        # save ant colony cost figure
        plt_ga_costs_fig = ga_tsp.plot_cost_iteration(ga_cost_values)

        ga_cost_fig_path = helper.save_figures_to_upload(
            plot_fig=plt_ga_costs_fig, img_name="plt_ga_costs.png")

        return jsonify({'compare_routes': compare_route_fig_path,
                        'compare_costs': compare_cost_fig_path,
                        'antcolony_route': antcolony_route_fig_path,
                        'antcolony_cost': antcolony_cost_fig_path,
                        'ga_route': ga_route_fig_path,
                        'ga_cost': ga_cost_fig_path})

    return jsonify({'error': 'Lütfen tüm verileri eksiksiz doldurun !'})


"""
@app.route('/travellingsalesmanproblem', methods = ["GET","POST"])
def run2():

    file_type = "csv"
    if file_type == "text":
        df = pd.read_text("../input/marmara_mesafe/{}".format("mesafeler.txt")) 
    if file_type == "csv":
        df = pd.read_csv("data/marmara_mesafeler.csv")

    cities = df.loc[:, 'city'].values

    cities_x_axis = df.loc[:,'longitude'].values  # longitude is x axis

    cities_y_axis = df.loc[:,'latitude'].values # latitude is y axis

    show_label = False

    if request.method == "POST":      
        start = timeit.default_timer()
        # karınca parametreleri
        ant_size = request.form.get("ant_size")
        pheromonerho = request.form.get("pheromonerho")
        alpha = request.form.get("alpha")
        beta = request.form.get("beta")

        # genetik parametreleri
        life_count = request.form.get("life_count")
        mutation_rate = request.form.get("mutation_rate")
        cross_rate = request.form.get("cross_rate")

        # iterasyon
        iteration = request.form.get("iteration")

        cities_xy = helper.format_for_genetic(cities_x_axis,cities_y_axis)
        
        aco_tsp = ACO_TSP_SOLVE(_x_axis = cities_x_axis,
                                _y_axis = cities_y_axis,
                                _iteration = int(iteration),
                                _ant_size = int(ant_size),
                                _rho = float(pheromonerho),
                                _alpha = float(alpha),
                                _beta = float(beta),
                                _cities = cities)

        aco_best_route, aco_cost_values, aco_best_cost = aco_tsp.run_optimize()

        ga_tsp = GA_TSP_SOLVE(_cities_xy = cities_xy,
                                _cities = cities,
                                _life_count = int(life_count),
                                _cross_rate = float(cross_rate),
                                _mutation_rate = float(mutation_rate))

        ga_best_route, ga_cost_values, ga_best_cost  = ga_tsp.run(int(iteration))

        # bitti
        stop = timeit.default_timer()

        show_label = True

        # save routes figure
        plt_compare_routes_fig = helper.compare_route_graphic(cities_x_axis, cities_y_axis, cities, aco_best_route, ga_best_route)
        compare_route_fig_path = helper.save_figures_to_upload(plot_fig = plt_compare_routes_fig, img_name = "plt_compare_routes.png")

        # save cost figure
        plt_compare_costs_fig = helper.compare_cost_values(aco_cost_values, ga_cost_values)
        compare_cost_fig_path = helper.save_figures_to_upload(plot_fig = plt_compare_costs_fig, img_name = "plt_compare_costs.png")
        
        # compare_route_fig_path = "static/uploads/karınca.png"
        print("onay {} resim yolu : {}".format(show_label, compare_route_fig_path))

        return render_template("tsp.html", route_compare_img = compare_route_fig_path, 
                                           cost_compare_img = compare_cost_fig_path, 
                                           onayli = show_label)
        
    else:
        return render_template("tsp.html", onayli = False)
"""
if __name__ == "__main__":
    app.run(debug=True)

import time
import os
from flask import Flask, render_template, redirect
from .plots import empty_plot, loss_accuracy_plot
from .dataloader import LogDataLoader, to_dict


app = Flask(__name__)
app.config["keras_log_db_path"] = "sqlite:///" + os.path.join(os.environ["HOME"], "tmp", "keras_logs.db")
print("DB is", app.config["keras_log_db_path"])


def db():
    try:
        return LogDataLoader(path=app.config["keras_log_db_path"])
    except ValueError:
        redirect("/nodb")


@app.route("/")
def main():
    log = db()
    return render_template("overview.html", data=zip(*log.get_overview()))


@app.route("/nodb")
def nodb():
    return render_template("nodb.html")


@app.route("/id/<int:id>")
def detail(id):
    start_time = time.time()
    log = db()
    if not log.id_exists(id):
        return render_template("idnotfound.html", id=id)
    comment = log.get_comment(id)
    df = log.get_data(id)
    last_update_time = log.get_last_update_time(id)
    config_string = log.get_config(id)
    config_dict = to_dict(config_string)
    layers = config_dict["layers"] if "layers" in config_dict else config_dict["config"]["layers"] if "layers" in config_dict["config"] else config_dict["config"]
    duration = time.time() - start_time
    general = {key: value for key, value in config_dict.items() if key != "layers"}

    if "optimizer" not in general:
        general["optimizer"] = {"name": "not found"}

    if log.id_exists(id) and len(df) > 0:
        loss_plot = loss_accuracy_plot(df, "epoch", [["loss", "val_loss"], ["acc", "val_acc"]])
    else:
        loss_plot = empty_plot
    return render_template("detail.html",
                           loss=loss_plot,
                           comment=comment,
                           id=id,
                           config_data=config_string,
                           layers=layers,
                           general=general,
                           last_update_time=last_update_time,
                           runs=zip(*log.get_overview()[:2]),
                           db_load_time=str(round(duration, 2)) + " s")


@app.route("/remove/<int:id>")
def remove(id):
    log = db()
    log.remove(id)
    return redirect("/")


app.debug = True

import marimo

__generated_with = "0.10.7"
app = marimo.App(width="medium")


@app.cell
def _(mo):
    rootdir = mo.ui.file_browser(selection_mode='directory',multiple=False)
    rootdir
    return (rootdir,)


@app.cell
def _(mo, os, rootdir):
    mo.stop(not rootdir.value, "HINT: Select a folder")
    def findautotests(dir):
        files = [x for x in os.listdir(dir) if os.path.isdir(os.path.join(dir, x))]
        targets = [dir] if "autotest" in files else []
        for file in files:
            targets.extend(findautotests(os.path.join(dir, file)))
        return targets


    _options = sorted(
        [
            x.replace(rootdir.value[0].path, ".")
            for x in findautotests(rootdir.value[0].path)
        ]
    )
    mo.stop(not _options, "ERROR: No autotests found")
    _hint = "(choose one)"
    target = mo.ui.dropdown(
        options=[_hint] + _options,
        value=_hint,
        label="Target: ",
        allow_select_none=False,
    )
    return findautotests, target


@app.cell
def _(mo, start, stop, target):
    mo.hstack([target,start,stop],justify='start')
    return


@app.cell
def _(mo, os, rootdir, target):
    get_target,set_target = mo.state(None)
    start = mo.ui.button(label="Start",
                         disabled=not os.path.isdir(os.path.join(rootdir.value[0].path,target.value.replace('./',''))),
                         on_click=lambda x:set_target(os.path.join(rootdir.value[0].path,target.value.replace('./',''))),
                        )
    return get_target, set_target, start


@app.cell
def _(get_target, mo, os, rootdir, set_target, target):
    mo.stop(not get_target())
    os.system(
        f"cd {rootdir.value[0].path}; gridlabd -W {target.value.replace('./', '')} -D keep_progress=TRUE --validate"
    )
    set_target(None)
    return


@app.cell
def _(mo):
    stop = mo.ui.button(label="Stop",disabled=True)
    return (stop,)


@app.cell
def _(mo, os, rootdir, target):
    mo.stop(
        not os.path.isdir(
            os.path.join(rootdir.value[0].path, target.value.replace("./", ""))
        ),
        "HINT: choose a target folder",
    )
    return


@app.cell
def _(os, re, rootdir, target):
    def findresults(dir):
        # print(os.path.join(rootdir.value[0].path,target.value.replace("./",""),"validate.txt"))
        with open(os.path.join(rootdir.value[0].path,target.value.replace("./",""),"validate.txt"),"r") as fh:
            return [os.path.splitext(x.split('\t')[2])[0] for x in fh.readlines() if re.match("^[ESX]\t",x)]
        return []
    return (findresults,)


@app.cell
def _(findresults, mo, os, rootdir, target):
    mo.stop(not 
            os.path.exists(os.path.join(rootdir.value[0].path,target.value.replace('./',''),"validate.txt")),"HINT: Click 'Start' to run validation in this target folder")

    def readfile(path):
        with open(path,"r") as fh:
            return fh.read()

    def subtabs(path):
        return {os.path.basename(x):mo.md(f"~~~\n{readfile(os.path.join(path,x))}\n~~~""") for x in os.listdir(path) if os.stat(os.path.join(path,x)).st_size > 0}

    results = {os.path.basename(x):mo.ui.tabs(subtabs(x),lazy=True) for x in findresults(target.value)}
    return readfile, results, subtabs


@app.cell
def _(mo, results):
    mo.stop(not results,"All tests succeeded")
    mo.vstack([mo.md(f"{len(results)} tests failed"),mo.ui.tabs(results,lazy=True)])
    return


@app.cell
def _():
    import marimo as mo
    import sys, os, json, re
    return json, mo, os, re, sys


if __name__ == "__main__":
    app.run()

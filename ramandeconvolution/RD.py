#!/usr/bin/python
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys, os
import ntpath
import configparser
import gui
import copy
from dialogs import *
from fit import FIT
from data import DATA
from convertwdf import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from recordtype import recordtype
from distutils.util import strtobool
import itertools
import queue
import multiprocessing as mp
from multiprocessing import Pool, cpu_count, Value, Process, Queue
from concurrent.futures import ProcessPoolExecutor, as_completed
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

Limits = recordtype('Limits', ['min', 'max'])

def BatchWorker(file_queue, results_queue, names, shape, bsParams, crop,
                            peakLimits, parguess, bounds, index, folder):
    result = pd.Series(index = index, dtype = object)
    while True:
        try:
            fname = file_queue.get_nowait()
            result.name = os.path.basename(fname)
            dt = DATA()
            try:
                dt.loadData(fname)
                dt.crop(crop.min, crop.max)
                dt.fitBaseline(bsParams, peakLimits, abs = True)

                text = ''
                for deg in np.arange(0, dt.bsDegree+1):
                    if dt.bsCoef[deg]>=0 and deg!=0:
                        text += '+'
                    text += f'{dt.bsCoef[deg]:.4E}*x^{dt.bsDegree-deg}'
                result.loc['baseline'] = text
            except Exception as e:
                print("Error {}".format(e))
            try:
                fit = FIT(shape, names)
                fit.deconvolute(dt, parguess.copy(), bounds.copy(), batch=True)
                for i, pars in enumerate(zip(names, shape)):
                    result.loc[pars[0]+'_'+'Position'] = fit.pars[int(
                                                       np.sum(fit.args[:i])+2)]
                    result.loc[pars[0]+'_'+'Amplitude'] = fit.pars[int(
                                                       np.sum(fit.args[:i]))]
                    result.loc[pars[0]+'_'+'FWHM'] = fit.fwhm[i]
                    result.loc[pars[0]+'_'+'Area'] = fit.area[i]
                    if pars[1] == 'V':
                        result.loc[pars[0]+'_'+'L/G'] = fit.pars[int(
                                                       np.sum(fit.args[:i])+3)]
                    elif pars[1] == 'B':
                        result.loc[pars[0]+'_'+'1/q'] = fit.pars[int(
                                                       np.sum(fit.args[:i])+3)]
            except Exception as e:
                print('Could not deconvolute the {} file'.format(f))
                result.iloc[1:len(index)] = -1*np.ones(len(index)-1)
                print(e)
            path = folder+ '/' + os.path.basename(fname)+'.png'
            fig = plt.figure(figsize=(12,8))
            fit.plot(figure=fig, path=path)
            results_queue.put('|'.join(np.append(result.name,
                                                    result.values.astype(str))))
        except queue.Empty:
            break

class Worker(QRunnable):
    '''
    Worker thread
    '''
    def __init__(self, fit, *args):
        super(Worker, self).__init__()

        self.fit = fit
        self.args = args

    @pyqtSlot()
    def run(self):
        '''
        Initialize the runner function with passed arguments
        '''
        try:
            self.fit.deconvolute(*self.args)
        except Exception as e:
            print('something went wrong\n', e)

class Deconvolute(QThread):

    error = pyqtSignal()
    progress = pyqtSignal(int, name='progress')
    def __init__(self, function, *args):
        QThread.__init__(self)
        self.function = function
        self.args = args

    def run(self):
        try:
            self.function(*self.args)
        except Exception as e:
            self.error.emit()
            print('Something went wrong: ', e)

class BatchDeconvolute(QThread):
    # Various sygnals
    error           = pyqtSignal()
    finished        = pyqtSignal(str, name='finished')
    procs_ready     = pyqtSignal(name='ready')
    building_output = pyqtSignal(name='building')
    output_saved    = pyqtSignal(str, name='saved')
    progress        = pyqtSignal(int, name='progress')

    def __init__(self, _files, _parguess, _bounds, _fit, _params):
        QThread.__init__(self)
        self.files = _files
        self.parguess = _parguess
        self.bounds = _bounds
        self.cores = _params[0]
        self.bsParams = _params[1:]
        self.fit = _fit
        self.results          = Queue()
        self.files_to_process = Queue()
        self.cancel_job = False

    def run(self):
        # Create N processes that will read files and deconvolute them
        try:
            _min = int(self.bsParams[1])
            _max = int(self.bsParams[2])
            _crop_min = int(self.bsParams[3])
            _crop_max = int(self.bsParams[4])
        except ValueError:
            self.error.emit()

        self.cropLimits = Limits(_crop_min, _crop_max)
        self.peakLimits = Limits(_min, _max)

        index = ['baseline']
        for name, s in zip(self.fit.names, self.fit.shape):
            index = np.append(index, [name+'_'+nm for nm in
                                    ('Position', 'Amplitude', 'FWHM', 'Area')])
            if s == 'V':
                index = np.append(index, '_'.join((name, 'L/G')))
            elif s == 'B':
                index = np.append(index, '_'.join((name, '1/q')))
        out = pd.DataFrame(index = index)

        folder  = os.path.dirname(self.files[0])+'/BatchDeconvolution_'
        folder += os.path.splitext(os.path.basename(self.files[0]))[0]
        if not os.path.exists(folder):
            os.makedirs(folder)
        arguments = [self.fit.names, self.fit.shape, self.bsParams[0],
                    self.cropLimits, self.peakLimits, self.parguess,
                    self.bounds, index, folder]

        # Fill the queue with files to process
        for file in self.files:
            self.files_to_process.put(file)

        # Create all the processes
        processes = []
        for w in range(self.cores):
            args = [self.files_to_process, self.results] + arguments
            p = Process(target=BatchWorker, args=args)
            processes.append(p)

        self.procs_ready.emit()

        # Start all the processes
        for p in processes:
            p.start()

        # Update the slider
        prev = 0
        while self.files_to_process.qsize():
            prog = int(100 * (len(self.files) - self.files_to_process.qsize())
                                                            / len(self.files))
            if prog != prev :
               self.progress.emit(prog)
               prev = prog

        # Wait for the processes to finish
        for p in processes:
            p.join()

        if not self.cancel_job:
            self.building_output.emit()
            # Process the results from the queue
            while not self.results.empty():
                res = self.results.get().split('|')
                out[res[0]] = res[1:]
            out.to_csv(folder+'/BatchDeconvolutionResults.csv')
            self.saved.emit(folder+'/BatchDeconvolutionResults.csv')
            if list(out.iloc[2]).count(-1) >0:
                pb = list(out.columns[out.iloc[0] == -1])
                self.finished.emit('<|>'.join(pb))
            else:
                self.finished.emit('OK')
        else:
            self.error.emit()

    def cancel(self):
        # Cancel the batch deconvolution
        self.cancel_job = True
        while True:
            # Remove all the remaining files from the queue
            try:
                self.files_to_process.get_nowait()
            except queue.Empty:
                break

class RD(QMainWindow, gui.Ui_MainWindow):

    header  = 50*'*'+'\n\n'+10*' '+'DECONVOLUTION OF RAMAN SPECTRA'
    header += 10*''+'\n\n'+50*'*'

    def __init__(self):
        super(RD, self).__init__()
        self.setupUi(self)
        #variables
        self.data = DATA()
        self.fit = 0
        self.changed = False
        self.peaksLimits = Limits(900, 1850)
        self.spike = 0 #scatter plot for spikes
        self.limit_low, self.limit_high = 0, 0 #exclude region
        self.baseline = 0
        self.path =os.path.dirname(os.path.realpath(__file__))

        self.actionQuit.triggered.connect(self.close)
        self.actionAbout.triggered.connect(self.about)
        self.actionGuess.triggered.connect(lambda: [self.dockGuess.setVisible(self.actionGuess.isChecked()),
                                                    self.dockGuess.raise_()])
        self.actionOutput.triggered.connect(lambda: [self.dockOut.setVisible(self.actionOutput.isChecked()),
                                                    self.dockOut.raise_()])
        self.dockGuess.visibilityChanged.connect(self.actionGuess.setChecked)
        self.dockOut.visibilityChanged.connect(self.actionOutput.setChecked)
        self.actionToolbar.triggered.connect(self.toolBar.toggleViewAction().trigger)
        self.actionNew.triggered.connect(self.New)
        self.actionSave.triggered.connect(self.Save)
        self.actionCrop.triggered.connect(self.Crop)
        self.actionRemove_Baseline.triggered.connect(self.Baseline)
        self.actionSpike_Removal.triggered.connect(self.removeSpikes)
        self.actionSmoothing.triggered.connect(self.Smoothing)
        self.actionDeconvolute.triggered.connect(self.Deconvolution)
        self.actionDeconvolute_MCMC.triggered.connect(self.DeconvMCMC)
        self.actionBatch_deconvolution.triggered.connect(self.BatchDeconv)
        self.actionLoadGuess.triggered.connect(self.LoadGuess)
        self.actionLoad_defaults.triggered.connect(lambda: self.LoadGuess(fname = self.path+'/config/initialData.csv'))
        self.actionExportGuess.triggered.connect(self.ExportGuess)
        self.tabifyDockWidget(self.dockGuess, self.dockOut)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tableWidget.itemChanged.connect(self.itemCheck)
        self.textOut.setReadOnly(True)
        self.textOut.setText(self.header)
        self.readConfig()
        self.dockGuess.raise_()


        self.spikeDialog = SpikeDialog(self.threshold)
        self.spikeDialog.slider.sliderReleased.connect(self.showSpikes)

        self.smoothDialog = SmoothDialog()
        self.smoothDialog.slider.sliderReleased.connect(self.previewSmoothed)

        self.figure = plt.figure()
        self.figure.set_tight_layout(True)
        self.subplot = self.figure.add_subplot(111) #add a subfigure
        #add widget
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setFocusPolicy(Qt.ClickFocus )
        self.canvas.setFocus()
        self.canvas.mpl_connect('button_press_event', self.onclick)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.gridLayout.addWidget(self.toolbar)
        self.gridLayout.addWidget(self.canvas)

        actionOpen  = QAction(QIcon("graphics/open.png"),"Open",self)
        actionSave  = QAction(QIcon("graphics/save.png"),"Save",self)
        actionCrop  = QAction(QIcon("graphics/crop.png"),"Crop",self)
        actionSpike = QAction(QIcon("graphics/spike.svg"),"Spike removal",self)
        actionSmooth = QAction(QIcon("graphics/smooth.svg"),"Smoothing",self)
        actionBaseline = QAction(QIcon("graphics/baseline.png"),"Remove baseline",self)
        actionDeconv = QAction(QIcon("graphics/deconv.svg"),"Deconvolution", self)
        actionMCMC = QAction(QIcon("graphics/mcmc.png"),"Deconvolution\nwith MCMC", self)
        actionBatch = QAction(QIcon("graphics/batch.png"),"Batch deconvolution", self)
        self.toolBar.addAction(actionOpen)
        self.toolBar.addAction(actionSave)
        self.toolBar.addSeparator()
        self.toolBar.addAction(actionCrop)
        self.toolBar.addAction(actionBaseline)
        self.toolBar.addAction(actionSpike)
        self.toolBar.addAction(actionSmooth)
        self.toolBar.addSeparator()
        self.toolBar.addAction(actionDeconv)
        self.toolBar.addAction(actionMCMC)
        self.toolBar.addSeparator()
        self.toolBar.addAction(actionBatch)
        self.toolBar.addSeparator()
        self.toolBar.toggleViewAction().setChecked(self.actionToolbar.isChecked())
        actionOpen.triggered.connect(self.New)
        actionCrop.triggered.connect(self.Crop)
        actionBaseline.triggered.connect(self.Baseline)
        actionSpike.triggered.connect(self.removeSpikes)
        actionSave.triggered.connect(self.Save)
        actionSmooth.triggered.connect(self.Smoothing)
        actionDeconv.triggered.connect(self.Deconvolution)
        actionMCMC.triggered.connect(self.DeconvMCMC)
        actionBatch.triggered.connect(self.BatchDeconv)

        self.startUp()


        self.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableWidget.customContextMenuRequested.connect(self.tableItemRightClicked)



    def startUp(self):
        #generate dummy data to plot at start-up
        X = np.arange(800, 2000, 2)
        Y1 = FIT.lorents(X, 1800, 1358, 110)
        Y2 = FIT.lorents(X, 1700, 1590, 50)
        self.subplot.plot(X, (Y1+Y2)+20*np.random.randn(len(X)), 'o')
        self.subplot.plot(X, Y1+Y2, 'r--', label = 'Sample data')
        self.subplot.legend()
        self.subplot.plot(X, Y1)
        self.subplot.plot(X, Y2)
        self.subplot.set_xlim(np.min(X), np.max(X))
        self.plotAdjust()

    def removeSpikes(self):
        #detect and remove spikes in the data (current data)
        if not np.shape(self.data.X):
            self.errorBox('There is no data', 'No data...')
            return
        self.Plot(self.data.X, self.data.current, 'Experimental data')
        self.showSpikes()
        result = self.spikeDialog.exec_()
        if not result:
            self.data.spikes = []
            if self.spike != 0:
                self.spike.remove()
                self.spike = 0
                self.subplot.legend()
                self.canvas.draw()
            return
        self.data.removeSpikes()
        self.statusbar.showMessage("%d datapoints removed" %len(self.data.spikes), 2000)
        self.Plot(self.data.X, self.data.current, "Experimental data", clear=True)
        if not self.changed:
            self.changed = True
            self.setWindowTitle(self.windowTitle()+'*')

    def Smoothing(self):
        #smooth the current data according to the user defined parameters
        if not np.shape(self.data.X):
            self.errorBox('There is no data', 'No data...')
            return
        self.Plot(self.data.X, self.data.current, "Experimental data")
        self.previewSmoothed()
        result = self.smoothDialog.exec_()
        self.baseline.remove()
        self.baseline = 0
        if not result:
            self.subplot.legend()
            self.canvas.draw()
            return
        self.data.prev = np.column_stack((self.data.X, self.data.current))
        self.data.current = self.data.smooth(self.data.current, 2*self.smoothDialog.slider.value()+1)

        self.Plot(self.data.X, self.data.current, "Smoothed data")
        self.plotAdjust()
        if not self.changed:
            #if the current data was changed add '*' to the title
            self.changed = True
            self.setWindowTitle(self.windowTitle()+'*')


    def previewSmoothed(self):
        #plot a preview of the smoothed data
        y_ = self.data.smooth(self.data.current, 2*self.smoothDialog.slider.value()+1)
        if self.baseline != 0:
            self.baseline.remove()
        self.baseline,  = self.subplot.plot(self.data.X, y_, 'r--', label = 'Smoothed data')
        self.subplot.legend()
        self.canvas.draw()
        return y_

    def prepDataForDeconv(self, **kwargs):
        #prepare the data for deconvolution
        #the function first checks if the data is present and that the baseline was removed
        #fitting parameters are then taken from the table and put in a list
        batch = kwargs.get('batch', False)
        if not np.shape(self.data.X) and not batch:
            self.errorBox('There is no data', 'No data...')
            return -1, -1, -1
        if not np.shape(self.data.baseline) and not batch:
            result = QMessageBox.question(self,
                    "Baseline...",
                    "The baseline is still present!\nWould you like to remove it first?",
                    QMessageBox.Yes| QMessageBox.No)
            if result == QMessageBox.Yes:
                res = self.Baseline()
                if res == -1:
                    return -1, -1, -1
            else:
                return -1, -1, -1
        rows = self.tableWidget.rowCount()
        cols = self.tableWidget.columnCount()
        params = pd.DataFrame(columns = ['lb', 'pos', 'pos_min', 'pos_max',  'int', 'width', 'shape'])
        for row in range(rows):
            if self.tableWidget.item(row, 0).checkState() & Qt.Checked:
                error = [self.itemCheck(self.tableWidget.item(row, col), silent=True) for col in range(1, cols-1)]
                if True in error:
                    self.errorBox("Bad parameters", "Bad values")
                    self.dockGuess.raise_()
                    return -1, -1, -1
                d =[self.tableWidget.item(row, col).text() for col in range(1, cols-1)]
                p_shape = self.tableWidget.cellWidget(row, cols-1).currentText().strip()[0]
                params = params.append({'lb': d[0],  'pos' : d[1], 'pos_min' : d[2],
                    'pos_max' : d[3], 'int' : d[4], 'width' : d[5], 'shape' : p_shape}, ignore_index =True)
        self.fit = FIT(params['shape'], params['lb'])
        parguess = np.concatenate([[params['int'][i], params['width'][i], params['pos'][i]]
                    for i in range(len(params['lb'])) ]).astype(float)
        lower = np.concatenate([[5, 5, params['pos_min'][i]] for i in range(len(params['lb'])) ]).astype(float)
        upper = np.concatenate([[float('inf'), float('inf'), params['pos_max'][i]] for i in range(len(params['lb'])) ]).astype(float)
        return parguess, lower, upper

    def Deconvolution(self):
        #deconvolute the data in a different thread
        parguess, lower, upper = self.prepDataForDeconv()
        if not np.shape(parguess):
            return
        bounds = [lower, upper]
        progress = QProgressDialog("Deconvoluting...", "Cancel", 0, 100)
        progress.setCancelButton(None)
        progress.show()
        progress.setValue(5)
        self.error = False
        self.deconvolutionThread = Deconvolute(self.fit.deconvolute, self.data, parguess, bounds, False)
        progress.canceled.connect(self.deconvolutionThread.exit)
        self.deconvolutionThread.finished.connect(lambda: [progress.setValue(100), self.plotDeconvResult()])
        self.deconvolutionThread.error.connect(lambda: [progress.setValue(100), self.errorBox("Wrong parameters...")])
        self.deconvolutionThread.start()

    def DeconvMCMC(self):
        parguess, lower, upper = self.prepDataForDeconv()
        if not np.shape(parguess):
            return
        bounds = [lower, upper]
        progress = QProgressDialog("Deconvoluting...", "Cancel", 0, 100)
        progress.setCancelButton(None)
        progress.show()
        progress.setValue(0)
        self.error = False
        self.deconvolutionThread = Deconvolute(self.fit.decMCMC, self.data, parguess, bounds, 10000)
        self.fit.pg.connect(progress.setValue)
        progress.canceled.connect(self.deconvolutionThread.exit)
        self.deconvolutionThread.finished.connect(lambda: [progress.setValue(100), self.plotDeconvResult()])
        self.deconvolutionThread.error.connect(lambda: [progress.setValue(100), self.errorBox("Wrong parameters...")])
        self.deconvolutionThread.start()

    def BatchDeconv(self):
        if self.changed:
            result = QMessageBox.question(self,
                    "Unsaved file...",
                    "Do you want to save the data before exiting?",
                    QMessageBox.Yes| QMessageBox.No |QMessageBox.Cancel)
            if result == QMessageBox.Yes:
                self.Save()
            elif result == QMessageBox.Cancel:
                return
        self.changed = False
        path = self.initialDir
        fnames, _filter = QFileDialog.getOpenFileNames(self, 'Open files', path,"Text files (*.txt *.dat);; Wire data files (*.wdf);; All files (*.*)")
        if not fnames:
            return
        elif self.initialDir!=ntpath.dirname(fnames[0]):
            self.initialDir=ntpath.dirname(fnames[0]) #update the initial directory for the Open/Save dialog
            self.settings.setValue('directory', self.initialDir)
        self.setWindowTitle( 'Raman Deconvolution - Batch Deconvolution')
        if _filter == 'Wire data files (*.wdf)':
            for i, fname in enumerate(fnames):
                convert(fname)
                fnames[i] = fname[:-3]+'txt'
        fnames.sort()
        dialog = BatchDialog(len(fnames), self.degree, self.peakLimits.min, self.peakLimits.max, 700, 2500, cpu_count())
        result = dialog.exec_()
        if not result:
            return
        params = dialog.getData()

        parguess, lower, upper = self.prepDataForDeconv(batch=True)
        if not np.shape(parguess):
            return
        bounds = [lower, upper]
        progress = QProgressDialog(f"Creating {params[0]} processes", "Cancel", 0, 100)
        progress.setMinimumWidth(300)
        progress.setWindowTitle("Batch deconvolution")
        progress.show()
        progress.setValue(0)
        self.batch = BatchDeconvolute(fnames, parguess, bounds, self.fit, params)

        progress.canceled.connect(self.batch.cancel)
        self.textOut.clear()
        self.subplot.clear()

        self.batch.progress.connect(progress.setValue)
        self.batch.procs_ready.connect(lambda: progress.setLabelText("Deconvoluting"))
        self.batch.building_output.connect(lambda: progress.setLabelText("Building the output"))
        self.batch.finished.connect(lambda x: [progress.setValue(100), self.errorBox('Some files were not deconvoluted...') if x!='OK' else print('all done')])
        self.batch.error.connect(lambda: [progress.setValue(100), print("job canceled")])
        self.batch.saved.connect(lambda x:[self.textOut.append('Results are saved at {}'.format(x)), self.dockOut.raise_()])
        self.batch.start()


    def plotDeconvResult(self):
        if self.error or self.fit.error:
            return
        self.statusbar.showMessage("Thread finished succesfully", 1000)
        self.Plot(self.data.X, self.data.current, "Experimental data")
        labels = self.fit.names
        [self.subplot.plot(self.data.X, self.fit.peaks[lb], label = lb) for lb in labels]
        self.subplot.plot(self.data.X, self.fit.peaks['cumulative'], 'r--', label = 'cumulative')
        self.plotAdjust()


        self.textOut.append(self.fit.report)
        self.dockOut.raise_()

    def showSpikes(self):
        self.data.detectSpikes(self.spikeDialog.slider.value())
        if self.spike != 0:
            self.spike.remove()
            self.spike = 0
            self.canvas.draw()
        sp = self.data.spikes
        if len(sp):
            self.spike, = self.subplot.plot(self.data.X[sp], self.data.current[sp], 'ro', label = 'Spikes')
            self.subplot.legend()
            self.canvas.draw()

    def plotAdjust(self):
        self.subplot.set_xlabel(r'$\mathbf{Raman\ shift,\ cm^{-1}}$')
        self.subplot.set_ylabel(r'$\mathbf{Intensty}$')
        self.subplot.legend()
        self.canvas.draw()

    #right click on the plot
    def onclick(self, event):
        if  np.shape(self.data.X):
            if event.button == 3:  #right click
                self.listMenu= QMenu()
                menu_item_0 = self.listMenu.addAction("Delete datapoint (spike)")
                idx = np.abs(self.data.X - event.xdata).argmin()
                self.statusbar.showMessage('Datapoint selected: X = %f, Y = %f' %(self.data.X[idx], self.data.current[idx]), 1000)
                spike, = self.subplot.plot(self.data.X[idx], self.data.current[idx], 'rs', label = 'Selected datapoint')
                self.subplot.legend()
                self.canvas.draw()
                cursor = QCursor()
                menu_item_0.triggered.connect(lambda: self.deleteSpike(idx))
                self.listMenu.move(cursor.pos() )
                self.listMenu.show()
                self.listMenu.aboutToHide.connect(lambda : (spike.remove(), self.canvas.draw()))

    def deleteSpike(self, x):
        self.statusbar.showMessage('Spike deleted: X = %f, Y = %f' %(self.data.X[x], self.data.current[x]), 1000)
        self.data.spikes = x
        self.data.removeSpikes()
        self.Plot(self.data.X, self.data.current, "Experimental data")
        if not self.changed:
            self.changed = True
            self.setWindowTitle(self.windowTitle()+'*')

    def Baseline(self):
        if not np.shape(self.data.X):
            self.errorBox('There is no data', 'No data...')
            return -1
        if np.shape(self.data.baseline):
            self.data.setData(self.data.X, self.data.Y.copy())
        self.Plot(self.data.X, self.data.current, 'Experimental data')

        if self.peakLimits.min <= self.data.X[0]:
            self.peakLimits.min = round(self.data.X[0] + 0.25*(self.data.X[-1]-self.data.X[0]))
        if self.peakLimits.max >= self.data.X[-1]:
            self.peakLimits.max = round(self.data.X[-1] - 0.25*(self.data.X[-1]-self.data.X[0]))
        dialog = BaselineDialog(self.degree, self.peakLimits.min, self.peakLimits.max)
        dialog.btPreview.clicked.connect(lambda: self.previewBaseline(dialog))
        self.previewBaseline(dialog)
        result = dialog.exec_()
        self.limit_low.remove()
        self.limit_high.remove()
        self.baseline.remove()
        self.limit_low, self.limit_high = 0, 0
        self.baseline = 0
        if not result:
            self.subplot.legend()
            self.canvas.draw()
            return -1
        params = dialog.getData()
        try:
            _min = int(params[2])
        except ValueError:
            self.statusbar.showMessage("Wrong value...setting to default", 3000)
        try:
            _max = int(params[3])
        except ValueError:
            self.statusbar.showMessage("Wrong value...setting to default", 3000)
        self.peakLimits = Limits(_min, _max)
        self.data.fitBaseline(params[1], self.peakLimits, abs = True)
        self.Plot(self.data.X, self.data.current, "Baseline corrected data")
        self.plotAdjust()
        self.dockOut.setVisible(True)
        self.textOut.clear()
        self.textOut.append('                  BASELINE FIT                   ')
        self.textOut.append('*************************************************')
        self.textOut.append('Polynomial fit -- degree: {}'.format(self.data.bsDegree))
        self.textOut.append('Fitting equation:')
        text = ''
        for deg in np.arange(0, self.data.bsDegree+1):
            if self.data.bsCoef[deg]>=0 and deg!=0:
                text += '+'
            text += '{:.4E}*x^{}'.format(self.data.bsCoef[deg], self.data.bsDegree-deg)
        self.textOut.append(text + '\n')
        self.dockOut.raise_()
        if not self.changed:
            self.changed = True
            self.setWindowTitle(self.windowTitle()+'*')

    def previewBaseline(self, dialog):
        dt = DATA()
        dt.setData(self.data.X, self.data.current)
        try:
            _min = int(dialog.lineEdit_min.text())
            _max = int(dialog.lineEdit_max.text())
        except ValueError:
            self.statusbar.showMessage("Wrong value...setting to default", 3000)
            _min = self.peakLimits.min
            _max = self.peakLimits.max
        if self.baseline != 0:
            self.limit_low.remove()
            self.limit_high.remove()
            self.baseline.remove()
        self.limit_low,  = self.subplot.plot([_min, _min], [np.min(self.data.current), np.max(self.data.current)], color = 'red', label = 'Exclude region')
        self.limit_high, = self.subplot.plot([_max, _max], [np.min(self.data.current), np.max(self.data.current)], color = 'red')

        peakLimits = Limits(_min, _max)
        dt.fitBaseline(dialog.spinBox.value(), peakLimits, abs = True)
        self.baseline, = self.subplot.plot(dt.X, dt.baseline, 'r--', label = "Baseline")
        self.subplot.legend()
        self.canvas.draw()
        del dt


    def LoadGuess(self, **kwargs):
        if 'fname' in kwargs:
            fname = kwargs['fname']
        else:
            path = self.initialDir
            fname, _filter = QFileDialog.getOpenFileName(self, 'Open file', path,"Comma separated values (*.csv);; All files (*.*)")
            if not fname:
                return
        try:
            parameters = pd.read_csv(fname)
            self.tableWidget.setRowCount(0)
            cols = ['labels', 'freq', 'freq_min', 'freq_max' ,'intens', 'width']
            shape = ['Lorentzian', 'Gaussian', 'Voigt', 'BWF']
            for i, l in enumerate(parameters['labels']):
                self.tableWidget.insertRow(i)
                self.tableWidget.setItem(i, 0, QTableWidgetItem(''))
                self.tableWidget.item(i, 0).setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                self.tableWidget.item(i, 0).setCheckState(Qt.Checked)
                for j, col in enumerate(cols):
                    self.tableWidget.setItem(i, j+1, QTableWidgetItem(str(parameters[col][i])))

                combo = QComboBox()
                [combo.addItem('  '+s) for s in shape]
                if parameters['shape'][i] in [s[0] for s in shape]:
                    combo.setCurrentIndex([s[0] for s in shape].index(parameters['shape'][i]))
                self.tableWidget.setCellWidget(i, j+2, combo)

            self.statusbar.showMessage("Initial parameters were loaded", 2000)
        except FileNotFoundError:
            self.errorBox('File not found', 'Parameters were not loaded')
        except KeyError:
            self.errorBox('Wrong file format', "Parameters were not loaded")
        except Exception as e:
            self.errorBox('Error\n{}'.format(e), 'Parameters were not loaded')

        error = []
        cols = self.tableWidget.columnCount()
        for row in range(self.tableWidget.rowCount()):
            error = np.append(error, [self.itemCheck(self.tableWidget.item(row, col), silent=True) for col in range(1, cols-1)])
        # if True in error:
        #     self.errorBox("Bad parameters", "Bad values")
        #     return

    def ExportGuess(self):
        path = self.initialDir
        fname, _filter = QFileDialog.getSaveFileName(self, 'Save file', path,"Initial guess (*.csv)")

        if not fname:
            return
        cols = ['labels', 'freq', 'freq_min', 'freq_max' ,'intens', 'width']
        rows = self.tableWidget.rowCount()
        guess = pd.DataFrame()
        try:
            for i, c in enumerate(cols):
                guess[c] = [self.tableWidget.item(row, i+1).text() for row in range(rows)]
            guess['shape'] = [self.tableWidget.cellWidget(row, 7).currentText().strip()[0] for row in range(rows)]
            guess.to_csv(fname, index=None)
            self.statusbar.showMessage("Initial guess file saved succesfully", 2000)
        except Exception as e:
            self.errorBox('Error\n{}'.format(e), 'Parameters were not loaded')

    def readConfig(self):

        self.settings = QSettings("Raman Deconvolution")
        self.initialDir = self.settings.value('directory', '/home/cat/')
        self.restoreGeometry(self.settings.value('MainWindow/geometry', self.saveGeometry()))
        self.restoreState(self.settings.value('MainWindow/state', self.saveState()))
        self.actionToolbar.setChecked(strtobool(self.settings.value('MainWindow/toolbar', 'true')))
        # self.actionGuess.setChecked(strtobool(self.settings.value('MainWindow/dockGuess', 'true')))
        # self.actionOutput.setChecked(strtobool(self.settings.value('MainWindow/dockOut', 'true')))
        # self.dockGuess.setVisible(self.actionGuess.isChecked())
        # self.dockOut.setVisible(self.actionOutput.isChecked())

        #read the configuration file
        self.config = configparser.ConfigParser()
        if len(self.config.read(self.path+'/config/config.ini')):
               self.degree = int(self.config['DEFAULT']['degree'])
               self.threshold = float(self.config['DEFAULT']['threshold'])
        #        font_size = int(config['DEFAULT']['font_size'])
               self.peakLimits = Limits(int(self.config['PEAK']['low']), int(self.config['PEAK']['high']))
        #load fitting parameters
        self.LoadGuess(fname = self.path + '/config/initialData.csv')

    def New(self):
        if self.changed:
            result = QMessageBox.question(self,
                    "Unsaved file...",
                    "Do you want to save the data before exiting?",
                    QMessageBox.Yes| QMessageBox.No |QMessageBox.Cancel)
            if result == QMessageBox.Yes:
                self.Save()
            elif result == QMessageBox.Cancel:
                return
        path = self.initialDir
        fname, _filter = QFileDialog.getOpenFileName(self, 'Open file', path,"Text files (*.txt *.dat);; Wire data files (*.wdf);; All files (*.*)")
        if not fname:
            return
        elif self.initialDir!=ntpath.dirname(fname):
            self.initialDir=ntpath.dirname(fname) #update the initial directory for the Open/Save dialog
            self.settings.setValue('directory', self.initialDir)
        if fname[-3:] == 'wdf':
            convert(fname)
            fname = fname[:-3]+'txt'
        try:
            # tmp = np.loadtxt(fname)
            # self.data.setData(tmp[:,0], tmp[:,1])
            self.data.loadData(fname)
            # self.statusbar.showMessage("Data loaded", 2000)
            self.Plot(self.data.X, self.data.Y, 'Experimental data')
            self.setWindowTitle( 'Raman Deconvolution - ' + ntpath.basename(fname))
            self.changed = False
            self.textOut.clear()
            self.textOut.setText(self.header)
        except Exception as e:
            self.errorBox('Could not load the file\n{}'.format(e), 'I/O error')
            self.statusbar.showMessage("Error loading the file", 2000)

    def Save(self):
        if not np.shape(self.data.X):
            self.statusbar.showMessage("No data...", 2000)
            return
        path = self.initialDir
        fname, _filter = QFileDialog.getSaveFileName(self, 'Save file', path,"Text files (*.txt);; Comma separated values (*.csv)")
        delimiter = '\t'
        if not fname:
            return
        if _filter == "Text files (*.txt)" and fname[-3:]!='txt':
            fname += '.txt'
        if _filter == "Comma separated values (*.csv)" and fname[-3:]!='csv':
            fname += '.csv'
            delimiter = ','

        data, comments = self.data.getData()
        if hasattr(self.fit, 'report'):
            comments += self.fit.report
            data = pd.concat([data, self.fit.peaks], ignore_index=True, axis = 1)
        f = open(fname, 'w')
        f.close()
        with open(fname, 'a') as f:
            [f.write(s) for s in comments]
            data.to_csv(f, index = None, sep = delimiter)

        self.statusbar.showMessage('File {} saved'.format(fname), 3000)


        if self.changed:
            self.changed =False
            self.setWindowTitle(self.windowTitle()[:-1])

    def Plot(self, X, Y, label, clear = True, limits=False):
        if clear:
            self.subplot.clear()
        if label == 'Baseline':
            line, = self.subplot.plot(X, Y, 'r--', label = label)
        else:
            line, = self.subplot.plot(X, Y, label = label)
        self.subplot.set_xlim(np.min(X), np.max(X))
        if limits:
            self.subplot.set_ylim(0.9*np.min(Y), 1.1*np.max(Y))
        self.plotAdjust()
        return line

    def errorBox(self, message, title="Error"):
        self.error = True
        self.statusbar.showMessage(message, 5000)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def Crop(self):
        if not np.shape(self.data.X):
            self.errorBox('There is no data', 'No data...')
            return
        _min = np.min(self.data.X)
        _max = np.max(self.data.X)
        dialog = CropDialog(_min, _max)
        result = dialog.exec_()
        params = dialog.getData()
        try:
            _min = int(params[0])
        except ValueError:
            self.statusbar.showMessage("Wrong value...setting to default", 3000)
        try:
            _max = int(params[1])
        except ValueError:
            self.statusbar.showMessage("Wrong value...setting to default", 3000)
        self.data.crop(_min, _max)
        self.statusbar.showMessage("Data cropped", 3000)
        self.Plot(self.data.X, self.data.current, "Experimental data")
        if self.peakLimits.min < self.data.X[0]:
            self.peakLimits.min = self.data.X[0]
        if self.peakLimits.max > self.data.X[-1]:
            self.peakLimits.max = self.data.X[-1]
        if not self.changed:
            self.changed = True
            self.setWindowTitle(self.windowTitle()+'*')

    def tableItemRightClicked(self, QPos):
        self.listMenu= QMenu()
        menu_item_2 = self.listMenu.addAction("Preview band")
        menu_item_3 = self.listMenu.addAction("Preview selected bands")
        self.listMenu.addSeparator()
        if self.tableWidget.item(self.tableWidget.currentRow(), 0).checkState() & Qt.Checked:
            menu_item_0 = self.listMenu.addAction("Don't use for deconvolution")
        else:
            menu_item_0 = self.listMenu.addAction("Use for deconvolution")
        menu_item_1 = self.listMenu.addAction("Use all")
        self.listMenu.addSeparator()
        menu_item_4 = self.listMenu.addAction("Add row")
        menu_item_5 = self.listMenu.addAction("Remove row")
        menu_item_0.triggered.connect(lambda: self.tableRowUse(self.tableWidget.currentRow()))
        menu_item_1.triggered.connect( self.tableUseAll)
        menu_item_2.triggered.connect( lambda: self.previewBand(self.tableWidget.currentRow()))
        menu_item_3.triggered.connect( self.previewAll)
        menu_item_4.triggered.connect(self.addRow)
        menu_item_5.triggered.connect( lambda: self.tableWidget.removeRow(self.tableWidget.currentRow()))
        parentPosition = self.tableWidget.mapToGlobal(QPoint(0, 0))
        self.listMenu.move(parentPosition + QPos)
        self.listMenu.show()

    def addRow(self):
        rows = self.tableWidget.rowCount()
        self.tableWidget.insertRow(rows)
        self.tableWidget.setItem(rows, 0, QTableWidgetItem(''))
        self.tableWidget.item(rows, 0).setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        self.tableWidget.item(rows, 0).setCheckState(Qt.Checked)
        [self.tableWidget.setItem(rows, j, QTableWidgetItem(str('--'))) for j in range(1, 7)]

        combo = QComboBox()
        [combo.addItem('  '+s) for s in ['Lorentzian', 'Gaussian', 'Voigt', 'BWF']]
        self.tableWidget.setCellWidget(rows, 7, combo)

    def itemCheck(self, item, **kwargs):
        col = item.column()
        value = item.text()
        error = False
        bg = self.tableWidget.item(0,0).background()
        if col in range(2, 7):
            try:
                float(value)
            except ValueError:
                error = True
                bg = QBrush(Qt.red)
                if 'silent' not in kwargs:
                    self.statusbar.showMessage('Not a valid number', 2000)
        elif col == 7:
            if value not in ['Gaussian', 'Lorentzian', 'Voigt', 'BWF']:
                error = True
                bg = QBrush(Qt.red)
                if 'silent' not in kwargs:
                    self.statusbar.showMessage('Unknown shape', 2000)
        item.setBackground(bg)
        item.setSelected(False)
        return error


    def previewBand(self, row):
        if not np.shape(self.data.X):
            self.errorBox('There is no data', 'No data...')
            return
        cols = self.tableWidget.columnCount()
        params =[self.tableWidget.item(row, col).text() for col in range(1, cols-1)]
        shape = self.tableWidget.cellWidget(row, cols-1).currentText().strip()[0]
        label = params[0]
        params = np.asarray([params[4], params[5], params[1]]).astype(float)
        if shape == 'V':
            params = np.append(params, 0.5)
        elif shape == 'B':
            params = np.append(params, 0.02)
        self.Plot(self.data.X, self.data.current, "Experimental data")
        self.subplot.plot(self.data.X, FIT.Peak(FIT, self.data.X, *params, shape = shape), label = label)
        self.subplot.legend()
        self.canvas.draw()

    def previewAll(self):
        if not np.shape(self.data.X):
            self.errorBox('There is no data', 'No data...')
            return
        self.subplot.clear()
        self.subplot.plot(self.data.X, self.data.current, label = 'Experimental data')
        cols = self.tableWidget.columnCount()
        rows = self.tableWidget.rowCount()
        cumulative = np.zeros(len(self.data.X))
        intensity = [float(self.tableWidget.item(row, 5).text()) for row in range(rows) if self.tableWidget.item(row, 0).checkState()&Qt.Checked]
        norm = max(self.data.current)/max(intensity)
        for row in range(rows):
            if self.tableWidget.item(row, 0).checkState() & Qt.Checked:
                error = [self.itemCheck(self.tableWidget.item(row, col), silent=True) for col in range(1, cols-1)]
                if True in error:
                    self.errorBox("Bad parameters", "Bad values")
                    return
                params =[float(self.tableWidget.item(row, col).text()) for col in [5, 6, 2]]
                params[0] *= norm
                label = self.tableWidget.item(row, 1).text()
                shape = self.tableWidget.cellWidget(row, 7).currentText().strip()[0]
                if shape == 'V':
                    params = np.append(params, 0.5)
                elif shape == 'B':
                    params = np.append(params, 0.02)
                p = FIT.Peak(FIT, self.data.X, *params, shape = shape)
                cumulative += p
                self.subplot.plot(self.data.X, p, label = label)
        self.subplot.plot(self.data.X, cumulative, 'r--', label = "Cumulative")
        self.plotAdjust()


    def tableUseAll(self):
        [self.tableWidget.item(row, 0).setCheckState(Qt.Checked) for row in range(self.tableWidget.rowCount())]

    def tableRowUse(self, row):
        cols = self.tableWidget.columnCount()
        if self.tableWidget.item(row, 0).checkState() & Qt.Checked:
            self.tableWidget.item(row, 0).setCheckState(Qt.Unchecked)
        else:
            self.tableWidget.item(row, 0).setCheckState(Qt.Checked)



    def about(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Version v1.01α \nMade by CAT \nLille, 2020")
        msg.setWindowTitle("About")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def closeEvent(self, event):

        self.settings.setValue('MainWindow/geometry', self.saveGeometry())
        self.settings.setValue('MainWindow/state', self.saveState())
        self.settings.setValue('MainWindow/toolbar', self.actionToolbar.isChecked())
        # self.settings.setValue('MainWindow/dockGuess', self.actionGuess.isChecked())
        # self.settings.setValue('MainWindow/dockOut', self.actionOutput.isChecked())
        if self.changed:
            result = QMessageBox.question(self,
                    "Unsaved file...",
                    "Do you want to save the data before exiting?",
                    QMessageBox.Yes| QMessageBox.No |QMessageBox.Cancel)
            if result == QMessageBox.Yes:
                self.Save()
                event.ignore()
            elif result == QMessageBox.Cancel:
                event.ignore()
            else:
                event.accept()


if __name__ == '__main__':
    mp.set_start_method('spawn')
    app = QApplication([sys.argv])
    application = RD()
    application.show()
    app.exec()


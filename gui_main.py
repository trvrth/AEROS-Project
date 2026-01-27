# gui_main.py
import sys
import matlab.engine
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel,
    QComboBox, QFormLayout, QLineEdit, QHBoxLayout, QMessageBox,
    QInputDialog
)
from PyQt5.QtCore import QTimer
from scipy.io import loadmat
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np

from utils import load_json, save_json
from editors import AsteroidEditWindow, ThrusterEditWindow

class AsteroidSimGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.eng = None
        self.t = self.x = self.y = None
        self.index = 0

        self.asteroid_file = "asteroids.json"
        self.thruster_file = "thrusters.json"

        # default (built-in) profiles - (can't be changed by user)
        self.default_asteroids = {
            "Ceres": {"mass": 9.4e20, "radius": 473000, "horizons_id": "1"},
            "Bennu": {"mass": 7.8e10, "radius": 245, "horizons_id": "101955"}
        }
        self.default_thrusters = {
            "Ion Drive": {"thrust": 0.5, "array_num": 1, "sc_num": 1, "dt": 3600, "mass_fuel": 1000.0, "mass_sc": 100.0, "Isp": 2500.0},
            "Chemical": {"thrust": 5000.0, "array_num": 1, "sc_num": 1, "dt": 3600, "mass_fuel": 10000.0, "mass_sc": 1000.0, "Isp": 300.0}
        }

        # load or create files
        self.asteroids = load_json(self.asteroid_file, self.default_asteroids)
        self.thrusters = load_json(self.thruster_file, self.default_thrusters)

        # builtin protection sets
        self.builtin_asteroid_names = set(self.default_asteroids.keys())
        self.builtin_thruster_names = set(self.default_thrusters.keys())

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Asteroid Deflection Simulator")

        # Profile selectors
        self.asteroid_label = QLabel("Asteroid Profile:")
        self.asteroid_select = QComboBox()
        self.asteroid_select.addItems(list(self.asteroids.keys()) + ["Custom"])
        self.asteroid_select.currentTextChanged.connect(self.load_asteroid)

        self.thruster_label = QLabel("Thruster Profile:")
        self.thruster_select = QComboBox()
        self.thruster_select.addItems(list(self.thrusters.keys()) + ["Custom"])
        self.thruster_select.currentTextChanged.connect(self.load_thruster)

        # Edit buttons
        self.edit_asteroid_btn = QPushButton("Edit Asteroid Parameters")
        self.edit_thruster_btn = QPushButton("Edit Thruster Parameters")
        self.edit_asteroid_btn.clicked.connect(self.open_asteroid_editor)
        self.edit_thruster_btn.clicked.connect(self.open_thruster_editor)

        # Inputs - expanded to include ODE_Handle parameters and Horizons inputs
        self.mass_input = QLineEdit()
        self.radius_input = QLineEdit()
        self.horizons_id_input = QLineEdit()
        self.h_start_input = QLineEdit()
        self.h_stop_input = QLineEdit()
        self.h_step_input = QLineEdit()

        # mission / thruster / ODE params
        self.thrust_input = QLineEdit()
        self.array_num_input = QLineEdit()
        self.sc_num_input = QLineEdit()
        self.dt_input = QLineEdit()
        self.mass_fuel_input = QLineEdit()
        self.mass_sc_input = QLineEdit()
        self.Isp_input = QLineEdit()
        self.standoff_input = QLineEdit()       # d
        self.theta_input = QLineEdit()          # divergence angle
        self.orbit_window_input = QLineEdit()
        self.infront_input = QLineEdit()        # -1 or 1

        form = QFormLayout()
        form.addRow("Asteroid Mass (M_A, kg):", self.mass_input)
        form.addRow("Asteroid Radius (R_A, m):", self.radius_input)
        form.addRow("Horizons ID:", self.horizons_id_input)
        form.addRow("Horizons Start Date (e.g. 2032-Jul-06):", self.h_start_input)
        form.addRow("Horizons Stop Date (e.g. 2032-Jul-07):", self.h_stop_input)
        form.addRow("Horizons Step Size (e.g. 1 d):", self.h_step_input)

        form.addRow("Thrust (N):", self.thrust_input)
        form.addRow("Array Number (int):", self.array_num_input)
        form.addRow("Number of SC (int):", self.sc_num_input)
        form.addRow("Time step dt (s):", self.dt_input)
        form.addRow("Mass fuel per SC (kg):", self.mass_fuel_input)
        form.addRow("Mass spacecraft (kg):", self.mass_sc_input)
        form.addRow("Isp (s):", self.Isp_input)

        form.addRow("Standoff distance d (m):", self.standoff_input)
        form.addRow("Ion beam divergence theta (deg):", self.theta_input)
        form.addRow("Orbit window (deg):", self.orbit_window_input)
        form.addRow("Infront (1 or -1):", self.infront_input)

        # Action buttons
        self.run_button = QPushButton("Run MATLAB Simulation")
        self.animate_button = QPushButton("Animate Trajectory")
        self.save_button = QPushButton("Save Custom Profile")
        self.status_label = QLabel("Ready.")

        self.run_button.clicked.connect(self.run_simulation)
        self.animate_button.clicked.connect(self.animate_plot)
        self.save_button.clicked.connect(self.save_profile)

        # Plot area
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.fig)
        self.line, = self.ax.plot([], [], 'b-')

        # Layout assembly
        layout = QVBoxLayout()
        layout.addWidget(self.asteroid_label)
        layout.addWidget(self.asteroid_select)
        layout.addWidget(self.edit_asteroid_btn)
        layout.addWidget(self.thruster_label)
        layout.addWidget(self.thruster_select)
        layout.addWidget(self.edit_thruster_btn)
        layout.addLayout(form)

        hlayout = QHBoxLayout()
        hlayout.addWidget(self.run_button)
        hlayout.addWidget(self.animate_button)
        hlayout.addWidget(self.save_button)
        layout.addLayout(hlayout)

        layout.addWidget(self.status_label)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        # Timer for animation
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)

        # initial load
        self.refresh_asteroid_dropdown()
        self.refresh_thruster_dropdown()
        self.load_asteroid(self.asteroid_select.currentText())
        self.load_thruster(self.thruster_select.currentText())

    # Dropdown refresh helpers
    def refresh_asteroid_dropdown(self):
        current = self.asteroid_select.currentText()
        self.asteroid_select.clear()
        names = list(self.asteroids.keys())
        self.asteroid_select.addItems(names + ["Custom"])
        idx = self.asteroid_select.findText(current)
        if idx >= 0:
            self.asteroid_select.setCurrentIndex(idx)

    def refresh_thruster_dropdown(self):
        current = self.thruster_select.currentText()
        self.thruster_select.clear()
        names = list(self.thrusters.keys())
        self.thruster_select.addItems(names + ["Custom"])
        idx = self.thruster_select.findText(current)
        if idx >= 0:
            self.thruster_select.setCurrentIndex(idx)

    # Editor launch
    def open_asteroid_editor(self):
        name = self.asteroid_select.currentText()
        if name == "Custom":
            QMessageBox.information(self, "Info", "Select a saved asteroid profile to edit.")
            return
        if name in self.builtin_asteroid_names:
            QMessageBox.information(self, "Protected", f"'{name}' is a built-in profile and cannot be edited or deleted.")
            return
        dlg = AsteroidEditWindow(self, self.asteroids[name], name, editable=True)
        dlg.exec_()

    def open_thruster_editor(self):
        name = self.thruster_select.currentText()
        if name == "Custom":
            QMessageBox.information(self, "Info", "Select a saved thruster profile to edit.")
            return
        if name in self.builtin_thruster_names:
            QMessageBox.information(self, "Protected", f"'{name}' is a built-in profile and cannot be edited or deleted.")
            return
        dlg = ThrusterEditWindow(self, self.thrusters[name], name, editable=True)
        dlg.exec_()

    # Profile loading
    def load_asteroid(self, name):
        """Loads asteroid parameters into the GUI fields."""
        if name == "Custom":
            # clear fields
            self.mass_input.clear()
            self.radius_input.clear()
            self.horizons_id_input.clear()
            return
    
        if name not in self.asteroids:
            return
    
        profile = self.asteroids[name]
    
        # ---- ALWAYS INSERT RAW VALUES, NEVER MATLAB OBJECTS ----
        self.mass_input.setText(str(profile.get("mass", "")))
        self.radius_input.setText(str(profile.get("radius", "")))
        self.horizons_id_input.setText(str(profile.get("horizons_id", "")))
    
        # Do NOT touch Horizons start/stop/step here


    def load_thruster(self, name):
        """Loads thruster / mission parameters into GUI fields."""
        if name == "Custom":
            # clear fields
            self.thrust_input.clear()
            self.array_num_input.clear()
            self.sc_num_input.clear()
            self.dt_input.clear()
            self.mass_fuel_input.clear()
            self.mass_sc_input.clear()
            self.Isp_input.clear()
            return
    
        if name not in self.thrusters:
            return
    
        profile = self.thrusters[name]
    
        # ---- ALWAYS INSERT RAW VALUES ----
        self.thrust_input.setText(str(profile.get("thrust", "")))
        self.array_num_input.setText(str(profile.get("array_num", "")))
        self.sc_num_input.setText(str(profile.get("sc_num", "")))
        self.dt_input.setText(str(profile.get("dt", "")))
        self.mass_fuel_input.setText(str(profile.get("mass_fuel", "")))
        self.mass_sc_input.setText(str(profile.get("mass_sc", "")))
        self.Isp_input.setText(str(profile.get("Isp", "")))


    # Save profile from main form (when 'Custom' selected)
    def save_profile(self):
        # minimal validation for main form
        try:
            # check numeric fields if non-empty
            if self.mass_input.text().strip() != "":
                _ = float(self.mass_input.text())
            if self.radius_input.text().strip() != "":
                _ = float(self.radius_input.text())
        except Exception:
            QMessageBox.warning(self, "Error", "Mass and radius must be numeric.")
            return

        asteroid_name = self.asteroid_select.currentText()
        thruster_name = self.thruster_select.currentText()

        if asteroid_name == "Custom":
            new_name = self.get_new_name("asteroid")
            if new_name:
                self.asteroids[new_name] = {}
                if self.mass_input.text().strip() != "":
                    self.asteroids[new_name]["mass"] = float(self.mass_input.text())
                if self.radius_input.text().strip() != "":
                    self.asteroids[new_name]["radius"] = float(self.radius_input.text())
                if self.horizons_id_input.text().strip() != "":
                    self.asteroids[new_name]["horizons_id"] = self.horizons_id_input.text().strip()
                if self.h_start_input.text().strip() != "":
                    self.asteroids[new_name]["h_start"] = self.h_start_input.text().strip()
                if self.h_stop_input.text().strip() != "":
                    self.asteroids[new_name]["h_stop"] = self.h_stop_input.text().strip()
                if self.h_step_input.text().strip() != "":
                    self.asteroids[new_name]["h_step"] = self.h_step_input.text().strip()
                save_json(self.asteroid_file, self.asteroids)
                self.refresh_asteroid_dropdown()
                QMessageBox.information(self, "Saved", f"Asteroid '{new_name}' saved.")

        if thruster_name == "Custom":
            new_name = self.get_new_name("thruster")
            if new_name:
                self.thrusters[new_name] = {}
                if self.thrust_input.text().strip() != "":
                    self.thrusters[new_name]["thrust"] = float(self.thrust_input.text())
                if self.array_num_input.text().strip() != "":
                    self.thrusters[new_name]["array_num"] = int(float(self.array_num_input.text()))
                if self.sc_num_input.text().strip() != "":
                    self.thrusters[new_name]["sc_num"] = int(float(self.sc_num_input.text()))
                if self.dt_input.text().strip() != "":
                    self.thrusters[new_name]["dt"] = float(self.dt_input.text())
                if self.mass_fuel_input.text().strip() != "":
                    self.thrusters[new_name]["mass_fuel"] = float(self.mass_fuel_input.text())
                if self.mass_sc_input.text().strip() != "":
                    self.thrusters[new_name]["mass_sc"] = float(self.mass_sc_input.text())
                if self.Isp_input.text().strip() != "":
                    self.thrusters[new_name]["Isp"] = float(self.Isp_input.text())
                save_json(self.thruster_file, self.thrusters)
                self.refresh_thruster_dropdown()
                QMessageBox.information(self, "Saved", f"Thruster '{new_name}' saved.")

    def get_new_name(self, kind):
        new_name, ok = QInputDialog.getText(self, "New Profile", f"Enter {kind} name:")
        if ok and new_name.strip() != "":
            return new_name.strip()
        return None

    # Run MATLAB Simulation: call get_horizons_rv then ODE_Handle
    def run_simulation(self):
        self.status_label.setText("Running MATLAB simulation...")
        QApplication.processEvents()
        try:
            if self.eng is None:
                self.eng = matlab.engine.start_matlab()

            # Gather Horizons inputs
            target_id = self.horizons_id_input.text().strip()
            start_date = self.h_start_input.text().strip()
            stop_date = self.h_stop_input.text().strip()
            step_size = self.h_step_input.text().strip()

            if not target_id or not start_date or not stop_date or not step_size:
                raise ValueError("Horizons inputs (ID / start / stop / step) must be provided.")

            # call get_horizons_rv to get rA0,vA0 (1x6 vector)
            state_vec_mat = self.eng.get_horizons_rv(target_id, start_date, stop_date, step_size, nargout=1)
            state_vec = np.array(state_vec_mat).astype(float).flatten()
            
            # state_vec is 1x6 MATLAB array: [x y z vx vy vz]
            rA0 = state_vec[:3]
            vA0 = state_vec[3:]
            
            rA0_mat = matlab.double([rA0.tolist()])
            vA0_mat = matlab.double([vA0.tolist()])

            # Gathers ODE inputs
            thrust      = float(self.thrust_input.text())
            array_num   = float(self.array_num_input.text())
            sc_num      = float(self.sc_num_input.text())
            dt          = float(self.dt_input.text())
            mass_fuel   = float(self.mass_fuel_input.text())
            mass_sc     = float(self.mass_sc_input.text())
            Isp         = float(self.Isp_input.text())
            d           = float(self.standoff_input.text())
            theta       = float(self.theta_input.text())
            orbit_win   = float(self.orbit_window_input.text())
            infront     = float(self.infront_input.text())
            M_A         = float(self.mass_input.text())
            R_A         = float(self.radius_input.text())

            # Call ODE_Handle with nargout=9 (matching your MATLAB signature)
            out = self.eng.ODE_Handle_GUI(
                                        rA0,
                                        vA0,
                                        thrust,
                                        array_num,
                                        sc_num,
                                        dt,
                                        mass_fuel,
                                        mass_sc,
                                        Isp,
                                        M_A,
                                        R_A,
                                        d,
                                        theta,
                                        orbit_win,
                                        infront,
                                        True,
                                        nargout=9
                                    )


            # Unpack MATLAB outputs: t_all, r_all, v_all, delr, delT, Z_all, DV_tot, a_all, e_all
            t_all = list(out[0])
            r_all = out[1]   # MATLAB Nx3 array-like
            # convert r_all to Python lists for x,y
            # r_all is an array of rows; handle shape robustly
            x_vals = []
            y_vals = []
            try:
                # r_all may be list-of-lists or matlab type; iterate rows
                for row in r_all:
                    row_list = list(row)
                    x_vals.append(float(row_list[0]))
                    y_vals.append(float(row_list[1]))
            except Exception:
                # fallback: try to index directly
                r_py = list(r_all)
                for i in range(len(r_py[0])):
                    x_vals.append(float(r_py[0][i]))
                    y_vals.append(float(r_py[1][i]))

            self.t = t_all
            self.x = x_vals
            self.y = y_vals

            self.status_label.setText("Simulation complete. Ready to animate.")
        except Exception as e:
            self.status_label.setText("Simulation failed.")
            QMessageBox.critical(self, "Error", str(e))

    # Animation
    def animate_plot(self):
        if self.t is None:
            self.status_label.setText("Run simulation first.")
            return
        self.ax.clear()
        self.ax.set_xlim(min(self.x), max(self.x))
        self.ax.set_ylim(min(self.y), max(self.y))
        self.line, = self.ax.plot([], [], "r-")
        self.index = 0
        self.timer.start(30)
        self.status_label.setText("Animating...")

    def update_plot(self):
        if self.index < len(self.t):
            self.line.set_data(self.x[:self.index], self.y[:self.index])
            self.canvas.draw()
            self.index += max(1, int(len(self.t)/200))  # speed control
        else:
            self.timer.stop()
            self.status_label.setText("Animation complete.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = AsteroidSimGUI()
    gui.show()
    sys.exit(app.exec_())

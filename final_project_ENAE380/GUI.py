"""
GUI.py

Trevor Thomas

ENAE 380

Section: 0106

12/14/25

"""

import sys
import subprocess
import scipy.io
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel,
    QComboBox, QFormLayout, QLineEdit, QHBoxLayout, QMessageBox,
    QInputDialog, QTextEdit, QDialog
)
import matplotlib.pyplot as plt

from utils import load_json, save_json
from editors import AsteroidEditWindow, ThrusterEditWindow, SpacecraftEditWindow
from utils_gui import run_matlab_batch

class AsteroidSimGUI(QWidget):
    
    def __init__(self):
        """
        Initializes the AsteroidSimGUI application state and loads in/creates 
        persistent JSON data files.
        
        This class serves as the central composition root for the application,
        owning all persistent data structures, JSON configuration files,
        and application state.
        
        The editor and util modules reference this class as their authoritative
        source of data via parent ownership.
        
        This constructor:
            - Initializes the Qt base class
            
            - Defines persistent JSON storage files for asteroid, thruster, spacecraft,
              and scenario profile data
              
            - Defines built-in (protected) default profiles for validated reference cases
            
            - Loads existing JSON data or creates new files with default profiles
            
            - Establishes protection sets to prevent modification of built-in profiles
            
            - Runs the GUI constructor to initialize all Qt widgets and layout of GUI
        
        """
        # Creates superclass
        super().__init__()

        # filenames
        self.asteroid_file = "asteroids.json"
        self.thruster_file = "thrusters.json"
        self.spacecraft_file = "spacecraft.json"
        self.scenario_file = "scenarios.json"

        # default (built-in) profiles - (can't be changed by user)
        self.default_asteroids = {
            "2024 PDC25": {
                           "mass": 6.41e9,
                           "radius": 75,
                           "horizons_id": "2024 PDC25",
                            "h_start": "2032-07-06",
                            "h_stop": "2032-07-07",
                            "h_step": "1d"
                            },
            "2021 PDC": {
                        "mass": 9.1e9,
                        "radius": 75.0,
                        "horizons_id": "-937014",
                        "h_start": "2021-10-19",
                        "h_stop": "2021-10-20",
                        "h_step": "1d"
                        },
        }
        
        self.default_thrusters = {
            "Next-C Ion Thruster": {
                                    "thrust": 0.235,
                                    "Isp": 4178,
                                    "Beam Divergence": 5},
            "T-220HT": {
                                   "thrust": 0.75,
                                   "Isp": 2500.0,
                                   "Beam Divergence": 28.0
                                   },
        }

        self.default_spacecraft = {
            "Single Array and Craft": {
                                "array_num": 1,
                                "sc_num": 1,
                                "mass_fuel": 2203.0,
                                "mass_sc": 5867.0
                                # "solar_power": 5000.0  # Watts, optional future field
            },
            
            "3 Array and 2 Craft": {
                                "array_num": 3,
                                "sc_num": 2,
                                "mass_fuel": 2203.0,
                                "mass_sc": 5867.0
                            },
        }
        
        self.default_scenario = {
            "Test 1":{
                        "profiles": {
                            "asteroid": "2024 PDC25",
                            "thruster": "Next-C Ion Thruster",
                            "spacecraft": "3 Array and 2 Craft"
                        },
                        
                        "asteroid_data": {
                            "mass": "6410000000.0",
                            "radius": "75",
                            "horizons_id": "2024 PDC25",
                            "h_start": "2032-07-05",
                            "h_stop": "2032-07-06",
                            "h_step": "1d"
                        },
                        
                        "thruster_data": {
                            "thrust": "0.235",
                            "Isp": "4178",
                            "theta": "5"
                        },
                        
                        "spacecraft_data": {
                            "array_num": "3",
                            "sc_num": "2",
                            "mass_fuel": "2203.0",
                            "mass_sc": "5867.0"
                        },
                        
                        "mission_data": {
                            "dt": "3600",
                            "standoff": "1000",
                            "orbit_window": "180",
                            "infront": "1"
                        },
                     }
            }

        # load/create files
        self.asteroids = load_json(self.asteroid_file, self.default_asteroids)
        self.thrusters = load_json(self.thruster_file, self.default_thrusters)
        self.spacecraft = load_json(self.spacecraft_file, self.default_spacecraft)
        self.scenarios = load_json(self.scenario_file, self.default_scenario)

        # builtin protection sets
        self.builtin_asteroid_names = set(self.default_asteroids.keys())
        self.builtin_thruster_names = set(self.default_thrusters.keys())
        self.builtin_spacecraft_names = set(self.default_spacecraft.keys())

        self.initUI()

    def initUI(self):
        """
        Constructs and initializes the graphical user interface for the simulator.

        This UI constructor method:
        - Creates all Qt widgets used for user interaction, including selectors,
          input fields, action buttons, and labels
          
        - Connects widget signals to their corresponding event handlers
        
        - Organizes widgets using form, vertical, and horizontal layouts
        
        - Applies the completed layout to the main application window
        
        - Loads/refreshes profile selection dropdowns from persistent JSON data
        
        - Loads the currently selected profiles to initialize input fields
        
        """
        self.setWindowTitle("Asteroid Deflection Simulator")

        # Asteroid Selectors
        self.asteroid_label = QLabel("Asteroid Profile:")
        self.asteroid_select = QComboBox() #drop down box

        # Thruster Selectors
        self.thruster_label = QLabel("Thruster Profile:")
        self.thruster_select = QComboBox() #drop down box

        # Spacecraft Selectors
        self.spacecraft_label = QLabel("Spacecraft Profile:")
        self.spacecraft_select = QComboBox() #drop down box

        # Scenario selector
        self.scenario_label = QLabel("Scenario:")
        self.scenario_select = QComboBox() #drop down box
        
        # Connects selectors to input form to refresh them when selection changes
        self.asteroid_select.currentTextChanged.connect(self.load_asteroid)
        self.thruster_select.currentTextChanged.connect(self.load_thruster)
        self.spacecraft_select.currentTextChanged.connect(self.load_spacecraft)
        self.scenario_select.currentTextChanged.connect(self.load_scenario)

        # Edit buttons
        self.edit_asteroid_btn = QPushButton("Edit Asteroid Parameters")
        self.edit_thruster_btn = QPushButton("Edit Thruster Parameters")
        self.edit_spacecraft_btn = QPushButton("Edit Spacecraft Arrangement")
        
        # Connectors to event (when button is clicked)
        self.edit_asteroid_btn.clicked.connect(self.open_asteroid_editor)
        self.edit_thruster_btn.clicked.connect(self.open_thruster_editor)
        self.edit_spacecraft_btn.clicked.connect(self.open_spacecraft_editor)

        # Asteroid Inputs
        self.mass_input = QLineEdit()
        self.radius_input = QLineEdit()
        
        # JPL Horizons Input
        self.horizons_id_input = QLineEdit()
        self.h_start_input = QLineEdit()
        self.h_stop_input = QLineEdit()
        self.h_step_input = QLineEdit()

        # Thruster Input
        self.thrust_input = QLineEdit()
        self.Isp_input = QLineEdit()
        
        # Spacecraft Input
        self.array_num_input = QLineEdit()  # how many thruster arrays
        self.sc_num_input = QLineEdit()     # how many spacecraft
        self.dt_input = QLineEdit()         # time step of sim
        self.mass_fuel_input = QLineEdit()  # Just fuel mass
        self.mass_sc_input = QLineEdit()    # Total space craft mass
        
        # Mission Specific Inputs
        self.standoff_input = QLineEdit()       # d
        self.theta_input = QLineEdit()          # beam divergence angle
        self.orbit_window_input = QLineEdit()   # angle about perihelion
        self.infront_input = QLineEdit()        # -1 or 1

        form = QFormLayout()
        # Asteroid GUI Inputs
        form.addRow("Asteroid Mass (M_A, kg):", self.mass_input)
        form.addRow("Asteroid Radius (R_A, m):", self.radius_input)
        form.addRow("Horizons ID:", self.horizons_id_input)
        form.addRow("Horizons Start Date (e.g. 2032-Jul-06):", self.h_start_input)
        form.addRow("Horizons Stop Date (e.g. 2032-Jul-07):", self.h_stop_input)
        form.addRow("Horizons Step Size (e.g. 1d):", self.h_step_input)
        
        # Thruster GUI Inputs
        form.addRow("Thrust (N):", self.thrust_input)
        form.addRow("Isp (s):", self.Isp_input)
        form.addRow("Ion beam divergence theta (deg):", self.theta_input)

        # Spacecraft GUI Inputs
        form.addRow("Array Number (int):", self.array_num_input)
        form.addRow("Number of SC (int):", self.sc_num_input)
        form.addRow("Mass fuel per SC (kg):", self.mass_fuel_input)
        form.addRow("Mass spacecraft (kg):", self.mass_sc_input)

        # Mission GUI Inputs
        form.addRow("Time step dt (s):", self.dt_input)
        form.addRow("Standoff distance d (m):", self.standoff_input)
        form.addRow("Orbit window (deg):", self.orbit_window_input)
        form.addRow("Infront (1 [behind] or -1 [infront]):", self.infront_input)

        # Action buttons
        self.run_button = QPushButton("Run MATLAB Simulation")
        self.save_scenario_button = QPushButton("Save Scenario")
        self.status_label = QLabel("Ready.")

        self.run_button.clicked.connect(self.run_simulation)
        self.save_scenario_button.clicked.connect(self.save_scenario)

        # ------ UI Layout --------
        layout = QVBoxLayout() # main vertical layout
        
        # Asteroid Button Layout
        layout.addWidget(self.asteroid_label)
        layout.addWidget(self.asteroid_select)
        layout.addWidget(self.edit_asteroid_btn)
        
        # Thruster Button Layout
        layout.addWidget(self.thruster_label)
        layout.addWidget(self.thruster_select)
        layout.addWidget(self.edit_thruster_btn)
        
        # Spacecraft Button Layout
        layout.addWidget(self.spacecraft_label)
        layout.addWidget(self.spacecraft_select)
        layout.addWidget(self.edit_spacecraft_btn)
        
        # Scenario Button Layout
        layout.addWidget(self.scenario_label)
        layout.addWidget(self.scenario_select)
        
        # Adds input form layout/labels to UI layout
        layout.addLayout(form)

        hlayout = QHBoxLayout()
        hlayout.addWidget(self.run_button)
        hlayout.addWidget(self.save_scenario_button)
        layout.addLayout(hlayout) # adds horizontal layout to main layout
        
        # Adds status label to bottom of window
        layout.addWidget(self.status_label)
        self.setLayout(layout) #assing layout as main layout manager

        # Initial load and refresh of dropdowns
        self.refresh_asteroid_dropdown()
        self.refresh_thruster_dropdown()
        self.refresh_spacecraft_dropdown()
        self.refresh_scenario_dropdown()

        # Loads current selections after refresh to populate input fields
        self.load_asteroid(self.asteroid_select.currentText())
        self.load_thruster(self.thruster_select.currentText())
        self.load_spacecraft(self.spacecraft_select.currentText())

    # === Dropdown refresh helpers ===
    def refresh_asteroid_dropdown(self):
        current = self.asteroid_select.currentText() #takes current asteroid text
        self.asteroid_select.clear() # removes all items from dropdown so it can be repopulated
        names = list(self.asteroids.keys()) # list of names stored in scenarios
        self.asteroid_select.addItems(names) # adds names to dropdown
        idx = self.asteroid_select.findText(current) #returns index of currently selected item
        if idx >= 0:  # checks if index is greater than 1 or not 
            self.asteroid_select.setCurrentIndex(idx) # sets dropdown selection to that index

    def refresh_thruster_dropdown(self):
        current = self.thruster_select.currentText() #takes current asteroid text
        self.thruster_select.clear() # removes all items from dropdown so it can be repopulated
        names = list(self.thrusters.keys()) # list of names stored in scenarios
        self.thruster_select.addItems(names) # adds names to dropdown
        idx = self.thruster_select.findText(current) #returns index of currently selected item
        if idx >= 0: # checks if index is greater than 1 or not 
            self.thruster_select.setCurrentIndex(idx) # sets dropdown selection to that index

    def refresh_spacecraft_dropdown(self):
        current = self.spacecraft_select.currentText() #takes current asteroid text
        self.spacecraft_select.clear() # removes all items from dropdown so it can be repopulated
        names = list(self.spacecraft.keys()) # list of names stored in scenarios
        self.spacecraft_select.addItems(names) # adds names to dropdown
        idx = self.spacecraft_select.findText(current) #returns index of currently selected item
        if idx >= 0: # checks if index is greater than 1 or not 
            self.spacecraft_select.setCurrentIndex(idx) # sets dropdown selection to that index

    def refresh_scenario_dropdown(self):
        current = self.scenario_select.currentText() #current selection in dropdown
        self.scenario_select.blockSignals(True) # starts blocking signals from other events
    
        self.scenario_select.clear() # removes all items from dropdown so it can be repopulated
        names = list(self.scenarios.keys()) # list of names stored in scenarios
        self.scenario_select.addItems([""] + names) # adds names to dropdown with a " " as the first option
    
        if current in names:
            self.scenario_select.setCurrentText(current) # restores selection if current selection is the same after the refresh
    
        self.scenario_select.blockSignals(False) # stops blocking signals from other events


    # === Editor launch ===
    def open_asteroid_editor(self):
        name = self.asteroid_select.currentText()
        if name in self.builtin_asteroid_names: # if builtin
            dlg = AsteroidEditWindow(self, self.asteroids[name], name, editable=False) # non editable
            dlg.exec_()
            self.asteroids = load_json(self.asteroid_file, self.default_asteroids)  # reloads JSON in case editor saved changes
            self.refresh_asteroid_dropdown()
            return
        dlg = AsteroidEditWindow(self, self.asteroids[name], name, editable=True) # editable if not built in
        dlg.exec_()
        self.asteroids = load_json(self.asteroid_file, self.default_asteroids) # reloads JSON in case editor saved changes
        self.refresh_asteroid_dropdown()

    def open_thruster_editor(self):
        name = self.thruster_select.currentText()
        if name in self.builtin_thruster_names: # if builtin
            dlg = ThrusterEditWindow(self, self.thrusters[name], name, editable=False) # non editable
            dlg.exec_()
            self.thrusters = load_json(self.thruster_file, self.default_thrusters) # reloads JSON in case editor saved changes
            self.refresh_thruster_dropdown()
            return
        dlg = ThrusterEditWindow(self, self.thrusters[name], name, editable=True) # editable if not built in
        dlg.exec_()
        self.thrusters = load_json(self.thruster_file, self.default_thrusters) # reloads JSON in case editor saved changes
        self.refresh_thruster_dropdown()

    def open_spacecraft_editor(self):
        name = self.spacecraft_select.currentText()
        if name in self.builtin_spacecraft_names: # if builtin
            dlg = SpacecraftEditWindow(self, self.spacecraft[name], name, editable=False) # non editable
            dlg.exec_()
            self.spacecraft = load_json(self.spacecraft_file, self.default_spacecraft) # reloads JSON in case editor saved changes
            self.refresh_spacecraft_dropdown()
            return
        dlg = SpacecraftEditWindow(self, self.spacecraft[name], name, editable=True) # editable if not built in
        dlg.exec_()
        self.spacecraft = load_json(self.spacecraft_file, self.default_spacecraft) # reloads JSON in case editor saved changes
        self.refresh_spacecraft_dropdown()

    # === Profile loading ===
    def load_asteroid(self, name):
        """Loads asteroid parameters into the GUI fields."""
        
        # checks if name exists in dictionary
        if name not in self.asteroids:
            return
        
        #retrieves parameters from dictionary
        profile = self.asteroids[name]

        # Inserts values into inputs box
        self.mass_input.setText(str(profile.get("mass", "")))
        self.radius_input.setText(str(profile.get("radius", "")))
        self.horizons_id_input.setText(str(profile.get("horizons_id", "")))
        self.h_start_input.setText(str(profile.get("h_start", "")))
        self.h_stop_input.setText(str(profile.get("h_stop", "")))
        self.h_step_input.setText(str(profile.get("h_step", "")))

    def load_thruster(self, name):
        """Loads thruster / mission parameters into GUI fields."""
        
        if name not in self.thrusters:
            return

        profile = self.thrusters[name]

        # Inserts values into inputs box
        self.thrust_input.setText(str(profile.get("thrust", "")))
        self.theta_input.setText(str(profile.get("Beam Divergence", "")))
        self.Isp_input.setText(str(profile.get("Isp", "")))

    def load_spacecraft(self, name):
        """Loads spacecraft arrangement parameters into GUI fields."""

        if name not in self.spacecraft:
            return

        profile = self.spacecraft[name]
        
        # Inserts values into inputs box
        self.array_num_input.setText(str(profile.get("array_num", "")))
        self.sc_num_input.setText(str(profile.get("sc_num", "")))
        self.mass_fuel_input.setText(str(profile.get("mass_fuel", "")))
        self.mass_sc_input.setText(str(profile.get("mass_sc", "")))
        # future: populate solar_power if present

    def load_scenario(self):
        name = self.scenario_select.currentText()
        data = self.scenarios[name]
    
        # ---- LOAD PROFILE SELECTORS ----
        self.asteroid_select.setCurrentText(data["profiles"]["asteroid"])
        self.thruster_select.setCurrentText(data["profiles"]["thruster"])
        self.spacecraft_select.setCurrentText(data["profiles"]["spacecraft"])
    
        # ---- LOAD ASTEROID ----
        a = data["asteroid_data"] # pulls data from asteroid in JSON file
        self.mass_input.setText(a["mass"])
        self.radius_input.setText(a["radius"])
        self.horizons_id_input.setText(a["horizons_id"])
        self.h_start_input.setText(a["h_start"])
        self.h_stop_input.setText(a["h_stop"])
        self.h_step_input.setText(a["h_step"])
    
        # ---- LOAD THRUSTER ----
        t = data["thruster_data"] # pulls data from thruster in JSON file
        self.thrust_input.setText(t["thrust"])
        self.Isp_input.setText(t["Isp"])
        self.theta_input.setText(t["theta"])
    
        # ---- LOAD SPACECRAFT ----
        s = data["spacecraft_data"] # pulls data from spacecraft in JSON file
        self.array_num_input.setText(s["array_num"])
        self.sc_num_input.setText(s["sc_num"])
        self.mass_fuel_input.setText(s["mass_fuel"])
        self.mass_sc_input.setText(s["mass_sc"])
    
        # ---- LOAD MISSION ----
        m = data["mission_data"] # pulls data from mission in JSON file
        self.dt_input.setText(m["dt"])
        self.standoff_input.setText(m["standoff"])
        self.orbit_window_input.setText(m["orbit_window"])
        self.infront_input.setText(m["infront"])

        
    # === Scenario save ===
    def save_scenario(self):
        name, ok = QInputDialog.getText(self, "Save Scenario", "Scenario name:")
        if not ok or not name.strip():
            return
    
        self.scenarios[name] = {
            # ---- PROFILE SELECTIONS ----
            "profiles": {
                "asteroid": self.asteroid_select.currentText(), # current selection of dropdowns
                "thruster": self.thruster_select.currentText(),
                "spacecraft": self.spacecraft_select.currentText()
            },
    
            # ---- ASTEROID DATA ----
            "asteroid_data": {
                "mass": self.mass_input.text(),
                "radius": self.radius_input.text(),
                "horizons_id": self.horizons_id_input.text(),
                "h_start": self.h_start_input.text(),
                "h_stop": self.h_stop_input.text(),
                "h_step": self.h_step_input.text()
            },
    
            # ---- THRUSTER DATA ----
            "thruster_data": {
                "thrust": self.thrust_input.text(),
                "Isp": self.Isp_input.text(),
                "theta": self.theta_input.text()
            },
            
            "spacecraft_data": {
                "array_num": self.array_num_input.text(),
                "sc_num": self.sc_num_input.text(),
                "mass_fuel": self.mass_fuel_input.text(),
                "mass_sc": self.mass_sc_input.text()
            },
            # ---- MISSION DATA ----
            "mission_data": {
                "dt": self.dt_input.text(),
                "standoff": self.standoff_input.text(),
                "orbit_window": self.orbit_window_input.text(),
                "infront": self.infront_input.text()
            }
        }
    
        save_json(self.scenario_file, self.scenarios)
        self.refresh_scenario_dropdown()
        self.scenario_select.setCurrentText(name)
    
        QMessageBox.information(self, "Saved", f"Scenario '{name}' saved.")

    # === Run MATLAB Simulation: call get_horizons_rv then ODE_Handle ===
    def run_simulation(self):
        self.status_label.setText("Running MATLAB simulation...")
        QApplication.processEvents() # Should Use QThread to call outside of GUI
        self.setEnabled(False)  # locks UI while running sim
    
        try:
            # Gather inputs
            target_id = self.horizons_id_input.text().strip()
            start_date = self.h_start_input.text().strip()
            stop_date = self.h_stop_input.text().strip()
            step_size = self.h_step_input.text().strip()
    
            if not target_id or not start_date or not stop_date or not step_size:
                raise ValueError("Horizons inputs must be provided.")
    
            # Gets initial state from MATLAB through batch script
            subprocess.run([
                "matlab", "-batch",
                f"vec=get_horizons_rv('{target_id}','{start_date}','{stop_date}','{step_size}'); save('init_state.mat','vec');"
            ], capture_output=True, text=True)
            init_data = scipy.io.loadmat("init_state.mat") # loads matlab mat file
            state_vec = np.array(init_data["vec"]).flatten() # flattens and turns into array
            rA0 = state_vec[:3]
            vA0 = state_vec[3:]
            print(rA0)
            print(vA0)
            
            # removes any whitespace from text, checks if something was actually entered and converts string to float
            def float_field(field):
                if field.text().strip() != "":
                    return float(field.text()) 
            
            # MATLAB Batch call
            out = run_matlab_batch(
                rA0, vA0,
                thrust=float_field(self.thrust_input),
                array_num=float_field(self.array_num_input),
                sc_num=float_field(self.sc_num_input),
                dt=float_field(self.dt_input),
                mass_fuel=float_field(self.mass_fuel_input),
                mass_sc=float_field(self.mass_sc_input),
                Isp=float_field(self.Isp_input),
                M_A=float_field(self.mass_input),
                R_A=float_field(self.radius_input),
                d=float_field(self.standoff_input),
                theta=float_field(self.theta_input),
                orbit_win=float_field(self.orbit_window_input),
                infront=float_field(self.infront_input)
            )
    
            if out is None: # if out does not exsist
                raise RuntimeError("MATLAB failed.")
        
            self.status_label.setText("Simulation complete.") # successful run
            
        except Exception as e: #any error found will produce simulation failed
            self.status_label.setText("Simulation failed.")
            QMessageBox.critical(self, "Error", str(e)) # produces error window pop up with exception error
        finally: # runs at end of try block
            self.setEnabled(True) # sets GUI to enabled again so things can be rerun if needed
            
        if out is not None: #if out has data
            self.show_simulation_summary(out) # runs simulation summary

    def show_simulation_summary(self,out):
        """
        
        Display key results from MATLAB batch simulation in a popup
        and plot a, e, z over time in a separate interactive window.
        
        """
        # flattens arrays into lists
        t_all = out["t_all"].flatten()
        a = out["a_all"].flatten()
        e = out["e_all"].flatten()
        z = out["Z_all"].flatten()
        DV = out["DV_tot"].flatten()
        delT = out["delT"].flatten()
        
        summary_text = (
            f"Change in semi-major axis: {a[-1] - a[1]:.3f} km\n"
            f"Total Deflection (zeta): {z[-1]:.6f} km\n"
            f"Total Delta V Imparted: {DV[-1]*1e6:.3f} mm/s\n"
            f"Total Change in Period (delta T): {delT[-1]:.3f} s\n"
            f"Total Time: {t_all[-1]/86400:.3f} days\n"
            f"Total Time: {t_all[-1]/86400/365.25:.3f} years\n"
        )
        
        # Plot Pop up with 3 sub plots to show trends over time
        plt.ion()  # interactive mode
        t_days = t_all / 86400
    
        fig, axs = plt.subplots(3, 1, figsize=(8, 10), sharex=True)
    
        # Semi-major axis
        axs[0].plot(t_days, a, 'b-')
        axs[0].set_ylabel('Semi-major axis a (km)')
        axs[0].set_title('Orbital Change Due to Ion Beam')
        axs[0].grid(True)
    
        # Eccentricity
        axs[1].plot(t_days, e, 'r-')
        axs[1].set_ylabel('Eccentricity')
        axs[1].set_title('Eccentricity over time')
        axs[1].grid(True)
    
        # Deflection
        axs[2].plot(t_days, z, 'g-')
        axs[2].set_ylabel('Zeta [km]')
        axs[2].set_xlabel('Time (days)')
        axs[2].set_title('B-Plane Deflection')
        axs[2].grid(True)
    
        plt.tight_layout()
        plt.show()  # pops out in separate window
        
        # Summary Dialog Box
        dlg = QDialog(self)
        dlg.setWindowTitle("Simulation Summary")
        layout = QVBoxLayout()
        text_box = QTextEdit()
        text_box.setReadOnly(True)
        text_box.setText(summary_text)
        layout.addWidget(text_box)
        dlg.setLayout(layout)
        dlg.resize(400, 300)
        
        dlg.setModal(False) # doesn't block interaction with other windows
        dlg.show() #shows summary window



if __name__ == "__main__":
    app = QApplication(sys.argv) # Creates main application object that handles all events, passes sys.argv which contains all arguments when running from the terminal
    gui = AsteroidSimGUI() # creates main window
    gui.show() # makes window visible
    sys.exit(app.exec_()) 
    
    # app.exec() keeps application running and responsive (starts event loop) and 
    # sys.exit makes sure the program exits cleanly when the window is closed

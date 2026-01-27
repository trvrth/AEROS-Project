"""
editors.py

Trevor Thomas

ENAE 380

Section: 0106

12/14/25

"""

from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QPushButton, QVBoxLayout,
    QMessageBox, QInputDialog
)
from utils import save_json

class AsteroidEditWindow(QDialog):
    """
    Editor for asteroid profiles. Editable flag determines if Save/Delete
    are enabled. Built-in profiles are created with editable=False.
    """
    def __init__(self, parent, asteroid_dict, asteroid_name, editable=True):
        super().__init__(parent)
        self.parent = parent
        self.asteroid_dict = asteroid_dict
        self.asteroid_name = asteroid_name
        self.editable = editable

        self.setWindowTitle(f"Edit Asteroid: {asteroid_name}")

        # fields (include horizons inputs)
        self.mass = QLineEdit(str(asteroid_dict.get("mass", "")))
        self.radius = QLineEdit(str(asteroid_dict.get("radius", "")))
        self.horizons_id = QLineEdit(str(asteroid_dict.get("horizons_id", "")))
        self.h_start = QLineEdit(str(asteroid_dict.get("h_start", "")))
        self.h_stop = QLineEdit(str(asteroid_dict.get("h_stop", "")))
        self.h_step = QLineEdit(str(asteroid_dict.get("h_step", "")))
        
        # Form Layout for editable parameters
        form = QFormLayout()
        form.addRow("Mass (kg):", self.mass)
        form.addRow("Radius (m):", self.radius)
        form.addRow("Horizons ID (e.g. '499' or '2025 PDC'):", self.horizons_id)
        form.addRow("Horizons Start Date (e.g. 2032-Jul-06):", self.h_start)
        form.addRow("Horizons Stop Date (e.g. 2032-Jul-07):", self.h_stop)
        form.addRow("Horizons Step Size (e.g. 1 d):", self.h_step)

        # Buttons with event connections
        self.save_btn = QPushButton("Save Changes")
        self.save_btn.clicked.connect(self.save_changes)

        self.save_new_btn = QPushButton("Save As New Profile")
        self.save_new_btn.clicked.connect(self.save_as_new)

        self.delete_btn = QPushButton("Delete Profile")
        self.delete_btn.clicked.connect(self.delete_profile)
        
        # If not editable
        if not self.editable:
            self.save_btn.setDisabled(True) # save button is disabled
            self.delete_btn.setDisabled(True)  # delete button is disabled
            
            # save_new_btn MUST remain enabled so user can "Save As New"
            self.save_new_btn.setEnabled(True) # save as new button is enabled
        
        # main layout and adds buttons and form to it
        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(self.save_btn)
        layout.addWidget(self.save_new_btn)
        layout.addWidget(self.delete_btn)
        self.setLayout(layout) # sets layout
    
    # validates if the inputted parameters are greater than or equal to 0
    def validate(self):
        try:
            m = float(self.mass.text())
            r = float(self.radius.text())
            if m <= 0 or r <= 0:
                raise ValueError
            return True #returns True for validation
        except Exception: # flags error if try does not work
            QMessageBox.warning(self, "Error", "Mass and radius must be positive numbers.")
            return False #returns false for validation

    def save_changes(self):
        if not self.editable: 
            return
        if not self.validate():
            return
        # takes text from input forms and assigns to dictionary
        self.asteroid_dict["mass"] = float(self.mass.text())
        self.asteroid_dict["radius"] = float(self.radius.text())
        
                    
        # checks for unnecessary spaces and strips for each
        if self.horizons_id.text().strip() != "": 
            self.asteroid_dict["horizons_id"] = self.horizons_id.text().strip()
        else:
            self.asteroid_dict.pop("horizons_id", None)
            
        if self.h_start.text().strip() != "":
            self.asteroid_dict["h_start"] = self.h_start.text().strip()
        else:
            self.asteroid_dict.pop("h_start", None)
            
        if self.h_stop.text().strip() != "":
            self.asteroid_dict["h_stop"] = self.h_stop.text().strip()
        else:
            self.asteroid_dict.pop("h_stop", None)
            
        if self.h_step.text().strip() != "":
            self.asteroid_dict["h_step"] = self.h_step.text().strip()
        else:
            self.asteroid_dict.pop("h_step", None)

        # saves over json file using save_json util function
        save_json(self.parent.asteroid_file, self.parent.asteroids)
        self.parent.refresh_asteroid_dropdown() # calls for parent's refresh asteroid dropdown method
        QMessageBox.information(self, "Saved", f"Asteroid '{self.asteroid_name}' updated.") # message box informing of success
        self.accept() # dialog ended successfuly, continues code

    def save_as_new(self):
        if not self.validate():
            return
        new_name, ok = QInputDialog.getText(self, "Save As New", "Enter new profile name:")
        if not ok or new_name.strip() == "":
            return
        new_name = new_name.strip()
        if new_name in self.parent.asteroids: # checks if name is already in parent dictionary
            QMessageBox.warning(self, "Error", f"Profile '{new_name}' already exists.")
            return
        self.parent.asteroids[new_name] = {
            "mass": float(self.mass.text()),
            "radius": float(self.radius.text())
        }
        if self.horizons_id.text().strip() != "":
            self.parent.asteroids[new_name]["horizons_id"] = self.horizons_id.text().strip()
        if self.h_start.text().strip() != "":
            self.parent.asteroids[new_name]["h_start"] = self.h_start.text().strip()
        if self.h_stop.text().strip() != "":
            self.parent.asteroids[new_name]["h_stop"] = self.h_stop.text().strip()
        if self.h_step.text().strip() != "":
            self.parent.asteroids[new_name]["h_step"] = self.h_step.text().strip()

        save_json(self.parent.asteroid_file, self.parent.asteroids)
        self.parent.refresh_asteroid_dropdown()
        QMessageBox.information(self, "Saved", f"Asteroid '{new_name}' created.")
        self.accept() # dialog ended successfuly, continues code

    def delete_profile(self):
        if not self.editable: # checks if editable
            return
        # message box to confirm delete or not
        confirm = QMessageBox.question(self, "Confirm Delete",
                                       f"Delete asteroid '{self.asteroid_name}'?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm != QMessageBox.Yes:
            return
        if self.asteroid_name in self.parent.asteroids:
            del self.parent.asteroids[self.asteroid_name] # deletes asteroid name from dictionary
            save_json(self.parent.asteroid_file, self.parent.asteroids) # saves JSON file with deletion
            self.parent.refresh_asteroid_dropdown() # refreshes drop down
            QMessageBox.information(self, "Deleted", f"Asteroid '{self.asteroid_name}' deleted.") #displays message informing of deletion
        self.accept() #continue code


class ThrusterEditWindow(QDialog):
    """
    Thruster profile editor. Contains thrust, array_num, sc_num, mass_fuel, mass_sc, Isp, duration, dt.
    """
    def __init__(self, parent, thruster_dict, thruster_name, editable=True):
        super().__init__(parent)
        self.parent = parent
        self.thruster_dict = thruster_dict
        self.thruster_name = thruster_name
        self.editable = editable

        self.setWindowTitle(f"Edit Thruster: {thruster_name}")

        # fields
        self.thrust = QLineEdit(str(thruster_dict.get("thrust", thruster_dict.get("force", ""))))
        self.Isp = QLineEdit(str(thruster_dict.get("Isp", thruster_dict.get("Isp", ""))))
        self.divergence = QLineEdit(str(thruster_dict.get("Beam Divergence", "")))

        form = QFormLayout()
        form.addRow("Thrust (N):", self.thrust)
        form.addRow("Isp (s):", self.Isp)
        form.addRow("Beam Divergence (deg):", self.divergence)
        
        self.save_btn = QPushButton("Save Changes")
        self.save_btn.clicked.connect(self.save_changes)

        self.save_new_btn = QPushButton("Save As New Profile")
        self.save_new_btn.clicked.connect(self.save_as_new)

        self.delete_btn = QPushButton("Delete Profile")
        self.delete_btn.clicked.connect(self.delete_profile)

        if not self.editable:
            
            # normal Save and Delete disabled
            self.save_btn.setDisabled(True)
            self.delete_btn.setDisabled(True)
            
            # save_new_btn MUST remain enabled so user can "Save As New"
            self.save_new_btn.setEnabled(True)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(self.save_btn)
        layout.addWidget(self.save_new_btn)
        layout.addWidget(self.delete_btn)
        self.setLayout(layout)

    def validate(self):
        try:
            t = float(self.thrust.text())
            isp = float(self.Isp.text())
            theta = float(self.divergence.text())
            if t <= 0 or isp <= 0 or theta < 0:
                raise ValueError
            return True
        except Exception:
            QMessageBox.warning(self, "Error", "Please ensure numeric positive values for required fields.")
            return False

    def save_changes(self):
        if not self.editable:
            return
        if not self.validate():
            return
        self.thruster_dict["thrust"] = float(self.thrust.text())
        self.thruster_dict["Isp"] = float(self.Isp.text())
        self.thruster_dict["Beam Divergence"] = float(self.divergence.text())

        save_json(self.parent.thruster_file, self.parent.thrusters)
        self.parent.refresh_thruster_dropdown()
        QMessageBox.information(self, "Saved", f"Thruster '{self.thruster_name}' updated.")
        self.accept()

    def save_as_new(self):
        if not self.validate():
            return
        new_name, ok = QInputDialog.getText(self, "Save As New", "Enter new profile name:")
        if not ok or new_name.strip() == "":
            return
        new_name = new_name.strip()
        if new_name in self.parent.thrusters:
            QMessageBox.warning(self, "Error", f"Profile '{new_name}' already exists.")
            return
        self.parent.thrusters[new_name] = {
            "thrust": float(self.thrust.text()),
            "Isp": float(self.Isp.text()),
            "Beam Divergence": float(self.divergence.text())
        }
        save_json(self.parent.thruster_file, self.parent.thrusters)
        self.parent.refresh_thruster_dropdown()
        QMessageBox.information(self, "Saved", f"Thruster '{new_name}' created.")
        self.accept()

    def delete_profile(self):
        if not self.editable:
            return
        confirm = QMessageBox.question(self, "Confirm Delete",
                                       f"Delete thruster '{self.thruster_name}'?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm != QMessageBox.Yes:
            return
        if self.thruster_name in self.parent.thrusters:
            del self.parent.thrusters[self.thruster_name]
            save_json(self.parent.thruster_file, self.parent.thrusters)
            self.parent.refresh_thruster_dropdown()
            QMessageBox.information(self, "Deleted", f"Thruster '{self.thruster_name}' deleted.")
        self.accept()

class SpacecraftEditWindow(QDialog):
    """
    Editor for spacecraft arrangement: array_num, sc_num, mass_fuel, mass_sc.
    """
    def __init__(self, parent, sc_dict, sc_name, editable=True):
        super().__init__(parent)
        self.parent = parent
        self.sc_dict = sc_dict
        self.sc_name = sc_name
        self.editable = editable

        self.setWindowTitle(f"Edit Spacecraft Arrangement: {sc_name}")

        self.array_num = QLineEdit(str(sc_dict.get("array_num", "")))
        self.sc_num = QLineEdit(str(sc_dict.get("sc_num", "")))
        self.mass_fuel = QLineEdit(str(sc_dict.get("mass_fuel", "")))
        self.mass_sc = QLineEdit(str(sc_dict.get("mass_sc", "")))

        form = QFormLayout()
        form.addRow("Array Number:", self.array_num)
        form.addRow("Number of Spacecraft:", self.sc_num)
        form.addRow("Mass Fuel per Craft (kg):", self.mass_fuel)
        form.addRow("Spacecraft Dry Mass (kg):", self.mass_sc)

        self.save_btn = QPushButton("Save Changes")
        self.save_new_btn = QPushButton("Save As New Profile")
        self.delete_btn = QPushButton("Delete Profile")

        self.save_btn.clicked.connect(self.save_changes)
        self.save_new_btn.clicked.connect(self.save_as_new)
        self.delete_btn.clicked.connect(self.delete_profile)

        if not self.editable:
            self.save_btn.setDisabled(True)
            self.delete_btn.setDisabled(True)
            
            # save_new_btn MUST remain enabled so user can "Save As New"
            self.save_new_btn.setEnabled(True)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(self.save_btn)
        layout.addWidget(self.save_new_btn)
        layout.addWidget(self.delete_btn)
        self.setLayout(layout)

    def validate(self):
        try:
            arr = int(float(self.array_num.text()))
            sc = int(float(self.sc_num.text()))
            mf = float(self.mass_fuel.text())
            ms = float(self.mass_sc.text())
            if arr <= 0 or sc <= 0 or mf < 0 or ms <= 0:
                raise ValueError
            return True
        except Exception:
            QMessageBox.warning(self, "Error", "Please enter valid positive numeric values.")
            return False

    def save_changes(self):
        if not self.editable:
            return
        if not self.validate():
            return

        self.sc_dict["array_num"] = int(float(self.array_num.text()))
        self.sc_dict["sc_num"] = int(float(self.sc_num.text()))
        self.sc_dict["mass_fuel"] = float(self.mass_fuel.text())
        self.sc_dict["mass_sc"] = float(self.mass_sc.text())

        save_json(self.parent.spacecraft_file, self.parent.spacecraft)
        self.parent.refresh_spacecraft_dropdown()
        QMessageBox.information(self, "Saved", f"Spacecraft '{self.sc_name}' updated.")
        self.accept()

    def save_as_new(self):
        if not self.validate():
            return
        name, ok = QInputDialog.getText(self, "Save As New", "Enter new profile name:")
        if not ok or name.strip() == "":
            return
        name = name.strip()
        if name in self.parent.spacecraft:
            QMessageBox.warning(self, "Error", f"Profile '{name}' already exists.")
            return

        self.parent.spacecraft[name] = {
            "array_num": int(float(self.array_num.text())),
            "sc_num": int(float(self.sc_num.text())),
            "mass_fuel": float(self.mass_fuel.text()),
            "mass_sc": float(self.mass_sc.text())
        }

        save_json(self.parent.spacecraft_file, self.parent.spacecraft)
        self.parent.refresh_spacecraft_dropdown()
        QMessageBox.information(self, "Saved", f"Spacecraft '{name}' saved.")
        self.accept()

    def delete_profile(self):
        if not self.editable:
            return
        confirm = QMessageBox.question(self, "Confirm Delete",
                                       f"Delete spacecraft profile '{self.sc_name}'?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm != QMessageBox.Yes:
            return

        if self.sc_name in self.parent.spacecraft:
            del self.parent.spacecraft[self.sc_name]
            save_json(self.parent.spacecraft_file, self.parent.spacecraft)
            self.parent.refresh_spacecraft_dropdown()
            QMessageBox.information(self, "Deleted", f"Spacecraft '{self.sc_name}' deleted.")
        self.accept()

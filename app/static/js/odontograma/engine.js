/*
 * Copyright (c) 2018 Bardur Thomsen <https://github.com/bardurt>.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Bardur Thomsen <https://github.com/bardurt> - initial API and implementation and/or initial documentation
 */

/* global Damage */

function Engine () {

  // canvas which is used by the engine
  this.canvas = null;

  this.adultShowing = true;

  // array which contains all the teeth for an odontograma
  this.mouth = [];

  // array which holds all the spaces between teeth
  this.spaces = [];

  // array for an adult odontograma
  this.odontAdult = [];

  // spaces for a adult odontograma
  this.odontSpacesAdult = [];

  // array for a child odontograma
  this.odontChild = [];

  // spaces for a child odontograma
  this.odontSpacesChild = [];
}

/*
 * Function to get all the data from the odontogram
 * in a format that can be stored in a database
 */
Engine.prototype.getOdontogramaData = function () {
  const teethData = [];
  const spacesData = [];
  const patientData = {
    dentist: this.dentist,
    patient: this.patient,
    id: this.id,
    record: this.record,
    date: this.date,
    dentistCheck: this.dentistCheck,
    observations: this.observations,
    specifications: this.specifications
  };

  // Process teeth data
  this.mouth.forEach(tooth => {
    const toothInfo = {
      id: tooth.id,
      address: tooth.address,
      surfaces: [],
      damages: []
    };

    // Surface data (assuming structure)
    if (tooth.surface && typeof tooth.surface.getSurfaceData === 'function') {
      toothInfo.surfaces = tooth.surface.getSurfaceData();
    } else if (tooth.surfacesRect) { // Fallback or alternative structure
      Object.values(tooth.surfacesRect).forEach(surfaceRect => {
        if (surfaceRect && surfaceRect.id && surfaceRect.state) {
          toothInfo.surfaces.push({ id: surfaceRect.id, state: surfaceRect.state });
        }
      });
    }

    tooth.damages.forEach(damage => {
      // Ensure damage has necessary properties, especially type for drawing
      if (damage && typeof damage.type !== 'undefined') {
        teethData.push({
          toothId: tooth.id,
          damageId: damage.id, // Assuming damage.id is the unique ID of the damage instance
          damageType: damage.type, // This is crucial for re-drawing
        });
      }
    });
    // Add toothInfo to teethData if it contains surfaces or if you always want to save tooth state
    if (toothInfo.surfaces.length > 0 || tooth.damages.length > 0 || Object.keys(tooth.notes).length > 0) {
       teethData.push(toothInfo);
    }
  });

  this.spaces.forEach(space => {
    space.damages.forEach(damage => {
      // Ensure damage has necessary properties
      if (damage && typeof damage.type !== 'undefined') {
        spacesData.push({
          spaceId: space.id,
          damageId: damage.id,
          damageType: damage.type,
        });
      }
    });
  });

  return {
    patient: patientData,
    teeth: teethData,
    spaces: spacesData
  };
};

/*
 * Function to load odontogram data from previously saved data
 */
Engine.prototype.loadOdontogramaData = function (data) {
  if (!data) return;

  // Clear existing damages first
  this.mouth.forEach(tooth => {
    tooth.damages = [];
    if (tooth.surface && typeof tooth.surface.clearStates === 'function') {
      tooth.surface.clearStates(); // Method to reset surface states
    } else if (tooth.surfacesRect) {
        Object.values(tooth.surfacesRect).forEach(rect => {
            if(rect && typeof rect.uncheck === 'function') rect.uncheck();
        });
    }
  });
  this.spaces.forEach(space => {
    space.damages = [];
  });

  if (data.teeth) {
    data.teeth.forEach(item => {
      const tooth = this.findToothById(item.toothId || item.id); // Support both direct toothId or nested id
      if (tooth) {
        if (item.damages && Array.isArray(item.damages)) { // If damages are nested under tooth item
            item.damages.forEach(damageData => {
                if (typeof damageData.damageType !== 'undefined') {
                    const damage = new Damage(
                        damageData.damageId, // or generate new if not present
                        0, 0, 0, 0, // Placeholder coords/dims, adjust if stored/needed
                        damageData.damageType
                    );
                    tooth.addDamage(damage);
                }
            });
        } else if (typeof item.damageType !== 'undefined') { // If item itself is a damage entry
            const damage = new Damage(
                item.damageId,
                0, 0, 0, 0, // Placeholder
                item.damageType
            );
            tooth.addDamage(damage);
        }

        // Load surface states
        if (item.surfaces && Array.isArray(item.surfaces)) {
          item.surfaces.forEach(surfaceData => {
            if (tooth.surface && typeof tooth.surface.setSurfaceState === 'function') {
              tooth.surface.setSurfaceState(surfaceData.id, surfaceData.state);
            } else if (tooth.surfacesRect && tooth.surfacesRect[surfaceData.id]) {
                const surfaceComponent = tooth.surfacesRect[surfaceData.id];
                if(surfaceComponent) {
                    if (surfaceData.state === 'cavity' && typeof surfaceComponent.cavity === 'function') {
                        surfaceComponent.cavity();
                    } else if (surfaceData.state === 'restoration' && typeof surfaceComponent.restoration === 'function') {
                        surfaceComponent.restoration();
                    }
                }
            }
          });
        }
      }
    });
  }

  if (data.spaces) {
    data.spaces.forEach(item => {
      const space = this.findSpaceById(item.spaceId);
      if (space && typeof item.damageType !== 'undefined') {
        const damage = new Damage(
          item.damageId,
          0, 0, 0, 0, // Placeholder
          item.damageType
        );
        space.addDamage(damage);
      }
    });
  }

  this.draw(); // Redraw canvas after loading data
};

/*
 * Helper function to find a tooth by its ID
 */
Engine.prototype.findToothById = function (id) {
  for (let i = 0; i < this.mouth.length; i++) {
    if (this.mouth[i].id === id) {
      return this.mouth[i];
    }
  }
  return null;
};

/*
 * Helper function to find a space by its ID
 */
Engine.prototype.findSpaceById = function (id) {
  for (let i = 0; i < this.spaces.length; i++) {
    if (this.spaces[i].id === id) {
      return this.spaces[i];
    }
  }
  return null;
};


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

/* global Rect, TextBox, Damage */

// -----------------
// Upper mouth = 0
// Lower mouth = 1;
// -----------------

/**
 * Base class for tooth
 * @returns {Tooth}
 */
function Tooth () {

  this.id = 0;
  this.tooth = true;
  this.surfaces = 0;
  this.highlight = false;
  this.highlightColor = '';
  this.damages = Array();
  this.checkBoxes = Array();
  this.rect = new Rect();
  this.textBox = new TextBox();
  this.spacer = 20; // spacer to seperate tooth from surfaces
  this.touching = false;
  this.address = 0;
  this.normalY = null;
  this.highY = null;
  this.blocked = false;
  this.constants = null;
  this.surfacesRect = {}; // Initialize as an object
}

/**
 * Method to set up position and dimension of the Tooth
 * @param {type} x position
 * @param {type} y position
 * @param {type} width
 * @param {type} height
 * @returns {undefined}
 */
Tooth.prototype.setDimens = function (x, y, width, height) {


  this.y = y; // y variable to help with animations, on mouse hover

  this.rect.x = x;
  this.rect.y = y;
  this.rect.width = width;
  this.rect.height = height;

  this.normalY = y;

  this.textBox.setDimens(x, y, width, 20);

  this.textBox.setLabel(this.id);
};

/**
 * Method to set the type of the tooth
 * @param {type} type of the tooth, upper or lower
 * @returns {undefined}
 */
Tooth.prototype.setType = function (type) {


  this.type = type;

  if (type === 0) {
    this.highY = this.rect.y - 10;

    this.textBox.rect.y = this.rect.y - 42;
  } else {
    this.highY = this.rect.y + 10;

    this.textBox.rect.y = this.rect.y + this.rect.height + 22;
  }
};

/**
 * Method to set a reference to constants
 * @param {type} constants
 * @returns {undefined}
 */
Tooth.prototype.setConstants = function (constants) {

  this.constants = constants;
};

/**
 * Method to check for collision
 * @param {type} eX x coordinates of event
 * @param {type} eY y coordinates of event
 * @returns boolean true if collision, else false
 */
Tooth.prototype.checkCollision = function (eX, eY) {

  return this.rect.checkCollision(eX, eY);
};

/**
 * Method to set surfaces for the tooth, 4 or 5
 * @param {type} surfaces
 * @returns {undefined}
 */
Tooth.prototype.setSurfaces = function (surfaces) {

  this.surfaces = surfaces;
};

Tooth.prototype.toggleSelected = function (selected) {

  this.highlight = selected;
};

/**
 * Method to create 4 surfaces for the tooth, 5 checkboxes
 * @param {type} settings global settings
 * @returns {undefined}
 */
Tooth.prototype.create4Surfaces = function (settings) {

  this.surfacesRect = {}; // Initialize as an object

  let x = this.rect.x + settings.TOOTH_PADDING;
  let y = this.rect.y + settings.TOOTH_PADDING;
  const surfaceWidth = (this.rect.width - 2 * settings.TOOTH_PADDING - settings.TOOTH_PADDING) / 2;
  const surfaceHeight = (this.rect.height - 2 * settings.TOOTH_PADDING - settings.TOOTH_PADDING) / 2;

  // Vestibular (V)
  let rect1 = new Rect();
  rect1.id = "V";
  rect1.setUp(x, y, surfaceWidth, surfaceHeight, false, "V");
  this.surfacesRect[rect1.id] = rect1;

  // Lingual (L) or Palatino (P)
  let rect2 = new Rect();
  rect2.id = this.type === 0 ? "P" : "L"; // Assuming type 0 is upper
  rect2.setUp(x + surfaceWidth + settings.TOOTH_PADDING, y, surfaceWidth, surfaceHeight, false, rect2.id);
  this.surfacesRect[rect2.id] = rect2;

  // Mesial (M)
  let rect3 = new Rect();
  rect3.id = "M";
  rect3.setUp(x, y + surfaceHeight + settings.TOOTH_PADDING, surfaceWidth, surfaceHeight, false, "M");
  this.surfacesRect[rect3.id] = rect3;

  // Distal (D)
  let rect4 = new Rect();
  rect4.id = "D";
  rect4.setUp(x + surfaceWidth + settings.TOOTH_PADDING, y + surfaceHeight + settings.TOOTH_PADDING, surfaceWidth, surfaceHeight, false, "D");
  this.surfacesRect[rect4.id] = rect4;

  // Oclusal (O) / Incisal (I) - Central Checkbox
  let rect5 = new Rect(); // Oclusal or Incisal
  rect5.id = "O"; // Or "I"
  const oclusalX = this.rect.x + this.rect.width / 4;
  const oclusalY = this.rect.y + this.rect.height / 4;
  const oclusalSize = this.rect.width / 2; // Example size
  rect5.setUp(oclusalX, oclusalY, oclusalSize, oclusalSize, false, rect5.id);
  this.surfacesRect[rect5.id] = rect5;

  this.hasSurfaces = true;
};

/**
 * Method to create 5 surfaces for the tooth
 * @param {type} settings global settings
 * @returns {undefined}
 */
Tooth.prototype.create5Surfaces = function (settings) {

  this.surfacesRect = {}; // Initialize as an object

  let x = this.rect.x + settings.TOOTH_PADDING;
  let y = this.rect.y + settings.TOOTH_PADDING;
  const surfaceWidth = (this.rect.width - 2 * settings.TOOTH_PADDING - settings.TOOTH_PADDING) / 2;
  const surfaceHeight = (this.rect.height - 2 * settings.TOOTH_PADDING - settings.TOOTH_PADDING) / 2;

  // Vestibular (V)
  let sRect1 = new Rect(); // Renamed to avoid redeclare if create4Surfaces was called in same broader scope
  sRect1.id = "V";
  sRect1.setUp(x, y, surfaceWidth, surfaceHeight, false, "V");
  this.surfacesRect[sRect1.id] = sRect1;

  // Lingual (L) or Palatino (P)
  let sRect2 = new Rect();
  sRect2.id = this.type === 0 ? "P" : "L";
  sRect2.setUp(x + surfaceWidth + settings.TOOTH_PADDING, y, surfaceWidth, surfaceHeight, false, sRect2.id);
  this.surfacesRect[sRect2.id] = sRect2;

  // Mesial (M)
  let sRect3 = new Rect();
  sRect3.id = "M";
  sRect3.setUp(x, y + surfaceHeight + settings.TOOTH_PADDING, surfaceWidth, surfaceHeight, false, "M");
  this.surfacesRect[sRect3.id] = sRect3;

  // Distal (D)
  let sRect4 = new Rect();
  sRect4.id = "D";
  sRect4.setUp(x + surfaceWidth + settings.TOOTH_PADDING, y + surfaceHeight + settings.TOOTH_PADDING, surfaceWidth, surfaceHeight, false, "D");
  this.surfacesRect[sRect4.id] = sRect4;

  // Oclusal (O)
  let sRect5 = new Rect();
  sRect5.id = "O";
  const oclusalDimen = Math.min(surfaceWidth, surfaceHeight) * 0.8; // Example: 80% of smaller dimension
  const oclusalX = this.rect.x + (this.rect.width - oclusalDimen) / 2;
  const oclusalY = this.rect.y + (this.rect.height - oclusalDimen) / 2;
  sRect5.setUp(oclusalX, oclusalY, oclusalDimen, oclusalDimen, false, "O");
  this.surfacesRect[sRect5.id] = sRect5;

  this.hasSurfaces = true;
};

/**
 * Base method for setting the surfaces for a tooth
 * @param {type} settings global settings
 * @returns {undefined}
 */
Tooth.prototype.createSurfaces = function (settings) {

  if (this.surfaces === 4) {
    this.create4Surfaces(settings);
  } else {
    this.create5Surfaces(settings);
  }
};

/**
 * Method to draw the id for the tooth
 * @param {type} context the canvas to draw on
 * @returns {undefined}
 */
Tooth.prototype.drawId = function (context) {

  context.beginPath();
  context.textAlign = 'center';
  context.fillStyle = '#000000';
  context.font = '15px Arial Bold';

  const space = 40;

  if (this.type === 0) {
    // draw id
    context.fillText('' + this.id, this.rect.x + this.rect.width / 2,
      this.y + this.rect.height + space + 10);

    // draw id border
    context.moveTo(this.rect.x, this.y + this.rect.height + space + 20);

    context.lineTo(this.rect.x + this.rect.width,
      this.y + this.rect.height + space + 20);

    context.moveTo(this.rect.x + this.rect.width,
      this.y + this.rect.height + space + 20);

    context.lineTo(this.rect.x + this.rect.width,
      this.y + this.rect.height + space);
  } else {
    // draw id
    context.fillText('' + this.id, this.rect.x + this.rect.width / 2,
      this.y - space - 5);

    // draw id border
    context.moveTo(this.rect.x, this.y - space - 20);
    context.lineTo(this.rect.x + this.rect.width, this.y - space - 20);

    context.moveTo(this.rect.x + this.rect.width, this.y - space - 20);
    context.lineTo(this.rect.x + this.rect.width, this.y - space);
  }

  context.lineWidth = 1;
  // set line color
  context.strokeStyle = '#000000';
  context.stroke();
  context.restore();
};

/**
 * Method to draw the checkboxes for the tooth
 * @param {type} context the canvas to draw on
 * @param {type} settings global settings
 * @returns {undefined}
 */
Tooth.prototype.drawCheckBoxes = function (context, settings) {


  for (let i = 0; i < this.checkBoxes.length; i++) {
    if (this.checkBoxes[i].state === 1) {
      this.checkBoxes[i].fillColor(context, settings.COLOR_RED);
      this.checkBoxes[i].outline(context, '#000000');
    } else if (this.checkBoxes[i].state === 11) {
      this.checkBoxes[i].fillColor(context, settings.COLOR_BLUE);
      this.checkBoxes[i].outline(context, '#000000');
    } else {
      this.checkBoxes[i].outline(context, '#000000');
    }
  }
};

/**
 * Method to draw a text box for the tooth
 * @param {type} context the canvas to draw on
 * @param {type} settings global settings
 * @returns {undefined} void
 */
Tooth.prototype.drawTextBox = function (context, settings) {


  this.textBox.render(context, settings.COLOR_BLUE);

  if (this.textBox.touching) {
    this.textBox.rect.highlightWithColor(context, '#36BE1B', 0.6);
  }
};

/**
 * Method to toggle Touchin on / off
 * @param {type} touch boolean value
 * @returns {undefined}
 */
Tooth.prototype.onTouch = function (touch) {


  if (this.tooth) {
    if (touch) {
      this.rect.y = this.highY;
    } else {
      this.rect.y = this.normalY;
    }
  }

  this.rect.touching = touch;
};

/**
 * Method to generate a damage for the tooth.
 * @param {type} damageId the id of the damage to create
 * @returns {Damage} damage which can be drawn
 */
Tooth.prototype.createDamage = function (damageId) {

  // empty damage
  let damage;

  if (this.constants.isDiagnostic(damageId)) {
    // attach damage in the proper position
    // first check if the damage should be positioned in the checkboxes area
    if (damageId === this.constants.DIENTE_EN_CLAVIJA ||
                damageId === this.constants.FUSION ||
                damageId === this.constants.CORONA_DEFINITIVA ||
                damageId === this.constants.CORONA_TEMPORAL) {
      // set the damage to proper position
      if (this.type === 0) {
        damage = new Damage(damageId,
          this.rect.x,
          this.y + this.rect.height,
          this.rect.width,
          60,
          this.type);
      } else {
        damage = new Damage(damageId,
          this.rect.x,
          this.y - 60,
          this.rect.width,
          60,
          this.type);
      }
    } else if (this.constants.isWritable(damageId)) {
      // damage should be attached to the textBox area
      damage = new Damage(damageId,
        this.textBox.rect.x,
        this.textBox.rect.y,
        this.textBox.rect.width,
        this.textBox.rect.height,
        this.type);
    } else {
      // damage should be attached on the tooth
      damage = new Damage(damageId,
        this.rect.x,
        this.y,
        this.rect.width,
        this.rect.height,
        this.type);
    }
  } else {
    // set the damage to proper position
    if (this.type === 0) {
      damage = new Damage(damageId,
        this.rect.x,
        this.y + this.rect.height,
        this.rect.width,
        60,
        this.type);
    } else {
      damage = new Damage(damageId,
        this.rect.x,
        this.y - 60,
        this.rect.width,
        60,
        this.type);
    }

    damage.setDiagnostic();
  }

  return damage;
};

/**
 * Method to toggle damage on a tooth on off
 * @param {type} damageId to add or remove
 * @returns {undefined}
 */
Tooth.prototype.toggleDamage = function (damageId) {

  console.log('Toggle damage for ' + this.id + ', damage ' + damageId);

  // if there are no damages, then add.
  if (this.damages.length < 1) {
    const d = this.createDamage(damageId); // Changed var to const

    if (d !== undefined) {
      this.damages.push(d);
    }
  } else {
    // if this tooth has damages, check for duplicates
    let exists = false;
    let splicer = -1;

    // check to see if this damage exists
    for (let i = 0; i < this.damages.length; i++) {
      // found this damage
      if (this.damages[i].id === damageId) {
        console.log('Splicing array for tooth ' + this.id);

        splicer = i;
        exists = true;
        break;
      }
    }

    // check if damage exists
    if (!exists) {
      // damge is new, so add it
      const newDamage = this.createDamage(damageId); // Changed var d to const newDamage

      if (newDamage !== undefined) {
        this.damages.push(newDamage);
      }
    } else {
      // if damage already exists, then we remove it
      this.damages.splice(splicer, 1);
    }
  }
};

/**
 * Method to add a damage to the tooth
 * @param {Damage} damage the damage to add
 * @returns {undefined}
 */
Tooth.prototype.addDamage = function (damage) {

  // Check for DIENTE_AUSENTE or EDENTULOA_TOTAL
  if (damage.type === this.constants.DIENTE_AUSENTE ||
      damage.type === this.constants.EDENTULOA_TOTAL) {
    this.blocked = true;
    this.clearDamages(); // Clear other damages if tooth is marked as absent/edentulous
    this.damages.push(damage); // Add only this defining damage
    // Also clear surface selections if any
    if (this.surface && typeof this.surface.clearStates === 'function') {
        this.surface.clearStates();
    } else if (this.surfacesRect) {
        Object.values(this.surfacesRect).forEach(rect => {
            if(rect && typeof rect.uncheck === 'function') rect.uncheck();
        });
    }
    return; // Prevent adding other damages or this damage multiple times
  }

  // Prevent adding new damages if tooth is already marked DIENTE_AUSENTE or EDENTULOA_TOTAL
  if (this.blocked) {
      console.log("Tooth " + this.id + " is marked as absent/edentulous. No more damages can be added.");
      return;
  }

  this.damages.push(damage);
};

/**
 * Method to render a Tooth on the screen with all its states
 * @param {type} context the canvas to draw on
 * @param {type} settings app settings
 * @param {type} constants application constants
 * @returns {undefined}
 */
Tooth.prototype.render = function (context, settings, constants) {

  // check if this is a tooth or a space
  if (this.tooth) {
    this.textBox.drawLabel(context);

    // draw the image of the tooth
    if (this.image !== undefined) {
      // center of tooth
      const cx = (this.rect.x + this.rect.width / 2);

      // centerinng of the tooth in x axis
      const dx = cx - this.image.naturalWidth / 2;

      // draw tooth
      context.drawImage(this.image, dx, this.rect.y);
    }

    // id
    this.drawId(context);

    // checkboxes
    this.drawCheckBoxes(context, settings);

    if (this.highlight) {
      this.rect.highlightWithColor(context, this.highlightColor, 0.3);
    }
  } else {
    // highlight the spaces between the teeths
    if (settings.HIHGLIGHT_SPACES) {
      if (this.rect.touching) {
        this.rect.highlightEllipse(context, '#00AEFF', 0.5, -10);
      } else {
        this.rect.highlightEllipse(context, '#19B900', 0.2, 10);
      }
    }
  }

  // draw all damages
  for (let i = 0; i < this.damages.length; i++) {
    const d = this.damages[i];
    d.render(context, settings, constants);
  }

  // highlight textboxes
  for (let i = 0; i < this.checkBoxes.length; i++) {
    if (this.checkBoxes[i].touching) {
      this.checkBoxes[i].highlightWithColor(context, '#36BE1B', 0.6);
    }
  }

  // Draw textboxes
  if (this.tooth) {
    this.drawTextBox(context, settings);
  }

  // show area of tooth or space, only in DEBUG MODE
  if (settings.DEBUG) {
    if (this.tooth) {
      this.rect.outline(context, '#000000');
    } else {
      this.rect.highlightEllipse(context, '#FFD100', 0.4, 2);
    }
  }
};

/**
 * Method to get a surface (checkbox) by id
 * @param {type} id the id of the textbox to find
 * @returns returns a rect if found, else undefined
 */
Tooth.prototype.getSurfaceById = function (id) {

  let surface;

  for (let i = 0; i < this.checkBoxes.length; i++) {
    if (this.checkBoxes[i].id === id) {
      surface = this.checkBoxes[i];
      break;
    }
  }

  return surface;
};

/**
 * Metod to move a tooth up and down the Y axis
 * @param {type} movement amount of pixels to move the tooth
 * @returns {void}
 */
Tooth.prototype.moveUpDown = function (movement) {
  this.normalY += movement;
  this.y += movement;
  this.rect.y += movement;

  this.textBox.rect.y += movement;

  for (let i = 0; i < this.checkBoxes.length; i++) { // Changed var to let
    this.checkBoxes[i].y += movement;
  }

  for (let i = 0; i < this.damages.length; i++) { // Changed var to let
    this.damages[i].rect.y += movement;
  }
};

/**
 * Method to pop the last item of the damages array
 * @returns {void}
 */
Tooth.prototype.popDamage = function () {
  const tail = this.damages.length - 1; // last item

  if (tail >= 0) {
    this.damages.splice(tail, 1);
  }
};

Tooth.prototype.refresh = function (/* constants */) { // Commented out unused parameter
  for (let i = 0; i < this.damages.length; i++) { // Changed var to let
    if (this.constants.isWritable(this.damages[i].id)) {
      // damage should be attached to the textBox area
      this.damages[i].rect.x = this.textBox.rect.x;
      this.damages[i].rect.y = this.textBox.rect.y;
    }
  }

  this.rect.y = this.normalY;
  this.touching = false;

  this.textBox.touching = false;

  for (let i = 0; i < this.checkBoxes.length; i++) { // Changed var to let
    this.checkBoxes[i].touching = false;
  }
};


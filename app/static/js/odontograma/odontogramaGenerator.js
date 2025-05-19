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

/* global Tooth */

/**
 * Helper class for creating a Odontograma
 * @returns {OdontogramaGenerator}
 */
function OdontogramaGenerator () {

  // variable for how many images have been loaded
  this.currentLoad = 0;

  // variable for how many teeths are in array
  this.arrayCount = 0;
  this.seperator = 210;
  this.imgWidth = 40;
  this.imgHeight = 90;
  this.engine = null;
  this.settings = null;
  this.constants = null;
}

/**
 * Method to set reference to the engine which uses this
 * odontograma
 * @param {type} engine
 * @returns {undefined}
 */
OdontogramaGenerator.prototype.setEngine = function (engine) {

  this.engine = engine;
};

/**
 * Method to set reference to settings
 * @param {type} settings application settings
 * @returns {undefined}
 */
OdontogramaGenerator.prototype.setSettings = function (settings) {

  this.settings = settings;
};

OdontogramaGenerator.prototype.setConstants = function (constants) {

  this.constants = constants;
};

/**
 * Method to update the count of images which have been loaded
 * @returns {void}
 */
OdontogramaGenerator.prototype.updateLoad = function () {

  this.currentLoad = this.currentLoad + 1;

  // notify when all images have been loaded
  if (this.currentLoad >= this.arrayCount) {
    this.engine.start();
  }
};

/* '
 * Method to prepare an Odontograma for an adult, 32 teeth
 * @param {type} odontograma array which holds all 32 teeth
 * @param {type} spaces array to hold all the spaces between teeths
 * @param {type} canvas the canvas where the odontograma will be drawn
 * @returns {void}
 */
OdontogramaGenerator.prototype.prepareOdontogramaAdult = function (odontograma,
  spaces, canvas) {

  const self = this;
  this.arrayCount = 0;

  // center the ondotograma horizontal
  const width = canvas.width;
  const odontWidth = 16 * this.imgWidth;
  const start = (width - odontWidth) / 2;

  // start of first tooth
  let x = start;

  // center vertial
  const height = canvas.height;
  const odontHeight = 2 * 150;
  const base = (height - odontHeight) / 2;

  // create the 1st group of upper teeth
  for (let i = 18; i > 10; i--) {
    const tooth = new Tooth();
    tooth.setConstants(this.constants);

    if (i > 13) {
      tooth.setSurfaces(5);
    } else {
      tooth.setSurfaces(4);
    }

    const image = new Image();

    image.onload = function () {
      self.updateLoad();
    };

    image.src = 'images/dentadura-sup-' + i + '.png';

    tooth.id = i;
    tooth.image = image;

    tooth.setDimens(x,
      base,
      this.imgWidth,
      this.imgHeight);

    tooth.setType(0);

    x += tooth.rect.width + this.settings.TOOTH_PADDING;

    odontograma[this.arrayCount] = tooth;

    tooth.address = this.arrayCount;

    this.arrayCount++;

    tooth.createSurfaces(this.settings);

    const space = new Tooth();
    space.setConstants(this.constants);

    space.setSurfaces(5);

    if (i !== 11) {
      const tmpid = (i) + '' + (i - 1);
      space.id = Number(tmpid);
    } else {
      const tmpid = (i) + '' + (21);
      space.id = Number(tmpid);
    }

    space.setDimens(tooth.rect.x + tooth.rect.width / 2,
      tooth.rect.y,
      tooth.rect.width,
      tooth.rect.height);

    space.type = tooth.type;
    space.tooth = false;

    spaces.push(space);
  }

  // create the 2nd group of upper teeth
  for (let i = 21; i < 29; i++) {
    const tooth = new Tooth();
    tooth.setConstants(this.constants);

    if (i < 24) {
      tooth.setSurfaces(4);
    } else {
      tooth.setSurfaces(5);
    }

    const image = new Image();

    image.onload = function () {
      self.updateLoad();
    };

    image.src = 'images/dentadura-sup-' + i + '.png';

    tooth.id = i;
    tooth.image = image;

    tooth.setDimens(x,
      base,
      this.imgWidth,
      this.imgHeight);

    tooth.setType(0);

    x += tooth.rect.width + this.settings.TOOTH_PADDING;

    odontograma[this.arrayCount] = tooth;

    tooth.address = this.arrayCount;

    this.arrayCount++;

    tooth.createSurfaces(this.settings);

    if (i < 28) {
      const space = new Tooth();
      space.setConstants(this.constants);
      space.setSurfaces(5);
      const tmpid = (i) + '' + (i + 1);
      space.id = Number(tmpid);

      space.setDimens(tooth.rect.x + tooth.rect.width / 2,
        tooth.rect.y,
        tooth.rect.width,
        tooth.rect.height);

      space.type = tooth.type;
      space.tooth = false;

      spaces.push(space);
    }
  }

  // start position of first
  x = start;

  // create the 1st group of lower teeth
  for (let i = 48; i > 40; i--) {
    const tooth = new Tooth();
    tooth.setConstants(this.constants);

    if (i < 44) {
      tooth.setSurfaces(4);
    } else {
      tooth.setSurfaces(5);
    }

    const image = new Image();

    image.onload = function () {
      self.updateLoad();
    };

    image.src = 'images/dentadura-inf-' + i + '.png';

    tooth.id = i;
    tooth.image = image;

    tooth.setDimens(x,
      base + this.seperator,
      this.imgWidth,
      this.imgHeight);

    tooth.setType(1);

    x += tooth.rect.width + this.settings.TOOTH_PADDING;

    odontograma[this.arrayCount] = tooth;

    tooth.address = this.arrayCount;

    this.arrayCount++;

    tooth.createSurfaces(this.settings);

    const space = new Tooth();
    space.setConstants(this.constants);
    space.setSurfaces(5);

    if (i !== 41) {
      const tmpid = (i) + '' + (i - 1);
      space.id = Number(tmpid);
    } else {
      const tmpid = (i) + '' + (31);
      space.id = Number(tmpid);
    }

    space.setDimens(tooth.rect.x + tooth.rect.width / 2,
      tooth.rect.y,
      tooth.rect.width,
      tooth.rect.height);

    space.type = tooth.type;
    space.tooth = false;

    spaces.push(space);
  }

  // create the 2nd group of lower teeth
  for (let i = 31; i < 39; i++) {
    const tooth = new Tooth();
    tooth.setConstants(this.constants);

    if (i < 34) {
      tooth.setSurfaces(4);
    } else {
      tooth.setSurfaces(5);
    }

    const image = new Image();

    image.onload = function () {
      self.updateLoad();
    };

    image.src = 'images/dentadura-inf-' + i + '.png';

    tooth.id = i;
    tooth.image = image;
    tooth.setDimens(x,
      base + this.seperator,
      this.imgWidth,
      this.imgHeight);

    tooth.setType(1);

    odontograma[this.arrayCount] = tooth;
    x += tooth.rect.width + this.settings.TOOTH_PADDING;

    tooth.address = this.arrayCount;
    this.arrayCount++;

    tooth.createSurfaces(this.settings);

    if (i < 38) {
      const space = new Tooth();
      space.setConstants(this.constants);
      space.setSurfaces(5);
      const tmpid = (i) + '' + (i + 1);
      space.id = Number(tmpid);

      space.setDimens(tooth.rect.x + tooth.rect.width / 2,
        tooth.rect.y,
        tooth.rect.width,
        tooth.rect.height);

      space.type = tooth.type;
      space.tooth = false;

      spaces.push(space);
    }
  }
};

/**
 * Method to prepare an odontograma for a child
 * @param {type} odontograma container for the odontograma, teeths
 * @param {type} spaces container for the spaces between teeth
 * @param {type} canvas the canvas where the odontograma will be drawn on
 * @returns {void}
 */
OdontogramaGenerator.prototype.prepareOdontogramaChild = function (odontograma,
  spaces, canvas) {

  this.arrayCount = 0;

  // center odontograma horizontal
  const width = canvas.width;
  const odontWidth = 10 * this.imgWidth;
  const start = (width - odontWidth) / 2;

  // start of first tooth
  let x = start;

  // center odontograma vertical
  const height = canvas.height;
  const odontHeight = 2 * 150;
  const base = (height - odontHeight) / 2;

  for (let i = 55; i > 50; i--) {
    const tooth = new Tooth();
    tooth.setConstants(this.constants);

    if (i > 53) {
      tooth.setSurfaces(5);
    } else {
      tooth.setSurfaces(4);
    }

    const image = new Image();

    image.src = 'images/dentadura-sup-' + i + '.png';

    tooth.id = i;
    tooth.image = image;

    tooth.setDimens(x,
      base,
      this.imgWidth,
      this.imgHeight);

    tooth.setType(0);

    x += tooth.rect.width + this.settings.TOOTH_PADDING;

    odontograma[this.arrayCount] = tooth;

    tooth.address = this.arrayCount;

    this.arrayCount++;

    tooth.createSurfaces(this.settings);

    const space = new Tooth();
    space.setConstants(this.constants);
    space.setSurfaces(5);

    if (i !== 51) {
      const tmpid = (i) + '' + (i - 1);
      space.id = Number(tmpid);
    } else {
      const tmpid = (i) + '' + (61);
      space.id = Number(tmpid);
    }

    space.setDimens(tooth.rect.x + tooth.rect.width / 2,
      tooth.rect.y,
      tooth.rect.width,
      tooth.rect.height);

    space.type = tooth.type;
    space.tooth = false;

    spaces.push(space);
  }

  for (let i = 61; i < 66; i++) {
    const tooth = new Tooth();
    tooth.setConstants(this.constants);

    if (i < 64) {
      tooth.setSurfaces(4);
    } else {
      tooth.setSurfaces(5);
    }

    const image = new Image();

    image.src = 'images/dentadura-sup-' + i + '.png';

    tooth.id = i;
    tooth.image = image;

    tooth.setDimens(x,
      base,
      this.imgWidth,
      this.imgHeight);

    tooth.setType(0);

    x += tooth.rect.width + this.settings.TOOTH_PADDING;

    tooth.address = this.arrayCount;

    odontograma[this.arrayCount] = tooth;

    this.arrayCount++;

    tooth.createSurfaces(this.settings);

    if (i < 65) {
      const space = new Tooth();
      space.setConstants(this.constants);

      space.setSurfaces(5);
      const tmpid = (i) + '' + (i + 1);
      space.id = Number(tmpid);

      space.setDimens(tooth.rect.x + tooth.rect.width / 2,
        tooth.rect.y,
        tooth.rect.width,
        tooth.rect.height);

      space.type = tooth.type;
      space.tooth = false;

      spaces.push(space);
    }
  }

  // start position of first
  x = start;

  for (let i = 85; i > 80; i--) {
    const tooth = new Tooth();
    tooth.setConstants(this.constants);

    if (i < 84) {
      tooth.setSurfaces(4);
    } else {
      tooth.setSurfaces(5);
    }

    const image = new Image();

    image.src = 'images/dentadura-inf-' + i + '.png';

    tooth.id = i;
    tooth.image = image;

    tooth.setDimens(x,
      base + this.seperator,
      this.imgWidth,
      this.imgHeight);

    tooth.setType(1);

    x += tooth.rect.width + this.settings.TOOTH_PADDING;

    odontograma[this.arrayCount] = tooth;

    tooth.address = this.arrayCount;

    this.arrayCount++;

    tooth.createSurfaces(this.settings);

    const space = new Tooth();
    space.setConstants(this.constants);
    space.setSurfaces(5);

    if (i !== 81) {
      const tmpid = (i) + '' + (i - 1);
      space.id = Number(tmpid);
    } else {
      const tmpid = (i) + '' + (71);
      space.id = Number(tmpid);
    }

    space.setDimens(tooth.rect.x + tooth.rect.width / 2,
      tooth.rect.y,
      tooth.rect.width,
      tooth.rect.height);

    space.type = tooth.type;
    space.tooth = false;

    spaces.push(space);
  }

  for (let i = 71; i < 76; i++) {
    const tooth = new Tooth();
    tooth.setConstants(this.constants);

    if (i < 74) {
      tooth.setSurfaces(4);
    } else {
      tooth.setSurfaces(5);
    }

    const image = new Image();

    image.src = 'images/dentadura-inf-' + i + '.png';

    tooth.id = i;
    tooth.image = image;
    tooth.setDimens(x,
      base + this.seperator,
      this.imgWidth,
      this.imgHeight);

    tooth.setType(1);

    odontograma[this.arrayCount] = tooth;
    x += tooth.rect.width + this.settings.TOOTH_PADDING;

    tooth.address = this.arrayCount;
    this.arrayCount++;

    tooth.createSurfaces(this.settings);

    if (i < 75) {
      const space = new Tooth();
      space.setConstants(this.constants);

      space.setSurfaces(5);
      const tmpid = (i) + '' + (i + 1);
      space.id = Number(tmpid);

      space.setDimens(tooth.rect.x + tooth.rect.width / 2,
        tooth.rect.y,
        tooth.rect.width,
        tooth.rect.height);

      space.type = tooth.type;
      space.tooth = false;

      spaces.push(space);
    }
  }
};


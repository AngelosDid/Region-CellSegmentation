var x = 400;    // X-coordinate of the top-left corner
var y = 400;    // Y-coordinate of the top-left corner
var size = 160; // Size of the selection (both width and height)

// Calculate the width and height based on the size
var width = size;
var height = size;

// Get the active image
var imp = IJ.getImage();

// Create a new selection using the specified coordinates and size
imp.setRoi(x, y, width, height);

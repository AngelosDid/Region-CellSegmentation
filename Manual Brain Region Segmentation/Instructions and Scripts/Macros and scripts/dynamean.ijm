title = getTitle();
// to avoid remaining selections from previous processings. If it creates issues, then remove the select none
run("Select None");
run("Color Picker...");
setForegroundColor(255, 255, 255);
// some desktops close the window instead of the color picker even if its the same version. Remove this if it cause problem
run("Close");
floodFill(0, 0);
run("Duplicate...", "title=duplicate.tiff");
setAutoThreshold("Default dark");
//run("Threshold...");
setThreshold(0, 1515, "raw");
run("Create Mask");
run("Create Selection");
run("ROI Manager...");
roiManager("Add");
selectImage(title);
roiManager("Select", 0);
roiManager("Measure");
saveAs("Results", "C:/Users/angdid/Desktop/areaout/" + title + ".csv");
run("Fresh Start");
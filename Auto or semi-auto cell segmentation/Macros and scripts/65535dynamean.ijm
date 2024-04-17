title = getTitle();
// Changing the background surrounding the cropped imageg from black to white
// to avoid remaining selections from previous processing
run("Select None");
run("Color Picker...");
setForegroundColor(255, 255, 255);
// ! In some desktops, even if the version is the same, this closes the window instead of the color picker
run("Close");
floodFill(0, 0);
run("Duplicate...", "title=duplicate.tiff");
setAutoThreshold("Default dark");
// The white background will have by default the maximum value that you used during resize_ribright. 
// In my case it is 1516 for cfos and 2868 for tdtomato (both in BLA). 
// Convert all pixels having the value 1516 (or 2868) to 65535.
changeValues(2868,2868,65535); 
// ! set your own threshold here. Maximum pixel value for 16-bit is 65535. So Threshold should be 65534 
setThreshold(0, 65534, "raw");
run("Create Mask");
run("Create Selection");
run("ROI Manager...");
roiManager("Add");
selectImage(title);
roiManager("Select", 0);
roiManager("Measure");
saveAs("Results", "C:/Users/angdid/Desktop/cut protrusions background measurements/" + title + ".csv");
run("Fresh Start");
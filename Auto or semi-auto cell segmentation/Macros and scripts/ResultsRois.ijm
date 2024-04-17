title = getTitle();
// roititle = title.substring(0, title.length() - 5) this is in case we have double extension, ie 425549.tiff.tiff
// to take out the second .tiff
run("ROI Manager...");
roiManager("Open", "C:/Users/angdid/Desktop/testmeasure/" + title + ".zip");
roiManager("Show All");
roiManager("Measure");
saveAs("Results", "C:/Users/angdid/Desktop/out/" + title + ".csv");
roiManager ("Reset");
run("Fresh Start");


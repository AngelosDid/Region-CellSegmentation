title = getTitle();
//In case you have to change a file.tiff to file, you can use roititle below and replace the title in the path below with roititle + ".zip"
//roititle = title.substring(0, title.length() - 5) 
//run("Brightness/Contrast...");
setMinAndMax(0.00, 0.60);
roiManager("Open", "C:/Users/angdid/Desktop/finalrois/" + title + ".zip");
roiManager("Show All");
RoiManager.setGroup(0);
RoiManager.setPosition(1);
roiManager("Set Color", "yellow");
roiManager("Set Line Width", 2);
run("Flatten");
saveAs("Tiff", "C:/Users/angdid/Desktop/finalRGB/" + title);
roiManager ("Reset");
run("Fresh Start");


// After you run this code, you might not see windows in macros anymore. You have to set it to false in other macro to make sure windows appear again
setBatchMode(true)
title = getTitle();
open("C:/Users/angdid/Desktop/background/" + title + ".csv");
mean = getResult("Mean", 0)
maximum_display = mean * 2.7
setMinAndMax(mean, maximum_display)
savepath = "C:/Users/angdid/Desktop/newminimum/"
saveAs("tiff", savepath + title);
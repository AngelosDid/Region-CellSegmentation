// Script runs well with ImageJ 1.54f
// Uses the min max modified images to manually correct the auto predictions.
// The script first opens the excluded ROIs and saves the names of their labels in an array called old_roiList.
// Then it clears all ROIs from the manager and opens both included (final_ROIs as named in the RemoveRois.py) and excluded ROIs.
// The included ROIs (final_ROIs) are in cyan color. The excluded in yellow. 
// The user first draws ROIs to neurons that are not detected by stardist (neither surrounded by cyan nor by yellow).
// Then deletes ROIs of wrong detections (cyan ROIs that do not surround an object of interest)
// And lastly deletes yellow surrounded objects of interests (meaning that they have been erroneously excluded).
// It saves all names again to another array called roiList.
// Then, it iterates from old_roiList and tries to detect yellow (excluded) ROIs that have not been deleted.
// These are trash ROIs, meaning that they are definitively excluded. They are appended to an array called trash.
// The trash labels are removed from the ROI. 
// Labels from the old_roiList that are not found in the manager after user's input are practically yellow labels
// That have been deleted by the user. Meaning that (s)he wants them back. These are the salvaged labels.
// The salvaged labels are put back to the roi manager.
// Finally, the ROIs will include : 
// 1)new ROIs by the user 
// 2)the included rois (except for any deleted by the user)
// 3) possibly salvaged ROIs from the excluded.
// Important : pay much attention to your filenames. For instance, .tif instead of .tiff. This code works for .tiff (check the line with new_image_title)
// Important : You have to change the paths to your paths and make sure that you have but zipped and unzipped folders with rois in your excluded directory (this is the output of RemoveROIs by default).
// Important : When you want to delete a ROI, make sure you click at the number, otherwise you'll just delete part of the image 
// Important : You have to create a folder
// The code could be more simplified had I known earlier that when a group of ROIs is added to the manager, they are practically the only selected ROIs by default.

// ! Path to the excluded ROIs
// Mind that this path must have both the zipped and unzipped outputs of RemoveRois.
// The zipped is used to load all regions whereas the unzipped to retrieve selectively for salvaging
excluded_path = "C:/Users/angdid/Desktop/filtered/Excluded/"

// ! Path to Final_Rois (the included ones based on RemoveRois.py, not really really final)
included_path = "C:/Users/angdid/Desktop/filtered/Final_ROIs/"

// ! Path to very final Folder which has only your Regions of interest and nothing else (output of this script)
roidir = "C:/Users/angdid/Desktop/verylastrois/"

// To make sure that images will be shown
setBatchMode(false)

// name of the file
title = getTitle();

// open the excluded rois for the first time to create an array with all names
// mind that you should open the more... from ROI manager and select show real ROI names


roiManager("Open", excluded_path + title + ".zip");
RoiManager.useNamesAsLabels("true");
roiManager("Show All with labels");

// Get number of old excluded ROIs ( 'old' meaning : before our intervention)
// That is, before we salvage any excluded ROIs by deleting the yellow-designated cells
len_of_excluded = roiManager("count");

// Create an empty list to store ROIs
old_roiList = newArray();

// Iterate through each ROI and store its information in the list
for (roindex = 0; roindex < len_of_excluded; roindex++) {
    roi_label = RoiManager.getName(roindex);
    old_roiList = Array.concat(old_roiList,roi_label);
	}

// clear the old Rois from the manager. 
// We only needed them to save their names in the old_roiList
roiManager("reset")


// open the filtered-in (included) rois and designate with particular color

roiManager("Open", included_path + title + ".zip");
roiManager("Show All");
RoiManager.setGroup(0);
RoiManager.setPosition(1);
roiManager("Set Color", "purple");
roiManager("Set Line Width", 1);
run("Flatten");

// a new image opens automatically when flattening. It has a "-1" before the tiff
// e.g 425538_20x-03-zchannel1-Bregma146-1.tiff instead of 425538_20x-03-zchannel1-Bregma146.tiff
// we close this one because we dont need it. Mind that we use -5 because we have .tiff 
// it should be -4 for .tif

new_image_title = title.substring(0, title.length() - 5);
new_image_title += "-1.tiff";
close(new_image_title);

// open the excluded rois again 
roiManager("Open", excluded_path + title + ".zip");
roiManager("Show All with labels");

// select all because only the newly  opened ones will be selected by default
run("Select All");

// User is expected to delete ROIs that erroneously designate real cells/nuclei
waitForUser("1) Add False Negatives (draw shape in cells without ROIs) \n" +
"2) Remove False Positives (cyan ROIs that are not real cells) \n" +
"3) Remove erroneuously excluded ROIS (yellow ROIs that ARE real cells) and press OK");

// Count all loaded Rois (both excluded & included). We need this number for the iteration.
overall_n = roiManager("count")

// Create an empty list to store both included and excluded ROIs
roiList = newArray();

print("overall n");
print(overall_n)

// Iterate through each ROI and store its information in the list
for (index = 0; index < overall_n; index++) {
    r_label = RoiManager.getName(index);
    roiList = Array.concat(roiList,r_label);
    print(r_label);
    print("is at index: ");
    print(index);
	}


// Create an empty list to store definitively exluded ROIS. Practically, the yellow designated
// rois that we never deleted (meaning that we aknowledged they are excluded)
// the trash contains the indices of the definitively excluded. You should never re-load the trash for whatever reason. This will affec indexing.
// The trash will be used to delete the definitevely excluded ROIs. 
// The salvaged array will retain the names of the excluded ROIs that we salvaged (by deleting the yellow ROI). This will be later re-loaded.


trash = newArray();
salvaged = newArray();

// Trace the non-salavaged old rois. That is, the ones that were not deleted.
// meaning they are indeed to be trashed. We iterate first through the array with 
// all old rois (both definitevely discarded and salvaged). If any of them is found in the
// Roi manager, then we save the index -as found in the Roi manager- of this label.
// We practically trace the non-salvaged because the salvaged do not exist at the Roi manager at this point.

for (oldroindex = 0; oldroindex < len_of_excluded; oldroindex++) {
    	old_roi_label = old_roiList[oldroindex];
        found_old_roi = false;
	for (finalroisindex = 0; finalroisindex < overall_n; finalroisindex++){
    	if (old_roi_label == roiList[finalroisindex]) {
		trash = Array.concat(trash,finalroisindex);
		found_old_roi = true;
    	}
}
    if (found_old_roi == false) {
        salvaged = Array.concat(salvaged, old_roi_label);
    }


    }


// after we saved definitevely excluded ROIs indices in the trash, we clear these ROIs from the manager
// the roiManager("select", trash);  is practically the selection of all trash indices

print("Printing trash");
Array.print(trash);
roiManager("deselect");
roiManager("select", trash);
roiManager("delete");


// Now we re-load the salvaged ROIs. Mind that we retrieve them from the unzipped folder 
// which should have the file's name, e.g 425538_20x-03-zchannel1-Bregma146.tiff


salvaged_range = salvaged.length

for (salindex=0; salindex < salvaged.length; salindex++) {
     salabel = salvaged[salindex];     
     roiManager("Open", excluded_path + title + "/" + salabel + ".roi");
}


// save rois themselves in a different directory
filename = title + ".zip";
newdirectory = roidir + filename;

run("Select All");
roiManager("Save", newdirectory);
run("Fresh Start");

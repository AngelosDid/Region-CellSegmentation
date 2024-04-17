// Open the active image
selectWindow(getTitle());

shift = 1;
ctrl = 2;
rightButton = 4;
alt = 8;
leftButton = 16;
insideROI = 32;

x2 = -1;
y2 = -1;
z2 = -1;
flags2 = -1;
logOpened = false;
if (getVersion >= "1.37r")
    setOption("DisablePopupMenu", true);

while (!logOpened || isOpen("Log")) {
    if (!logOpened) {
        // Prompt the user to click and specify the center of the ROI
        waitForUser("Click to define the center of the ROI");
        logOpened = true;
    }

    getCursorLoc(x, y, z, flags);
    if (x != x2 || y != y2 || z != z2 || flags != flags2) {
        if (flags & leftButton != 0) {
            // Calculate the rectangle coordinates with the new size (820x820)
            x1 = x - 410; // Half of the width (820 / 2)
            y1 = y - 410; // Half of the height (820 / 2)
            width = 820;
            height = 820;

            // Create the rectangle ROI
            makeRectangle(x1, y1, width, height);
            updateDisplay();
        }
        x2 = x;
        y2 = y;
        z2 = z;
        flags2 = flags;
    }
    wait(10);
}

if (getVersion >= "1.37r")
    setOption("DisablePopupMenu", false);
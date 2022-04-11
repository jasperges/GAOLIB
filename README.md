# GAOLIB

GAOLIB is a GAO SHAN PICTURES Blender add-on developped to manage a library of poses and animations. This tool will help you store and re-use animations and poses in from and to different Blender files. 

## Prerequisite
GAOLIB works with Blender 2.93. It has not fully been tested on Blender 3, but the first tests seem to be working as well. To install it, please visit the Blender Download web page : https://www.blender.org/download/.

## Installation
Download the zip of the add-on and install it in the 'Add-ons' section of the Blender preferences : 

Edit > Preferences > Add-ons > Install... > Select the zip file in your files > Install Add-on.

Then enable the add-on.
This add-on uses PySide2 and imageio as external dependencies. They can be installed directly from the add-on preferences by clicking on the 'Install dependencies' button. 

In case there is any problem with the installed dependencies, an 'Uninstall dependencies' button is also available. To complete the uninstallation, the user is asked for confirmation in the system console for each dependency used. 


## Usage
The GAOLIB Pannel should now be available in Blender 3D View.


![image](https://user-images.githubusercontent.com/103406493/162702699-6e96c988-5fd8-4b09-b8e6-ad86f8cd86e4.png)


Four operators are available : 

- GAOLIB  : Starts the main window of the tool. On the first use, you will be asked to define the location of the root folder of your library. A ROOT directory will be created in the given location.

- Create Pose : Creates a new pose item to be stored in the library. 
To use after the following actions in the main window. 
	'+' button > New Pose > 'Camera' button. The pose is created if the selected object in the scene is an armature and the mode is set to Pose Mode. The pose only contains the selected bones.

- Create Animation : Creates a new animation item to be stored in the library. 
To use after the following actions in the main window. 
	'+' button > New Animation> 'Camera' button.
The animation is created if the selected object in the scene is an armature and the mode is set to Pose Mode. The pose only contains the selected bones.

- Show overlay hidden : After creating a pose/animation, some overlays can be hidden for its preview to be clean. This button sets back the deactivated overlays.


![image](https://user-images.githubusercontent.com/103406493/162702462-737643c8-a262-46e4-9ba4-3dd6838f4a92.png)


## Note
This project is the first version of a work in progress. We are aware that some things can be improved and we are still looking for a way to change them. Amongst them : 

- The user has to define a non empty path in the Blender preferences, File Paths section for Temporary files. If not, he/she won't be able to create new items in the library.

- The user has to choose a ROOT location for his/her library where he/she has all the writing rights.

- In order to remove properly the add-on from Blender, the user has to do it from a Blender session in which the Gaolib main window has not been opened. Otherwise, when trying to remove the add-on it will raise an Error in Windows (WinError 32:  The process cannot access the file because it is being used by another process).

- For now, in order to create an animation/pose item in the library, the user has to go through 4 steps after clicking '+'> New animation. This process would be more user friendly if it were lighter : 
	
	-- One click on the camera button in the Gaolib Window: Remember the current render path, and set the render path to the temp directory to be able to retrieve the files generated by the creation of the item
	
	-- One click on the Create Pose/Animation button in the Gaolib toolbox : Triggers the render and create the temporary files needed for the item creation
	
	-- One click on the camera button in the Gaolib Window : Set back the old render path and gves a preview of the iem thumbnail
	
	-- One click on the Save Pose/Animation button in the Gaolib window : Actually stores the files related to the pose/animation item in the library.

## License
Published under GPLv3 license.

## Author
Anne Beurard

Note :

The dependencies management is adapted from Robert Guetzkow work available here :
[https://github.com/robertguetzkow/blender-python-examples/tree/master/add_ons/install_dependencies](https://github.com/robertguetzkow/blender-python-examples/tree/master/add_ons/install_dependencies "https://github.com/robertguetzkow/blender-python-examples/tree/master/add_ons/install_dependencies")

Prerequest:
Download Anaconda2(Python 2.7) from website

https://www.anaconda.com/download/#linux

Running the installation

Install Prerequest

conda install -c conda-forge opencv pyqt

conda install matplotlib

Runing:

navigate to the download direct run

python 1.py


Usage 

First you need Download the image data from course website. Unzip the file in this folder.Then execute {python 1.py} and input your name initial and student id to open the main window.

in the main windowsLeft side is the image file list. You could choose the label image, after it is label, the color would become red.

Middle is the actual image. There are 21 different joint points on the image. We have preprocess the data that make most of the hand joint align to their right positions. But there is some situation that our model is not able to handle with. For those image, you may need to drag joint points to right positions. If there is occluded hand joint, you may inference the position by yourself.

Right part would tell you the actual coordination of each hand joint. Also there is the option that allow you to make hand joint visible or invisible. This is quite useful when a lot joints are close to each other.

After you finish labeling all the image, submit your {name_initial} _ {studentID}.js file to canvas.
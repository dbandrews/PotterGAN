"""
Script to crop pottery images using the YOLO v4 object detection darknet tool

Run in the darknet/build/x64 folder where darknet.py file is for perform detect function

"""
# import the necessary packages
from darknet import performDetect
import pandas as pd
import cv2
import glob
import os
import time


def yolo_crop(image_path, output_path, pottery_labels,yolo_weight_path, detect_thresh=0.5, min_pixels=256, make_square=False, new_dims=None):
    '''
    Function to perform the detection and cropping of images in a given folder.

    Assumes it is being run from darknet/build/x64 folder with darknet.exe and DLL's there

    Parameters:
    ---------------------
    image_path: str
        Path to the folder where the images to be cropped are

    output_path: str
        Path to where the cropped images should be saved, can be same as image_path
        for quick testing

    pottery_labels: list of str
        The names of the categories that you want to save from YOLO, i.e. ['mug', 'cup']

    detect_thresh: float (default= 0.5)
        The detection threshold for YOLO, mugs worked well with 0.65

    min_pixels: int
        The minimum resolution of the output image in X and Y, default 256, helps stop very small images being saved

    make_square: Bool
        Resize image to make square? If true and new_dims aren't set, resizes to square using smallest dimension of original image. Otherwise makes square with new dimensions.

    new_dims: Tuple
        New dimensions for image if make_square=True
    '''

    # dataframe to store detected object details so this doesn't need to be run again
    image_details = pd.DataFrame(index=[0], columns=['originalFileName',
                                                     'newFileName',
                                                     'label',
                                                     'confidence',
                                                     "imageHeight",
                                                     "imageWidth",
                                                     "xPosition",
                                                     "yPosition",
                                                     "croppedHeight",
                                                     "croppedWidth"])

    #tracking variables
    start_time = time.time()
    images_processed = 0
    for image in glob.iglob(image_path):

        detected = performDetect(imagePath=image,
                                weightPath=yolo_weight_path,
                                showImage=False,
                                thresh=detect_thresh)
        #loads the image to be cropped
        img = cv2.imread(image)
        imgHeight, imgWidth = img.shape[:2]

        #goes over all detected objects and crops then saves the cropped image
        for object in detected:

            label = object[0]
            confidence = object[1]
            bounds = object[2]

            print(f"{label} {confidence}")

            #box dimensions
            width = int(bounds[2])
            height = int(bounds[3])
            xCoord = int(bounds[0] - width/2)
            yCoord = int(bounds[1] - height/2)
            #padding around the detected boundary box set at 10%
            border = int(width*0.1)

            #only process/save images that are large enough, reduces small snippets of objects
            if (label in pottery_labels) and (width > min_pixels) and (height > min_pixels):

                #if object is detected in corner of image, don't apply border
                if (xCoord < border):
                    print("Object in X corner")
                    xCoord = 0
                    border = 0
                if (yCoord < border):
                    print("Object in Y corner")
                    yCoord = 0
                    border = 0

                print(f"X:{xCoord} Y:{yCoord} width:{width} height:{height} border:{border}")

                if make_square:

                    if new_dims == None:
                        new_dimension = (min(height,width),min(height,width))
                    else:
                        new_dimension = new_dims

                    #Crop to box, get the smallest dimension and interpolate to make square with smallest dimension for height and width.
                    crop_img = img[yCoord-border:yCoord + height + border, xCoord - border:xCoord + width + border]
                    crop_img = cv2.resize(crop_img, new_dimension, interpolation = cv2.INTER_AREA)
                else:
                  crop_img = img[yCoord-border:yCoord + height + border, xCoord - border:xCoord + width + border]

                cropHeight, cropWidth = crop_img.shape[:2]

                #cv2.imshow("cropped", crop_img) #Uncomment to show the cropped images
                #cv2.waitKey(0)

                original_file = os.path.basename(image)
                file_name = f"{original_file}_{label}_{confidence:0.2f}.jpg"

                cv2.imwrite(os.path.join(output_path, file_name), crop_img)

                image_details.loc[image_details.index.max() + 1] = [original_file,
                                                         file_name,
                                                         label,
                                                         confidence,
                                                         imgHeight,
                                                         imgWidth,
                                                         xCoord,
                                                         yCoord,
                                                         cropHeight,
                                                         cropWidth]

        #increment how may images were processed
        images_processed = images_processed+1

    processing_time = time.time() - start_time

    #save off the image details to the same folder as the cropped images once all images completed
    print(f"{images_processed:2.0f} Images Processed in {processing_time:3.1f} seconds")
    image_details.to_csv(os.path.join(output_path,"CroppedImageDetails.csv"), index=False)


if __name__ == "__main__":

    #paths to the images to be cropped
    yolo_weight_path = "C:\\Users\\Dustin\\Python_Scripts\\Generative_Deep_Learning\\PotterGAN\\PotterGAN\\scripts\\cfg\\yolov4.weights"
    image_path = "C:\\Users\\Dustin\\Python_Scripts\\Generative_Deep_Learning\\PotterGAN\\PotterGAN\\\\data\\mug\\*.jpg"
    output_path = 'C:\\Users\\Dustin\\Python_Scripts\\Generative_Deep_Learning\\PotterGAN\\PotterGAN\\\\data\\output\\'

    # minimum image resolution to save
    min_pixels = 100

    # Yolo related pottery labels
    pottery_labels = ['mug', 'cup', 'vase', 'bowl']

    # detection thresholdfor YOLO,
    detect_thresh = 0.65

    #run the cropping
    yolo_crop(image_path,
              output_path,
              pottery_labels,
              yolo_weight_path,
              detect_thresh,
              min_pixels,
              make_square=True,
              new_dims=(300,300))
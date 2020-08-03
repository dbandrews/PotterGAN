import os

from keras.preprocessing.image import ImageDataGenerator, load_img, save_img, img_to_array


def load_images(path_to_data, image_size, batch_size):
    data_folder = os.path.join('./data', path_to_data)

    image_gen = ImageDataGenerator(preprocessing_function=lambda x:(x.astype('float32') - 127.5)/ 127.5)

    x_train = image_gen.flow_from_directory(data_folder
    , target_size= (image_size,image_size)
    , batch_size= batch_size
    ,shuffle=True
    , class_mode = 'input'
    ,subset='training')

    return x_train

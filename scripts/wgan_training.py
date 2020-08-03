import os
import matplotlib.pyplot as plt

from models.wgan_model import WGANGP
from loaders.load_dataset import load_images


# run params
SECTION = 'wgangp'
RUN_ID = '0001'
DATA_NAME = 'mug'
RUN_FOLDER = 'run/{}/'.format(SECTION)
RUN_FOLDER += '_'.join([RUN_ID, DATA_NAME])

if not os.path.exists(RUN_FOLDER):
    os.mkdir(RUN_FOLDER)
    os.mkdir(os.path.join(RUN_FOLDER, 'viz'))
    os.mkdir(os.path.join(RUN_FOLDER, 'images'))
    os.mkdir(os.path.join(RUN_FOLDER, 'weights'))

mode =  'build' #'load' #

# Training Constants
batch_size = 24
image_size = 256 #pixels height x width....

# Create flow of images - all considered training
x_train = load_images('mug_vase_bowl', image_size, batch_size)


gan = WGANGP(input_dim = (image_size,image_size,3)
        , critic_conv_filters = [64,128,256,512]
        , critic_conv_kernel_size = [5,5,5,5]
        , critic_conv_strides = [2,2,2,2]
        , critic_batch_norm_momentum = None
        , critic_activation = 'leaky_relu'
        , critic_dropout_rate = None
        , critic_learning_rate = 0.0002
        , generator_initial_dense_layer_size = (16, 16, 512)
        , generator_upsample = [1,1,1,1]
        , generator_conv_filters = [512,256,128,3]
        , generator_conv_kernel_size = [5,5,5,5]
        , generator_conv_strides = [2,2,2,2]
        , generator_batch_norm_momentum = 0.9
        , generator_activation = 'leaky_relu'
        , generator_dropout_rate = None
        , generator_learning_rate = 0.0002
        , optimiser = 'adam'
        , grad_weight = 10
        , z_dim = 100
        , batch_size = batch_size
        )

if mode == 'build':
    gan.save(RUN_FOLDER)

else:
    gan.load_weights(os.path.join(RUN_FOLDER, 'weights/weights.h5'))



gan.critic.summary()

gan.generator.summary()

# Train settings
epochs = 8000
print_n_batches = 100
critic_repeats = 5


gan.train(     
    x_train
    , batch_size = batch_size
    , epochs = epochs
    , run_folder = RUN_FOLDER
    , print_every_n_batches = print_n_batches
    , n_critic = critic_repeats
    , using_generator = True
)






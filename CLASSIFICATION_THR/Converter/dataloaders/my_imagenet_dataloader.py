import tensorflow as tf
import os

def get_imagenet_dataloader(dataset_path_name, batch_size):
    ds_quant = tf.keras.preprocessing.image_dataset_from_directory(
                directory = dataset_path_name,
                labels = 'inferred',
                label_mode = None,
                color_mode = "rgb",
                batch_size = batch_size,
                image_size = (224,224),
                shuffle = False
    )
    ds_quant = ds_quant.unbatch().batch(batch_size, drop_remainder=True) # Force drop remainder
    return ds_quant
